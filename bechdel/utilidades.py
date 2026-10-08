"""Funciones auxiliares compartidas por todo el pipeline (sin clases)."""

from pathlib import Path

from bechdel.excepciones import EsquemaIncorrectoError


def comprobar_columnas(df, *columnas):
    """Comprueba que la tabla tiene todas las columnas indicadas.

    Recibe el DataFrame y tantos nombres de columna como se quiera (*args).
    No devuelve nada; lanza EsquemaIncorrectoError con la lista de las que
    faltan (en el orden en que se pidieron) si alguna no existe.
    """
    faltantes = [columna for columna in columnas if columna not in df.columns]
    if faltantes:
        raise EsquemaIncorrectoError(faltantes)


def porcentaje(parte, total, decimales=1):
    """Calcula parte / total * 100 redondeado a `decimales`.

    Si `total` es 0 devuelve 0.0 en lugar de romperse.
    """
    if total == 0:
        return 0.0
    return round(float(parte) / float(total) * 100, decimales)


def formatear_millones(valor, decimales=1):
    """Convierte 45000000 en el texto '45.0 M$'."""
    return f"{valor / 1_000_000:.{decimales}f} M$"


def anio_a_decada(anio):
    """Convierte un año en su década: 1987 -> 1980 (funciona con números o Series)."""
    return anio // 10 * 10


def asegurar_carpeta(ruta):
    """Crea la carpeta (y sus padres) si no existe y devuelve su Path."""
    ruta = Path(ruta)
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta
