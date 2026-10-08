"""Análisis de la tabla limpia (Estación 3 del pipeline)."""

import numpy as np
import pandas as pd

from bechdel import config
from bechdel.excepciones import DatosInsuficientesError
from bechdel.utilidades import comprobar_columnas, porcentaje

_COLUMNAS_NECESARIAS = (
    "decada",
    "resultado",
    "aprueba",
    "hay_desacuerdo",
    "presupuesto_2013",
    "recaudacion_internacional_2013",
    "roi",
)


class AnalizadorBechdel:
    """Responde, con un método por pregunta, a las preguntas sobre el test de Bechdel.

    Recibe la tabla limpia (contrato 5.2) y nunca la modifica.
    """

    def __init__(self, df):
        """Comprueba que la tabla tiene lo necesario y guarda una copia."""
        comprobar_columnas(df, *_COLUMNAS_NECESARIAS)
        self._datos = df.copy()

    @property
    def datos(self):
        """Devuelve una copia de la tabla limpia del analizador."""
        return self._datos.copy()

    def tasa_aprobado_global(self):
        """Devuelve el % de películas que aprueban (float, ≈ 44.8)."""
        return porcentaje(self._datos["aprueba"].sum(), len(self._datos))

    def tasa_por_decada(self):
        """Devuelve una fila por década con n_peliculas, n_aprueban y pct_aprueba.

        Lanza DatosInsuficientesError si alguna década tiene muy pocas películas.
        """
        grupos = self._datos.groupby("decada")["aprueba"]
        tabla = pd.DataFrame(
            {
                "n_peliculas": grupos.size(),
                "n_aprueban": grupos.sum().astype("int64"),
            }
        )
        pequenas = tabla[tabla["n_peliculas"] < config.MIN_PELICULAS_DECADA]
        if not pequenas.empty:
            decada = int(pequenas.index[0])
            raise DatosInsuficientesError(
                f"década {decada}", int(pequenas.iloc[0]["n_peliculas"]), config.MIN_PELICULAS_DECADA
            )
        tabla["pct_aprueba"] = np.round(tabla["n_aprueban"] / tabla["n_peliculas"] * 100, 1)
        return tabla

    def motivos_suspenso(self):
        """Devuelve (Series) cuántas películas suspenden por cada motivo, en el orden de config."""
        suspensas = self._datos[~self._datos["aprueba"]]
        conteo = suspensas["resultado"].astype(str).value_counts()
        motivos = conteo.reindex(config.ORDEN_MOTIVOS_SUSPENSO, fill_value=0).astype("int64")
        motivos.name = "n_peliculas"
        return motivos

    def composicion_por_decada(self):
        """Devuelve década x resultado en % por fila (cada fila suma 100)."""
        resultado = self._datos["resultado"].astype(str)
        tabla = pd.crosstab(self._datos["decada"], resultado, normalize="index") * 100
        columnas = ["ok", *config.ORDEN_MOTIVOS_SUSPENSO]
        tabla = tabla.reindex(columns=columnas, fill_value=0.0)
        tabla.columns.name = None
        return tabla

    def datos_economicos(self):
        """Devuelve las películas con todos los datos de dinero, solo con 4 columnas."""
        columnas = ["aprueba", "presupuesto_2013", "recaudacion_internacional_2013", "roi"]
        tabla = self._datos[columnas].dropna().copy()
        for columna in ("presupuesto_2013", "recaudacion_internacional_2013"):
            tabla[columna] = tabla[columna].astype("int64")
        tabla["roi"] = tabla["roi"].astype("float64")
        return tabla.reset_index(drop=True)

    def comparar_economia(self):
        """Devuelve medianas de presupuesto, recaudación y ROI para 'Aprueba' y 'Suspende'.

        Columnas: mediana_presupuesto, mediana_recaudacion, mediana_roi, n_peliculas.
        """
        economicos = self.datos_economicos()
        filas = {}
        for etiqueta, aprueba in (("Aprueba", True), ("Suspende", False)):
            grupo = economicos[economicos["aprueba"] == aprueba]
            if grupo.empty:
                raise DatosInsuficientesError(
                    f"comparación económica ({etiqueta})", 0, 1
                )
            filas[etiqueta] = {
                "mediana_presupuesto": float(np.median(grupo["presupuesto_2013"])),
                "mediana_recaudacion": float(np.median(grupo["recaudacion_internacional_2013"])),
                "mediana_roi": float(np.median(grupo["roi"])),
                "n_peliculas": len(grupo),
            }
        return pd.DataFrame.from_dict(filas, orient="index")

    def _con_tramo_presupuesto(self, tramos):
        """Devuelve `datos_economicos()` con una columna `tramo` (texto tipo '13–28 M$').

        Los tramos se cortan por cuantiles, así que todos tienen casi las mismas películas.
        """
        economicos = self.datos_economicos()
        cortes = np.quantile(economicos["presupuesto_2013"], np.linspace(0, 1, tramos + 1))
        millones = [f"{c / 1_000_000:.0f}" for c in cortes]
        etiquetas = [f"< {millones[1]} M$"]
        etiquetas += [f"{millones[i]}–{millones[i + 1]} M$" for i in range(1, tramos - 1)]
        etiquetas += [f"> {millones[-2]} M$"]
        economicos["tramo"] = pd.qcut(economicos["presupuesto_2013"], tramos, labels=etiquetas)
        return economicos

    def aprobado_por_presupuesto(self, tramos=config.N_TRAMOS_PRESUPUESTO):
        """Devuelve, por tramo de presupuesto, n_peliculas, n_aprueban y pct_aprueba."""
        grupos = self._con_tramo_presupuesto(tramos).groupby("tramo", observed=True)["aprueba"]
        tabla = pd.DataFrame({"n_peliculas": grupos.size(), "n_aprueban": grupos.sum().astype("int64")})
        tabla["pct_aprueba"] = np.round(tabla["n_aprueban"] / tabla["n_peliculas"] * 100, 1)
        return tabla

    def rentabilidad_por_presupuesto(self, tramos=config.N_TRAMOS_PRESUPUESTO):
        """Devuelve, por tramo de presupuesto, el ROI mediano de las que aprueban y de las que suspenden.

        Columnas: roi_aprueba, roi_suspende, n_aprueba, n_suspende. Comparar dentro de cada
        tramo evita mezclar películas baratas con superproducciones.
        """
        economicos = self._con_tramo_presupuesto(tramos)
        grupos = economicos.groupby(["tramo", "aprueba"], observed=True)["roi"]
        medianas = grupos.median().unstack()
        conteos = grupos.size().unstack()
        if conteos.isna().any().any():
            raise DatosInsuficientesError("rentabilidad por tramo de presupuesto", 0, 1)
        return pd.DataFrame(
            {
                "roi_aprueba": medianas[True],
                "roi_suspende": medianas[False],
                "n_aprueba": conteos[True].astype("int64"),
                "n_suspende": conteos[False].astype("int64"),
            }
        )

    def presupuesto_por_decada(self):
        """Devuelve, por década, la mediana de presupuesto (en $ de 2013) de las que aprueban y suspenden.

        Columnas: presupuesto_aprueba, presupuesto_suspende.
        """
        medianas = self._datos.groupby(["decada", "aprueba"])["presupuesto_2013"].median().unstack()
        return pd.DataFrame(
            {"presupuesto_aprueba": medianas[True], "presupuesto_suspende": medianas[False]}
        ).astype("float64")

    def desacuerdo_por_categoria(self):
        """Devuelve (Series) el % de películas con desacuerdo en cada resultado."""
        resultado = self._datos["resultado"].astype(str)
        pct = self._datos.groupby(resultado)["hay_desacuerdo"].mean() * 100
        orden = [c for c in ["ok", *config.ORDEN_MOTIVOS_SUSPENSO] if c in pct.index]
        pct = pct.reindex(orden).round(1)
        pct.name = "pct_desacuerdo"
        return pct

    def filtrar(self, **condiciones):
        """Devuelve la tabla limpia filtrada por condiciones nombre=valor (todas a la vez).

        Si el valor es una lista, tupla o conjunto, se acepta cualquiera de ellos.
        Lanza EsquemaIncorrectoError si una columna no existe y
        DatosInsuficientesError si no queda ninguna película.
        """
        comprobar_columnas(self._datos, *condiciones)
        mascara = pd.Series(True, index=self._datos.index)
        for columna, valor in condiciones.items():
            serie = self._datos[columna]
            if isinstance(serie.dtype, pd.CategoricalDtype):
                serie = serie.astype(str)
            if isinstance(valor, (list, tuple, set)):
                mascara &= serie.isin(list(valor))
            else:
                mascara &= serie == valor
        filtrado = self._datos[mascara].copy()
        if filtrado.empty:
            raise DatosInsuficientesError(f"filtro {condiciones}", 0, 1)
        return filtrado


if __name__ == "__main__":
    from bechdel.limpieza import DepuradorPeliculas

    limpio = DepuradorPeliculas().limpiar(pd.read_csv(config.RUTA_DATOS))
    analizador = AnalizadorBechdel(limpio)
    print(analizador.tasa_aprobado_global())
    print(analizador.tasa_por_decada())
    print(analizador.motivos_suspenso())
    print(analizador.composicion_por_decada())
    print(analizador.comparar_economia())
    print(analizador.aprobado_por_presupuesto())
    print(analizador.rentabilidad_por_presupuesto())
    print(analizador.presupuesto_por_decada())
    print(analizador.desacuerdo_por_categoria())
