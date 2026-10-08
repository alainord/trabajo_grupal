"""Gráficos del pipeline (Estación 4: dibujar).

Patrón "plantilla": la clase madre `GraficoBechdel` hace todo lo común
(figura, título, ejes, guardado y cierre) y cada hija solo escribe `_dibujar`.
"""

import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el pipeline solo guarda PNG.

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

from bechdel import config  # noqa: E402
from bechdel.excepciones import DatosInsuficientesError, EsquemaIncorrectoError  # noqa: E402
from bechdel.utilidades import asegurar_carpeta, comprobar_columnas, formatear_millones  # noqa: E402

# Valores de config.py (sección 6 de la guía). Si A aún no los ha definido allí,
# se usan estos por defecto para que el módulo funcione igualmente.
CARPETA_GRAFICOS = getattr(
    config,
    "CARPETA_GRAFICOS",
    Path(__file__).resolve().parent.parent / "resultados" / "graficos",
)
COLOR_APRUEBA = getattr(config, "COLOR_APRUEBA", "#2a9d8f")
COLOR_SUSPENDE = getattr(config, "COLOR_SUSPENDE", "#c0392b")
DPI_GRAFICOS = getattr(config, "DPI_GRAFICOS", 150)
ORDEN_MOTIVOS_SUSPENSO = getattr(
    config, "ORDEN_MOTIVOS_SUSPENSO", ["nowomen", "notalk", "men", "dubious"]
)
ETIQUETAS_RESULTADO = getattr(
    config,
    "ETIQUETAS_RESULTADO",
    {
        "ok": "Aprueba",
        "nowomen": "Menos de 2 mujeres",
        "notalk": "No hablan entre ellas",
        "men": "Solo hablan de hombres",
        "dubious": "Dudoso",
    },
)
COLORES_RESULTADO = getattr(
    config,
    "COLORES_RESULTADO",
    {
        "ok": COLOR_APRUEBA,
        "nowomen": "#7b2d26",
        "notalk": COLOR_SUSPENDE,
        "men": "#e08a5b",
        "dubious": "#b8b8b8",
    },
)

_MIN_PELICULAS_GRUPO = 1


def _etiqueta(resultado):
    """Devuelve el texto en español de un resultado ('notalk' -> 'No hablan entre ellas')."""
    return ETIQUETAS_RESULTADO.get(resultado, str(resultado))


def _formato_dinero(valor, _posicion=None):
    """Formatea un valor del eje (en dólares) como millones, para FuncFormatter."""
    if valor >= 1_000_000:
        decimales = 0
    elif valor >= 100_000:
        decimales = 1
    else:
        decimales = 2
    return formatear_millones(valor, decimales)


class GraficoBechdel:
    """Clase madre de todos los gráficos.

    Hace lo común: crear la figura, poner título y nombres de ejes, guardar el PNG
    y cerrar la figura. Las hijas solo implementan `_dibujar(ax)`.
    """

    def __init__(self, datos, titulo, etiqueta_x, etiqueta_y, nombre_archivo, carpeta=None):
        """Guarda los datos y los textos del gráfico.

        `carpeta` es opcional: si es None se usa CARPETA_GRAFICOS de config.
        """
        self._datos = datos
        self._titulo = titulo
        self._etiqueta_x = etiqueta_x
        self._etiqueta_y = etiqueta_y
        self._nombre_archivo = nombre_archivo
        self._carpeta = Path(carpeta) if carpeta is not None else Path(CARPETA_GRAFICOS)

    @property
    def carpeta(self):
        """Carpeta donde se guarda el PNG (solo lectura)."""
        return self._carpeta

    @property
    def titulo(self):
        """Título del gráfico (solo lectura)."""
        return self._titulo

    @property
    def nombre_archivo(self):
        """Nombre del PNG que se genera (solo lectura)."""
        return self._nombre_archivo

    @property
    def ruta_salida(self):
        """Ruta completa del PNG que se generará (solo lectura)."""
        return self._carpeta / self._nombre_archivo

    def _dibujar(self, ax):
        """Dibuja el contenido del gráfico en `ax`. Cada hija escribe el suyo."""
        raise NotImplementedError("Cada gráfico hijo debe implementar _dibujar(ax).")

    def generar(self):
        """Crea el gráfico, lo guarda como PNG y devuelve la ruta del archivo."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        try:
            self._dibujar(ax)
            ax.set_title(self._titulo, fontsize=13, fontweight="bold")
            ax.set_xlabel(self._etiqueta_x)
            ax.set_ylabel(self._etiqueta_y)
            ax.spines[["top", "right"]].set_visible(False)
            ruta = self.guardar(fig, dpi=DPI_GRAFICOS, bbox_inches="tight")
        finally:
            plt.close(fig)
        return ruta

    def guardar(self, fig, **opciones):
        """Guarda `fig` como PNG en la carpeta del gráfico y devuelve la ruta.

        `**opciones` se pasa tal cual a `fig.savefig` (por ejemplo dpi=150).
        """
        asegurar_carpeta(self._carpeta)
        ruta = self.ruta_salida
        fig.savefig(ruta, **opciones)
        return ruta


class GraficoEvolucionDecadas(GraficoBechdel):
    """Gráfico 1: líneas con el % de películas que aprueban en cada década."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `tasa_por_decada()` (índice = década)."""
        comprobar_columnas(datos, "n_peliculas", "n_aprueban", "pct_aprueba")
        super().__init__(
            datos,
            "Evolución del % de películas que aprueban el test de Bechdel",
            "Década",
            "Películas que aprueban (%)",
            "01_evolucion_decadas.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Línea con puntos, referencia al 50 % y n=… sobre cada punto."""
        decadas = list(self._datos.index)
        pct = self._datos["pct_aprueba"].to_numpy(dtype=float)
        ax.plot(decadas, pct, marker="o", linewidth=2.2, color=COLOR_APRUEBA, label="% que aprueba")
        ax.axhline(50, linestyle="--", color="grey", linewidth=1, label="Referencia: 50 %")
        for decada, valor, n in zip(decadas, pct, self._datos["n_peliculas"]):
            ax.annotate(
                f"{valor:.1f} %\n(n={int(n)})",
                (decada, valor),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=8,
            )
        ax.set_xticks(decadas)
        ax.set_xticklabels([f"{d}s" for d in decadas])
        ax.set_ylim(0, 100)
        ax.set_xlim(decadas[0] - 4, decadas[-1] + 4)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="lower right")


class GraficoMotivosSuspenso(GraficoBechdel):
    """Gráfico 2: barras horizontales con los motivos por los que se suspende."""

    def __init__(self, datos, carpeta=None):
        """Recibe la Series de `motivos_suspenso()` (índice = motivo)."""
        faltantes = [m for m in ORDEN_MOTIVOS_SUSPENSO if m not in datos.index]
        if faltantes:
            raise EsquemaIncorrectoError(faltantes)
        super().__init__(
            datos,
            "¿Por qué suspenden las películas?",
            "Número de películas",
            "Motivo de suspenso",
            "02_motivos_suspenso.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Barras horizontales en el orden de config, con el valor al final."""
        motivos = list(ORDEN_MOTIVOS_SUSPENSO)
        valores = [int(self._datos[m]) for m in motivos]
        barras = ax.barh([_etiqueta(m) for m in motivos], valores, color=COLOR_SUSPENDE)
        ax.bar_label(barras, padding=3)
        ax.invert_yaxis()  # El primer motivo del orden queda arriba.
        ax.margins(x=0.12)
        ax.grid(axis="x", alpha=0.3)


class GraficoComposicionDecadas(GraficoBechdel):
    """Gráfico 3: barras apiladas al 100 % con la composición de cada década."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `composicion_por_decada()` (filas = décadas, columnas = resultados)."""
        comprobar_columnas(datos, "ok", *ORDEN_MOTIVOS_SUSPENSO)
        super().__init__(
            datos,
            "Composición de los resultados del test por década",
            "Década",
            "Películas (%)",
            "03_composicion_decadas.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Una barra por década y un color por resultado; leyenda fuera del gráfico."""
        posiciones = np.arange(len(self._datos))
        base = np.zeros(len(self._datos))
        for resultado in ["ok", *ORDEN_MOTIVOS_SUSPENSO]:
            valores = self._datos[resultado].to_numpy(dtype=float)
            ax.bar(
                posiciones,
                valores,
                bottom=base,
                color=COLORES_RESULTADO.get(resultado),
                label=_etiqueta(resultado),
                width=0.7,
            )
            base = base + valores
        ax.set_xticks(posiciones)
        ax.set_xticklabels([f"{d}s" for d in self._datos.index])
        ax.set_ylim(0, 100)
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="Resultado")


def _roi_por_grupo(datos):
    """Devuelve (roi de las que aprueban, roi de las que suspenden), solo valores > 0."""
    positivos = datos[datos["roi"] > 0]
    aprueban = positivos.loc[positivos["aprueba"].astype(bool), "roi"].to_numpy(dtype=float)
    suspenden = positivos.loc[~positivos["aprueba"].astype(bool), "roi"].to_numpy(dtype=float)
    for nombre, grupo in (("Aprueba", aprueban), ("Suspende", suspenden)):
        if len(grupo) < _MIN_PELICULAS_GRUPO:
            raise DatosInsuficientesError(f"ROI de las que {nombre.lower()}", len(grupo), _MIN_PELICULAS_GRUPO)
    return aprueban, suspenden


class GraficoRentabilidad(GraficoBechdel):
    """Gráfico 4: caja y bigotes del ROI de las que aprueban frente a las que suspenden."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `datos_economicos()`."""
        comprobar_columnas(datos, "aprueba", "roi")
        super().__init__(
            datos,
            "Rentabilidad (ROI) según el resultado del test de Bechdel",
            "Resultado del test",
            "ROI = recaudación internacional / presupuesto (escala logarítmica)",
            "04_rentabilidad_roi.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Dos cajas con escala log en Y y una línea en ROI = 1 (se recupera lo invertido)."""
        aprueban, suspenden = _roi_por_grupo(self._datos)
        cajas = ax.boxplot(
            [aprueban, suspenden],
            tick_labels=[f"Aprueba\n(n={len(aprueban)})", f"Suspende\n(n={len(suspenden)})"],
            patch_artist=True,
            widths=0.5,
            medianprops={"color": "black", "linewidth": 2},
            flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
        )
        for caja, color in zip(cajas["boxes"], (COLOR_APRUEBA, COLOR_SUSPENDE)):
            caja.set_facecolor(color)
            caja.set_alpha(0.75)
        ax.set_yscale("log")
        ax.axhline(1, linestyle="--", color="grey", linewidth=1)
        ax.annotate("ROI = 1: ingresos = presupuesto", (0.5, 1), xycoords=ax.get_yaxis_transform(),
                    textcoords="offset points", xytext=(0, -5), ha="center", va="top", fontsize=8, color="grey")
        ax.grid(axis="y", alpha=0.3)


class GraficoPresupuestoRecaudacion(GraficoBechdel):
    """Gráfico 5: dispersión presupuesto frente a recaudación, con la diagonal y = x."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `datos_economicos()`."""
        comprobar_columnas(datos, "aprueba", "presupuesto_2013", "recaudacion_internacional_2013")
        super().__init__(
            datos,
            "Presupuesto frente a recaudación internacional",
            "Presupuesto (millones de $ de 2013, escala logarítmica)",
            "Recaudación internacional (millones de $ de 2013, escala logarítmica)",
            "05_presupuesto_recaudacion.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Un punto por película (verde/rojo) y la diagonal 'lo que costó = lo que ganó'."""
        datos = self._datos[
            (self._datos["presupuesto_2013"] > 0) & (self._datos["recaudacion_internacional_2013"] > 0)
        ]
        aprueba = datos["aprueba"].astype(bool)
        for mascara, color, etiqueta in ((aprueba, COLOR_APRUEBA, "Aprueba"), (~aprueba, COLOR_SUSPENDE, "Suspende")):
            grupo = datos[mascara]
            ax.scatter(
                grupo["presupuesto_2013"].to_numpy(dtype=float),
                grupo["recaudacion_internacional_2013"].to_numpy(dtype=float),
                s=16,
                alpha=0.55,
                color=color,
                label=f"{etiqueta} (n={len(grupo)})",
            )
        minimo = float(min(datos["presupuesto_2013"].min(), datos["recaudacion_internacional_2013"].min()))
        maximo = float(max(datos["presupuesto_2013"].max(), datos["recaudacion_internacional_2013"].max()))
        ax.plot([minimo, maximo], [minimo, maximo], linestyle="--", color="black", linewidth=1,
                label="Recaudación = presupuesto")
        ax.set_xscale("log")
        ax.set_yscale("log")
        for eje in (ax.xaxis, ax.yaxis):
            eje.set_major_formatter(FuncFormatter(_formato_dinero))
            eje.set_minor_formatter(NullFormatter())
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", title="Por encima de la línea: ganó dinero", fontsize=8, title_fontsize=8)


class GraficoDesacuerdo(GraficoBechdel):
    """Gráfico 6 (opcional): barras verticales con el % de desacuerdo por resultado."""

    def __init__(self, datos, carpeta=None):
        """Recibe la Series de `desacuerdo_por_categoria()` (índice = resultado)."""
        super().__init__(
            datos,
            "Desacuerdo entre los evaluadores según el resultado del test",
            "Resultado del test",
            "Películas con desacuerdo (%)",
            "06_desacuerdo_categoria.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Barras verticales con el porcentaje escrito encima."""
        categorias = list(self._datos.index)
        colores = [COLORES_RESULTADO.get(c) for c in categorias]
        barras = ax.bar([_etiqueta(c) for c in categorias], self._datos.to_numpy(dtype=float), color=colores)
        ax.bar_label(barras, fmt="%.1f %%", padding=3)
        ax.margins(y=0.15)
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(axis="x", labelsize=8)


def crear_graficos(analizador, carpeta=None, incluir_opcional=False):
    """Crea (sin generar) los gráficos del pipeline a partir de un AnalizadorBechdel.

    Devuelve una lista de objetos gráfico; cada uno se genera con `.generar()`.
    Con `incluir_opcional=True` añade también el gráfico de desacuerdo.
    """
    economicos = analizador.datos_economicos()
    graficos = [
        GraficoEvolucionDecadas(analizador.tasa_por_decada(), carpeta),
        GraficoMotivosSuspenso(analizador.motivos_suspenso(), carpeta),
        GraficoComposicionDecadas(analizador.composicion_por_decada(), carpeta),
        GraficoRentabilidad(economicos, carpeta),
        GraficoPresupuestoRecaudacion(economicos, carpeta),
    ]
    if incluir_opcional:
        graficos.append(GraficoDesacuerdo(analizador.desacuerdo_por_categoria(), carpeta))
    return graficos


if __name__ == "__main__":
    # Prueba con datos de mentira (misma forma que el contrato 5.3 de la guía).
    rng = np.random.default_rng(0)
    decadas = pd.Index([1970, 1980, 1990, 2000, 2010], name="decada")
    por_decada = pd.DataFrame(
        {"n_peliculas": [100, 250, 400, 600, 444], "n_aprueban": [26, 72, 176, 294, 200]}, index=decadas
    )
    por_decada["pct_aprueba"] = (por_decada["n_aprueban"] / por_decada["n_peliculas"] * 100).round(1)
    motivos = pd.Series({"nowomen": 141, "notalk": 514, "men": 194, "dubious": 142})
    composicion = pd.DataFrame(
        rng.dirichlet([3, 1, 4, 1.5, 1], size=5) * 100,
        index=decadas,
        columns=["ok", "nowomen", "notalk", "men", "dubious"],
    )
    presupuesto = rng.lognormal(17, 1, 200).astype("int64")
    recaudacion = (presupuesto * rng.lognormal(0.8, 1, 200)).astype("int64")
    economicos = pd.DataFrame(
        {
            "aprueba": rng.random(200) < 0.45,
            "presupuesto_2013": presupuesto,
            "recaudacion_internacional_2013": recaudacion,
            "roi": recaudacion / presupuesto,
        }
    )
    desacuerdo = pd.Series({"ok": 30.0, "nowomen": 20.0, "notalk": 25.0, "men": 15.0, "dubious": 40.0})

    salida = tempfile.mkdtemp(prefix="bechdel_prueba_")
    for grafico in (
        GraficoEvolucionDecadas(por_decada, salida),
        GraficoMotivosSuspenso(motivos, salida),
        GraficoComposicionDecadas(composicion, salida),
        GraficoRentabilidad(economicos, salida),
        GraficoPresupuestoRecaudacion(economicos, salida),
        GraficoDesacuerdo(desacuerdo, salida),
    ):
        print(grafico.generar())
