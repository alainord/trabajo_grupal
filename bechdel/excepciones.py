"""Excepciones propias del pipeline (las "alarmas" del proyecto).

Todas heredan de ErrorPipelineBechdel, de modo que en main.py basta con
`except ErrorPipelineBechdel` para atrapar cualquiera de ellas.
"""


class ErrorPipelineBechdel(Exception):
    """Madre de todas las excepciones del proyecto. No se lanza directamente."""


class FicheroNoValidoError(ErrorPipelineBechdel):
    """El archivo está vacío, no es un .csv o no se puede leer."""

    def __init__(self, ruta, motivo):
        """Guarda la ruta y el motivo y construye el mensaje."""
        self.ruta = ruta
        self.motivo = motivo
        super().__init__(f"El archivo '{ruta}' no es válido: {motivo}.")


class EsquemaIncorrectoError(ErrorPipelineBechdel):
    """A una tabla le faltan columnas obligatorias."""

    def __init__(self, columnas_faltantes):
        """Guarda la lista de columnas que faltan y construye el mensaje."""
        self.columnas_faltantes = list(columnas_faltantes)
        super().__init__(f"Faltan las columnas {self.columnas_faltantes}.")


class ValorFueraDeDominioError(ErrorPipelineBechdel):
    """Una columna contiene valores que no deberían existir."""

    def __init__(self, columna, valores):
        """Guarda la columna y los valores raros y construye el mensaje."""
        self.columna = columna
        self.valores = list(valores)
        super().__init__(
            f"La columna '{columna}' tiene valores no permitidos: {self.valores}."
        )


class DatosInsuficientesError(ErrorPipelineBechdel):
    """Un cálculo se queda con muy pocas películas para ser fiable."""

    def __init__(self, contexto, n_peliculas, minimo):
        """Guarda el contexto, cuántas películas hay y el mínimo exigido."""
        self.contexto = contexto
        self.n_peliculas = n_peliculas
        self.minimo = minimo
        super().__init__(
            f"Datos insuficientes en {contexto}: {n_peliculas} películas "
            f"(mínimo {minimo})."
        )
