"""Punto de entrada del pipeline: carga, limpia, analiza y dibuja.

No hace cálculos: solo llama a las estaciones en orden y gestiona las
alarmas. Se ejecuta con `python main.py` desde la raíz del proyecto.
"""

import time

from bechdel import config
from bechdel.analisis import AnalizadorBechdel
from bechdel.carga import LectorBechdel
from bechdel.excepciones import (
    EsquemaIncorrectoError,
    ErrorPipelineBechdel,
    FicheroNoValidoError,
    ValorFueraDeDominioError,
)
from bechdel.limpieza import DepuradorPeliculas
from bechdel.visualizacion import crear_graficos


def main(ruta=config.RUTA_DATOS):
    """Ejecuta el pipeline completo sobre el CSV de `ruta` (por defecto, el de config)."""
    inicio = time.perf_counter()
    try:
        # 1. Cargar y validar
        crudo = LectorBechdel(ruta).cargar()

        # 2. Limpiar y exportar
        depurador = DepuradorPeliculas()
        limpio = depurador.limpiar(crudo)
        depurador.exportar(limpio, config.RUTA_CSV_LIMPIO)

        # 3. Analizar
        analizador = AnalizadorBechdel(limpio)

        # 4. Dibujar
        graficos = crear_graficos(analizador)
        rutas_graficos = [grafico.generar() for grafico in graficos]
    except (FileNotFoundError, FicheroNoValidoError) as error:
        print(f"No se ha podido cargar el archivo: {error}")
    except (EsquemaIncorrectoError, ValorFueraDeDominioError) as error:
        print(f"Los datos no tienen el formato esperado: {error}")
    except ErrorPipelineBechdel as error:
        print(f"Error en el pipeline: {error}")
    except Exception as error:
        print(f"Error inesperado: {type(error).__name__}: {error}")
    else:
        print(
            f"Pipeline completado: {len(limpio)} películas limpias, "
            f"{len(rutas_graficos)} gráficos generados."
        )
    finally:
        print(f"Fin de la ejecución (tardó {time.perf_counter() - inicio:.2f} segundos).")


if __name__ == "__main__":
    main()
