# Pipeline de análisis del test de Bechdel

Pipeline en Python (pandas, numpy y matplotlib) que carga y valida un CSV con
1.794 películas (1970–2013), lo limpia, calcula si ha mejorado la tasa de
aprobado del test de Bechdel y si está relacionada con el dinero, y guarda
los resultados en gráficos.

## Instalación

Requiere Python 3.10 o superior.

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto, con el entorno activado:

```bash
python main.py
```

Para ver cómo se gestionan los errores (archivo inexistente, columna que
falta y valor inventado):

```bash
python demo_errores.py
```

## Qué se genera

| Archivo | Contenido |
|---|---|
| `resultados/peliculas_limpio.csv` | La tabla limpia |
| `resultados/graficos/*.png` | Los gráficos del análisis |

Las conclusiones, con cada gráfico explicado, están en [RESULTADOS.md](RESULTADOS.md).

## Estructura

```
trabajo_grupal/
├── data/grupo02_cine_test_bechdel.csv   Datos originales
├── bechdel/
│   ├── config.py          Constantes compartidas (rutas, columnas, colores)   Persona A
│   ├── excepciones.py     Excepciones propias                                 Persona A
│   ├── carga.py           Reglas de validación y LectorBechdel                Persona A
│   ├── utilidades.py      Funciones auxiliares                                Persona B
│   ├── limpieza.py        DepuradorPeliculas                                  Persona B
│   ├── analisis.py        AnalizadorBechdel                                   Persona B
│   └── visualizacion.py   GraficoBechdel y sus gráficos hijos                 Persona C
├── resultados/            Salidas del pipeline
├── main.py                Ejecuta el pipeline completo                        Persona A
├── demo_errores.py        Demostración de las excepciones                     Persona A
└── requirements.txt
```

Flujo: `LectorBechdel.cargar()` → `DepuradorPeliculas.limpiar()` →
`AnalizadorBechdel` → `Grafico<...>.generar()`.

## Equipo

- **Persona A (Oier):** configuración, excepciones, carga y validación, `main.py`.
- **Persona B (Alain):** utilidades, limpieza y análisis.
- **Persona C:** gráficos y presentación.
