"""Gráficos del pipeline (Estación 4: dibujar).

Patrón "plantilla": la clase madre `GraficoBechdel` hace todo lo común
(figura, título, ejes, guardado y cierre) y cada hija solo escribe `_dibujar`.
"""

import tempfile
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el pipeline solo guarda PNG.

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from bechdel import config  # noqa: E402
from bechdel.excepciones import EsquemaIncorrectoError  # noqa: E402
from bechdel.utilidades import asegurar_carpeta, comprobar_columnas  # noqa: E402

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

def _etiqueta(resultado):
    """Devuelve el texto en español de un resultado ('notalk' -> 'No hablan entre ellas')."""
    return ETIQUETAS_RESULTADO.get(resultado, str(resultado))


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
            "El aprobado subió hasta los 2000 y se estancó por debajo del 50 %",
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
                xytext=(0, -12),  # Debajo del punto, para no chocar con la línea del 50 %.
                ha="center",
                va="top",
                fontsize=8,
            )
        ax.set_xticks(decadas)
        ax.set_xticklabels([f"{d}s" for d in decadas])
        ax.set_ylim(0, 80)
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
            "La mitad de los suspensos: las mujeres no hablan entre ellas",
            "Número de películas",
            "Motivo de suspenso",
            "02_motivos_suspenso.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Barras horizontales de mayor a menor, con el número y el % de los suspensos al final."""
        motivos = sorted(ORDEN_MOTIVOS_SUSPENSO, key=lambda m: int(self._datos[m]), reverse=True)
        valores = [int(self._datos[m]) for m in motivos]
        total = sum(valores)
        barras = ax.barh([_etiqueta(m) for m in motivos], valores, color=COLOR_SUSPENDE,
                         height=0.65, edgecolor="white", linewidth=2)
        ax.bar_label(barras, labels=[f"{v} ({v / total * 100:.0f} %)" for v in valores], padding=4)
        ax.invert_yaxis()  # El motivo más frecuente queda arriba.
        ax.margins(x=0.18)
        ax.grid(axis="x", alpha=0.3)
        ax.set_axisbelow(True)


class GraficoComposicionDecadas(GraficoBechdel):
    """Gráfico 3: barras apiladas al 100 % con la composición de cada década."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `composicion_por_decada()` (filas = décadas, columnas = resultados)."""
        comprobar_columnas(datos, "ok", *ORDEN_MOTIVOS_SUSPENSO)
        super().__init__(
            datos,
            "Hay más aprobados porque cae «no hablan entre ellas» (50 % → 28 %)",
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
                edgecolor="white",
                linewidth=2,
            )
            if resultado in ("ok", "notalk"):  # Solo se rotulan los dos tramos que cuentan la historia.
                for x, y0, v in zip(posiciones, base, valores):
                    ax.text(x, y0 + v / 2, f"{v:.0f} %", ha="center", va="center", fontsize=9,
                            color="white", fontweight="bold")
            base = base + valores
        ax.set_xticks(posiciones)
        ax.set_xticklabels([f"{d}s" for d in self._datos.index])
        ax.set_ylim(0, 100)
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="Resultado")


class GraficoAprobadoPresupuesto(GraficoBechdel):
    """Gráfico 4: barras con el % que aprueba en cada tramo de presupuesto."""

    def __init__(self, datos, media_global=None, carpeta=None):
        """Recibe la tabla de `aprobado_por_presupuesto()` y, opcional, el % global de aprobado."""
        comprobar_columnas(datos, "n_peliculas", "pct_aprueba")
        super().__init__(
            datos,
            "Cuanto más cara es la película, menos aprueba el test",
            "Presupuesto (en $ de 2013), dividido en 5 tramos con las mismas películas",
            "Películas que aprueban (%)",
            "04_aprobado_por_presupuesto.png",
            carpeta,
        )
        self._media_global = media_global

    def _dibujar(self, ax):
        """Una barra por tramo con el % encima, n bajo cada tramo y la media global de referencia."""
        etiquetas = [f"{tramo}\n(n={int(n)})" for tramo, n in zip(self._datos.index, self._datos["n_peliculas"])]
        barras = ax.bar(etiquetas, self._datos["pct_aprueba"].to_numpy(dtype=float), color=COLOR_APRUEBA,
                        width=0.65, edgecolor="white", linewidth=2)
        ax.bar_label(barras, fmt="%.0f %%", padding=3, fontsize=10, fontweight="bold")
        if self._media_global is not None:
            ax.axhline(self._media_global, linestyle="--", color="grey", linewidth=1)
            ax.annotate(f"Media de todas: {self._media_global:.0f} %", (1, self._media_global),
                        xycoords=ax.get_yaxis_transform(), textcoords="offset points", xytext=(0, 4),
                        ha="right", va="bottom", fontsize=8, color="grey")
        ax.set_ylim(0, 70)
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)


class GraficoRentabilidadPresupuesto(GraficoBechdel):
    """Gráfico 5: barras agrupadas con el ROI mediano de aprueban/suspenden en cada tramo de presupuesto."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `rentabilidad_por_presupuesto()`."""
        comprobar_columnas(datos, "roi_aprueba", "roi_suspende", "n_aprueba", "n_suspende")
        super().__init__(
            datos,
            "Con el mismo presupuesto, aprobar o suspender da casi lo mismo",
            "Presupuesto (en $ de 2013), dividido en 5 tramos con las mismas películas",
            "Dólares recaudados por cada dólar invertido\n(ROI mediano)",
            "05_rentabilidad_por_presupuesto.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Dos barras por tramo (aprueba/suspende) con el ROI escrito como '3.5×'."""
        posiciones = np.arange(len(self._datos))
        ancho = 0.38
        for desplazamiento, columna, color, nombre in (
            (-ancho / 2, "roi_aprueba", COLOR_APRUEBA, "Aprueban"),
            (ancho / 2, "roi_suspende", COLOR_SUSPENDE, "Suspenden"),
        ):
            barras = ax.bar(posiciones + desplazamiento, self._datos[columna].to_numpy(dtype=float), ancho,
                            color=color, edgecolor="white", linewidth=2, label=nombre)
            ax.bar_label(barras, fmt="%.1f×", padding=3, fontsize=9)
        ax.axhline(1, linestyle="--", color="grey", linewidth=1)
        # Hueco a la derecha de la última barra para que la etiqueta de la línea no pise ninguna barra.
        ax.set_xlim(-0.6, len(posiciones) - 0.4 + 0.7)
        ax.annotate("1× =\nrecupera\nlo invertido", (1, 1), xycoords=ax.get_yaxis_transform(),
                    textcoords="offset points", xytext=(0, 4), ha="right", va="bottom", fontsize=8, color="grey")
        ax.set_xticks(posiciones)
        ax.set_xticklabels(list(self._datos.index))
        ax.set_ylim(0, float(self._datos[["roi_aprueba", "roi_suspende"]].to_numpy().max()) * 1.2)
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)
        ax.legend(loc="upper right", frameon=False)


class GraficoPresupuestoDecadas(GraficoBechdel):
    """Gráfico 6: líneas con el presupuesto mediano de las que aprueban y suspenden en cada década."""

    def __init__(self, datos, carpeta=None):
        """Recibe la tabla de `presupuesto_por_decada()` (índice = década)."""
        comprobar_columnas(datos, "presupuesto_aprueba", "presupuesto_suspende")
        super().__init__(
            datos,
            "Desde los 90, las películas que aprueban reciben menos presupuesto",
            "Década",
            "Presupuesto mediano (millones de $ de 2013)",
            "06_presupuesto_por_decada.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Dos líneas, la brecha sombreada y etiquetas directas al final de cada línea."""
        decadas = np.array(self._datos.index, dtype=float)
        aprueba = self._datos["presupuesto_aprueba"].to_numpy(dtype=float) / 1_000_000
        suspende = self._datos["presupuesto_suspende"].to_numpy(dtype=float) / 1_000_000
        ax.fill_between(decadas, aprueba, suspende, where=suspende >= aprueba, color="grey", alpha=0.12,
                        interpolate=True, linewidth=0)
        for valores, color, nombre in ((aprueba, COLOR_APRUEBA, "Aprueban"), (suspende, COLOR_SUSPENDE, "Suspenden")):
            ax.plot(decadas, valores, marker="o", markersize=7, linewidth=2.2, color=color, label=nombre)
            ax.annotate(f"{nombre}: {valores[-1]:.0f} M$", (decadas[-1], valores[-1]), textcoords="offset points",
                        xytext=(8, 0), va="center", fontsize=9, fontweight="bold")
        brecha = suspende[-1] - aprueba[-1]
        ax.annotate(f"Brecha: {brecha:.0f} M$", (decadas[-1], (aprueba[-1] + suspende[-1]) / 2),
                    textcoords="offset points", xytext=(-10, 0), ha="right", va="center", fontsize=8, color="grey")
        ax.set_xticks(decadas)
        ax.set_xticklabels([f"{int(d)}s" for d in decadas])
        ax.set_xlim(decadas[0] - 3, decadas[-1] + 9)
        ax.set_ylim(0, max(aprueba.max(), suspende.max()) * 1.2)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="upper left", frameon=False)


class GraficoDesacuerdo(GraficoBechdel):
    """Gráfico 7: barras verticales con el % de desacuerdo por resultado."""

    def __init__(self, datos, carpeta=None):
        """Recibe la Series de `desacuerdo_por_categoria()` (índice = resultado)."""
        super().__init__(
            datos,
            "Los suspensos generan más dudas entre los evaluadores que los aprobados",
            "Resultado del test",
            "Películas con desacuerdo (%)",
            "07_desacuerdo_categoria.png",
            carpeta,
        )

    def _dibujar(self, ax):
        """Barras verticales con el porcentaje escrito encima."""
        categorias = list(self._datos.index)
        colores = [COLORES_RESULTADO.get(c) for c in categorias]
        etiquetas = [textwrap.fill(_etiqueta(c), 12) for c in categorias]
        barras = ax.bar(etiquetas, self._datos.to_numpy(dtype=float), color=colores,
                        width=0.7, edgecolor="white", linewidth=2)
        ax.bar_label(barras, fmt="%.1f %%", padding=3)
        ax.margins(y=0.15)
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)


def crear_graficos(analizador, carpeta=None):
    """Crea (sin generar) los gráficos del pipeline a partir de un AnalizadorBechdel.

    Devuelve una lista de objetos gráfico; cada uno se genera con `.generar()`.
    """
    return [
        GraficoEvolucionDecadas(analizador.tasa_por_decada(), carpeta),
        GraficoMotivosSuspenso(analizador.motivos_suspenso(), carpeta),
        GraficoComposicionDecadas(analizador.composicion_por_decada(), carpeta),
        GraficoAprobadoPresupuesto(
            analizador.aprobado_por_presupuesto(), analizador.tasa_aprobado_global(), carpeta
        ),
        GraficoRentabilidadPresupuesto(analizador.rentabilidad_por_presupuesto(), carpeta),
        GraficoPresupuestoDecadas(analizador.presupuesto_por_decada(), carpeta),
        GraficoDesacuerdo(analizador.desacuerdo_por_categoria(), carpeta),
    ]


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
    tramos = pd.Index(["< 13 M$", "13–29 M$", "29–50 M$", "50–92 M$", "> 92 M$"], name="tramo")
    por_presupuesto = pd.DataFrame(
        {"n_peliculas": [357, 358, 355, 357, 356], "pct_aprueba": [52.9, 48.9, 50.4, 40.6, 30.9]}, index=tramos
    )
    rentabilidad = pd.DataFrame(
        {
            "roi_aprueba": rng.uniform(2, 4, 5),
            "roi_suspende": rng.uniform(2, 4, 5),
            "n_aprueba": [189, 175, 179, 145, 110],
            "n_suspende": [168, 183, 176, 212, 246],
        },
        index=tramos,
    )
    presupuesto = pd.DataFrame(
        {"presupuesto_aprueba": [22e6, 34e6, 37e6, 31e6, 27e6], "presupuesto_suspende": [21e6, 31e6, 51e6, 46e6, 47e6]},
        index=decadas,
    )
    desacuerdo = pd.Series({"ok": 30.0, "nowomen": 20.0, "notalk": 25.0, "men": 15.0, "dubious": 40.0})

    salida = tempfile.mkdtemp(prefix="bechdel_prueba_")
    for grafico in (
        GraficoEvolucionDecadas(por_decada, salida),
        GraficoMotivosSuspenso(motivos, salida),
        GraficoComposicionDecadas(composicion, salida),
        GraficoAprobadoPresupuesto(por_presupuesto, 44.8, salida),
        GraficoRentabilidadPresupuesto(rentabilidad, salida),
        GraficoPresupuestoDecadas(presupuesto, salida),
        GraficoDesacuerdo(desacuerdo, salida),
    ):
        print(grafico.generar())
