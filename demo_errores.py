"""Demostración de las excepciones propias (para las capturas del PPT).

Lanza el pipeline con tres archivos rotos y muestra el mensaje amable de
cada caso. Las copias rotas se crean en una carpeta temporal que se borra
al terminar, así que el CSV original nunca se toca.

Uso: `python demo_errores.py` desde la raíz del proyecto.
"""

import tempfile
from pathlib import Path

import pandas as pd

from bechdel import config
from main import main


def crear_copia_sin_columna(carpeta, columna="year"):
    """Guarda una copia del CSV sin `columna` y devuelve su ruta."""
    ruta = Path(carpeta) / "sin_columna.csv"
    pd.read_csv(config.RUTA_DATOS).drop(columns=columna).to_csv(ruta, index=False)
    return ruta


def crear_copia_con_valor_inventado(carpeta, columna="binary", valor="MAYBE"):
    """Guarda una copia del CSV con un valor inventado en la primera fila."""
    ruta = Path(carpeta) / "valor_inventado.csv"
    df = pd.read_csv(config.RUTA_DATOS)
    df.loc[0, columna] = valor
    df.to_csv(ruta, index=False)
    return ruta


def demo():
    """Ejecuta los tres casos de error, uno detrás de otro."""
    with tempfile.TemporaryDirectory() as carpeta:
        casos = [
            ("1. Ruta que no existe", Path(carpeta) / "no_existe.csv"),
            ("2. Falta la columna 'year'", crear_copia_sin_columna(carpeta)),
            ("3. 'PASS' cambiado por 'MAYBE'", crear_copia_con_valor_inventado(carpeta)),
        ]
        for titulo, ruta in casos:
            print(f"\n=== {titulo} ===")
            main(ruta)


if __name__ == "__main__":
    demo()
