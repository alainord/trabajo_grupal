"""Limpieza de la tabla cruda de películas (Estación 2 del pipeline)."""

import html
from pathlib import Path

import numpy as np
import pandas as pd

from bechdel import config
from bechdel.utilidades import anio_a_decada, asegurar_carpeta, comprobar_columnas

# Contrato con la Persona C (sección 5.2 de la guía): columnas de la tabla limpia.
COLUMNAS_LIMPIAS = [
    "imdb",
    "titulo",
    "anio",
    "decada",
    "resultado",
    "aprueba",
    "hay_desacuerdo",
    "presupuesto_2013",
    "recaudacion_nacional_2013",
    "recaudacion_internacional_2013",
    "roi",
]

_COLUMNAS_DINERO = [
    "presupuesto_2013",
    "recaudacion_nacional_2013",
    "recaudacion_internacional_2013",
]
_COLUMNAS_RECAUDACION = ["recaudacion_nacional_2013", "recaudacion_internacional_2013"]
_DIGITOS_IMDB = 7


class DepuradorPeliculas:
    """Convierte la tabla cruda del CSV en la tabla limpia del contrato.

    Cada paso de limpieza es un método protegido que apunta en el informe
    qué ha tocado. El informe se lee con la propiedad `informe`.
    """

    def __init__(self):
        """Prepara el informe de limpieza (vacío)."""
        self._informe = {}

    @property
    def informe(self):
        """Devuelve una copia del informe de limpieza (dict paso -> número)."""
        return dict(self._informe)

    def limpiar(self, df):
        """Limpia la tabla cruda y devuelve una tabla nueva (no modifica `df`)."""
        df = df.copy()
        self._informe = {"filas_entrada": len(df)}
        df = self._renombrar_columnas(df)
        df = self._arreglar_titulos(df)
        df = self._arreglar_imdb(df)
        df = self._separar_desacuerdo(df)
        df = self._derivar_resultado_y_aprueba(df)
        df = self._ceros_falsos_a_nan(df)
        df = self._registrar_huecos(df)
        df = self._eliminar_duplicados(df)
        df = self._calcular_decada(df)
        df = self._calcular_roi(df)
        df = self._borrar_columnas_sobrantes(df)
        df = self._convertir_tipos(df)
        self._comprobar_contrato(df)
        self._informe["filas_salida"] = len(df)
        return df

    def exportar(self, df, ruta):
        """Guarda la tabla limpia como CSV en `ruta` y devuelve la ruta."""
        ruta = Path(ruta)
        asegurar_carpeta(ruta.parent)
        df.to_csv(ruta, index=False)
        return ruta

    # ---- pasos de limpieza (en el orden de la guía) ----

    def _renombrar_columnas(self, df):
        """Paso 1: pasa los nombres originales a los del contrato."""
        df = df.rename(columns=config.RENOMBRAR_COLUMNAS)
        self._informe["columnas_renombradas"] = len(config.RENOMBRAR_COLUMNAS)
        return df

    def _arreglar_titulos(self, df):
        """Paso 2: decodifica entidades HTML (&amp; -> &) y quita espacios."""
        original = df["titulo"].astype(str)
        arreglado = original.map(html.unescape).str.strip()
        self._informe["titulos_html_corregidos"] = int((original != arreglado).sum())
        df["titulo"] = arreglado
        return df

    def _arreglar_imdb(self, df):
        """Paso 3: deja los códigos IMDb como 'tt' + 7 dígitos."""

        def normalizar(codigo):
            digitos = str(codigo).strip().lower().removeprefix("tt")
            if len(digitos) > _DIGITOS_IMDB:
                digitos = digitos.lstrip("0")
            return "tt" + digitos.zfill(_DIGITOS_IMDB)

        original = df["imdb"].astype(str)
        arreglado = original.map(normalizar)
        self._informe["imdb_corregidos"] = int((original != arreglado).sum())
        df["imdb"] = arreglado
        return df

    def _separar_desacuerdo(self, df):
        """Paso 4: crea `hay_desacuerdo` (True si `test` contiene 'disagree')."""
        df["hay_desacuerdo"] = df["test"].astype(str).str.contains("disagree")
        self._informe["peliculas_con_desacuerdo"] = int(df["hay_desacuerdo"].sum())
        return df

    def _derivar_resultado_y_aprueba(self, df):
        """Paso 5: `aprueba` sale de `binary` (PASS -> True)."""
        df["aprueba"] = df["binary"] == "PASS"
        self._informe["peliculas_aprueban"] = int(df["aprueba"].sum())
        self._informe["peliculas_suspenden"] = int((~df["aprueba"]).sum())
        return df

    def _ceros_falsos_a_nan(self, df):
        """Paso 6: una recaudación de 0 $ es un dato ausente, no un cero real."""
        ceros = 0
        for columna in _COLUMNAS_RECAUDACION:
            es_cero = df[columna] == 0
            ceros += int(es_cero.sum())
            df[columna] = df[columna].mask(es_cero, np.nan)
        self._informe["ceros_falsos_a_nan"] = ceros
        return df

    def _registrar_huecos(self, df):
        """Paso 7: NO rellena huecos de dinero; solo los cuenta."""
        for columna in _COLUMNAS_DINERO:
            self._informe[f"huecos_{columna}"] = int(df[columna].isna().sum())
        return df

    def _eliminar_duplicados(self, df):
        """Paso 8: quita filas repetidas según `imdb` (nunca según el título)."""
        antes = len(df)
        df = df.drop_duplicates(subset="imdb", keep="first")
        self._informe["duplicados_eliminados"] = antes - len(df)
        return df

    def _calcular_decada(self, df):
        """Paso 9: calcula `decada` a partir de `anio`."""
        df["decada"] = anio_a_decada(df["anio"])
        return df

    def _calcular_roi(self, df):
        """Paso 10: roi = recaudación internacional / presupuesto (vacío si falta)."""
        presupuesto = df["presupuesto_2013"].astype("float64")
        recaudacion = df["recaudacion_internacional_2013"].astype("float64")
        df["roi"] = recaudacion / presupuesto.where(presupuesto > 0)
        self._informe["roi_calculados"] = int(df["roi"].notna().sum())
        return df

    def _borrar_columnas_sobrantes(self, df):
        """Paso 11: se queda solo con las columnas del contrato, en su orden."""
        sobrantes = [c for c in df.columns if c not in COLUMNAS_LIMPIAS]
        self._informe["columnas_borradas"] = len(sobrantes)
        return df[COLUMNAS_LIMPIAS]

    def _convertir_tipos(self, df):
        """Paso 12: tipos finales (enteros con huecos 'Int64', categoría, etc.)."""
        df = df.copy()
        df["anio"] = df["anio"].astype("int64")
        df["decada"] = df["decada"].astype("int64")
        df["resultado"] = df["resultado"].astype("category")
        for columna in _COLUMNAS_DINERO:
            df[columna] = df[columna].round().astype("Int64")
        return df

    def _comprobar_contrato(self, df):
        """Paso 13: verifica que la tabla tiene exactamente las columnas del contrato."""
        comprobar_columnas(df, *COLUMNAS_LIMPIAS)
        if list(df.columns) != COLUMNAS_LIMPIAS:
            raise ValueError(f"Columnas inesperadas tras la limpieza: {list(df.columns)}")


if __name__ == "__main__":
    crudo = pd.read_csv(config.RUTA_DATOS)
    depurador = DepuradorPeliculas()
    limpio = depurador.limpiar(crudo)
    limpio.info()
    for paso, valor in depurador.informe.items():
        print(f"{paso}: {valor}")
    print(f"Filas: {len(limpio)}")
