"""Constantes compartidas por todo el pipeline (el "tablón de anuncios" del proyecto).

Cualquier valor que se use en más de un sitio se define aquí una sola vez.
Las rutas se calculan a partir de la posición de este archivo, así que
funcionan en cualquier ordenador.
"""

from pathlib import Path

# ---- Rutas ----

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ_PROYECTO / "data" / "grupo02_cine_test_bechdel.csv"
CARPETA_RESULTADOS = RAIZ_PROYECTO / "resultados"
CARPETA_GRAFICOS = CARPETA_RESULTADOS / "graficos"
RUTA_CSV_LIMPIO = CARPETA_RESULTADOS / "peliculas_limpio.csv"

# ---- Esquema del CSV original ----

COLUMNAS_OBLIGATORIAS = [
    "year",
    "imdb",
    "title",
    "test",
    "clean_test",
    "binary",
    "budget",
    "domgross",
    "intgross",
    "code",
    "budget_2013$",
    "domgross_2013$",
    "intgross_2013$",
    "period code",
    "decade code",
]

# ---- Valores permitidos (reglas de validación) ----

CATEGORIAS_VALIDAS = {
    "clean_test": ["ok", "notalk", "men", "dubious", "nowomen"],
    "binary": ["PASS", "FAIL"],
}

ANIO_MINIMO = 1970
ANIO_MAXIMO = 2013

# ---- Renombrado de columnas originales -> contrato (sección 5.2) ----
# `test` y `binary` no se renombran: la limpieza las usa y después las borra.

RENOMBRAR_COLUMNAS = {
    "year": "anio",
    "title": "titulo",
    "clean_test": "resultado",
    "budget_2013$": "presupuesto_2013",
    "domgross_2013$": "recaudacion_nacional_2013",
    "intgross_2013$": "recaudacion_internacional_2013",
}

# ---- Análisis ----

ORDEN_MOTIVOS_SUSPENSO = ["nowomen", "notalk", "men", "dubious"]

# Mínimo de películas para que un porcentaje por grupo sea fiable.
MIN_PELICULAS_DECADA = 5

# En cuántos tramos (con el mismo número de películas) se divide el presupuesto.
N_TRAMOS_PRESUPUESTO = 5

# ---- Gráficos ----

COLOR_APRUEBA = "#2a9d8f"
COLOR_SUSPENDE = "#e63946"
DPI_GRAFICOS = 150

# Traducción de los resultados para las etiquetas visibles.
ETIQUETAS_RESULTADO = {
    "ok": "Aprueba",
    "nowomen": "Menos de 2 mujeres",
    "notalk": "No hablan entre ellas",
    "men": "Solo hablan de hombres",
    "dubious": "Dudoso",
}

# Un color por resultado (gráfico de barras apiladas).
COLORES_RESULTADO = {
    "ok": COLOR_APRUEBA,
    "nowomen": "#6d597a",
    "notalk": COLOR_SUSPENDE,
    "men": "#f4a261",
    "dubious": "#adb5bd",
}
