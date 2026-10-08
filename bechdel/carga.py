"""Carga y validación del CSV original (Estación 1 del pipeline).

Aquí no se limpia nada: el lector devuelve la tabla tal cual, después de
pasarla por todas las reglas de validación.
"""

from pathlib import Path

import pandas as pd

from bechdel import config
from bechdel.excepciones import (
    EsquemaIncorrectoError,
    FicheroNoValidoError,
    ValorFueraDeDominioError,
)


# ---- Reglas de validación ----


class ReglaValidacion:
    """Madre de las reglas de validación. Cada hija comprueba una sola cosa."""

    def __init__(self, descripcion):
        """Guarda la descripción de la regla."""
        self.descripcion = descripcion

    def comprobar(self, df):
        """Comprueba la tabla; cada hija debe escribir su propia versión."""
        raise NotImplementedError("Cada regla debe implementar comprobar(df).")

    def __repr__(self):
        """Representación legible de la regla."""
        return f"{type(self).__name__}({self.descripcion!r})"


class ReglaColumnasObligatorias(ReglaValidacion):
    """Comprueba que la tabla tiene todas las columnas obligatorias."""

    def __init__(self, columnas=None):
        """Usa las columnas de config si no se indican otras."""
        super().__init__("Están todas las columnas obligatorias")
        self.columnas = list(columnas or config.COLUMNAS_OBLIGATORIAS)

    def comprobar(self, df):
        """Lanza EsquemaIncorrectoError si falta alguna columna."""
        faltantes = [columna for columna in self.columnas if columna not in df.columns]
        if faltantes:
            raise EsquemaIncorrectoError(faltantes)


class ReglaCategoriasValidas(ReglaValidacion):
    """Comprueba que las columnas categóricas solo tienen valores permitidos."""

    def __init__(self, categorias=None):
        """Recibe {columna: valores permitidos}; por defecto, las de config."""
        super().__init__("Las categorías solo tienen valores permitidos")
        self.categorias = dict(categorias or config.CATEGORIAS_VALIDAS)

    def comprobar(self, df):
        """Lanza ValorFueraDeDominioError con los valores no permitidos."""
        for columna, permitidos in self.categorias.items():
            raros = df.loc[~df[columna].isin(permitidos), columna]
            if not raros.empty:
                raise ValorFueraDeDominioError(columna, sorted(raros.astype(str).unique()))


class ReglaRangoAnios(ReglaValidacion):
    """Comprueba que todos los años están dentro del rango válido."""

    def __init__(self, minimo=config.ANIO_MINIMO, maximo=config.ANIO_MAXIMO):
        """Guarda el rango de años permitido (por defecto, el de config)."""
        super().__init__(f"Los años están entre {minimo} y {maximo}")
        self.minimo = minimo
        self.maximo = maximo

    def comprobar(self, df):
        """Lanza ValorFueraDeDominioError con los años fuera de rango."""
        anios = pd.to_numeric(df["year"], errors="coerce")
        fuera = df.loc[~anios.between(self.minimo, self.maximo), "year"]
        if not fuera.empty:
            raise ValorFueraDeDominioError("year", sorted(fuera.astype(str).unique()))


def reglas_por_defecto():
    """Devuelve las tres reglas de siempre (la de columnas va primero)."""
    return [ReglaColumnasObligatorias(), ReglaCategoriasValidas(), ReglaRangoAnios()]


# ---- Lector ----


class LectorBechdel:
    """Lee el CSV del test de Bechdel y lo valida con una lista de reglas."""

    def __init__(self, ruta, reglas=None):
        """Valida y guarda la ruta; si no se pasan reglas, usa las de siempre."""
        self.ruta = ruta  # pasa por el setter, que la valida
        self._reglas = list(reglas) if reglas is not None else reglas_por_defecto()

    @property
    def ruta(self):
        """Ruta (Path) del CSV que se va a leer."""
        return self.__ruta

    @ruta.setter
    def ruta(self, nueva_ruta):
        """Acepta la ruta solo si el archivo existe y termina en .csv."""
        nueva_ruta = Path(nueva_ruta)
        if not nueva_ruta.exists():
            raise FileNotFoundError(f"No existe el archivo '{nueva_ruta}'.")
        if nueva_ruta.suffix.lower() != ".csv":
            raise FicheroNoValidoError(nueva_ruta, "no es un archivo .csv")
        self.__ruta = nueva_ruta

    @property
    def reglas(self):
        """Copia de la lista de reglas que se aplican al cargar."""
        return list(self._reglas)

    def cargar(self):
        """Lee el CSV, lo pasa por todas las reglas y devuelve la tabla sin tocar."""
        try:
            df = pd.read_csv(self.__ruta)
        except pd.errors.EmptyDataError:
            raise FicheroNoValidoError(self.__ruta, "está vacío") from None
        except (pd.errors.ParserError, UnicodeDecodeError) as error:
            raise FicheroNoValidoError(self.__ruta, f"no se puede leer ({error})") from error
        if df.empty:
            raise FicheroNoValidoError(self.__ruta, "no tiene filas")
        for regla in self._reglas:
            regla.comprobar(df)
        return df


if __name__ == "__main__":
    tabla = LectorBechdel(config.RUTA_DATOS).cargar()
    print(f"Filas cargadas: {len(tabla)}")
