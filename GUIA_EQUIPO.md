# Guía del equipo: Pipeline de análisis del test de Bechdel

> **Para quién es esta guía:** para los tres miembros del grupo, sepáis mucho o poco de programación.
> Si nunca has programado, léela entera y en orden. Si ya tienes experiencia, puedes ir directamente a tu sección.

---

## Índice

1. [La idea en 2 minutos](#1-la-idea-en-2-minutos)
2. [Diccionario para no perderse](#2-diccionario-para-no-perderse)
3. [Antes de empezar: preparar el ordenador (los tres)](#3-antes-de-empezar-preparar-el-ordenador-los-tres)
4. [Cómo trabajar en equipo con git (los tres)](#4-cómo-trabajar-en-equipo-con-git-los-tres)
5. [Los acuerdos del equipo (los contratos)](#5-los-acuerdos-del-equipo-los-contratos)
6. [Normas de estilo](#6-normas-de-estilo)
7. [Guía de la Persona A: base, carga e integración](#7-guía-de-la-persona-a-base-carga-e-integración)
8. [Guía de la Persona B: limpieza y análisis](#8-guía-de-la-persona-b-limpieza-y-análisis)
9. [Guía de la Persona C: gráficos y presentación](#9-guía-de-la-persona-c-gráficos-y-presentación)
10. [Calendario sugerido](#10-calendario-sugerido)
11. [Errores típicos y cómo resolverlos](#11-errores-típicos-y-cómo-resolverlos)
12. [Checklist final antes de entregar](#12-checklist-final-antes-de-entregar)

---

## 1. La idea en 2 minutos

### ¿Qué es el test de Bechdel?

Es una prueba muy sencilla para películas. Una película **aprueba** si cumple estas tres condiciones:

1. Salen **al menos dos mujeres** (con nombre).
2. **Hablan entre ellas**.
3. Hablan de **algo que no sea un hombre**.

Nuestro archivo de datos (`data/grupo02_cine_test_bechdel.csv`) tiene **1.794 películas** de 1970 a 2013. De cada una sabemos si aprueba o no, por qué suspende si suspende, cuánto costó hacerla y cuánto dinero ganó.

### ¿Qué tenemos que construir?

Un **pipeline**. Piensa en una **cadena de montaje de una fábrica**: el material entra por un lado, pasa por varias estaciones y cada estación hace **una sola tarea**.

```
  📄 CSV          🔍 Estación 1      🧹 Estación 2      📊 Estación 3      🎨 Estación 4
 (datos en  ───►  CARGAR Y     ───►  LIMPIAR      ───►  ANALIZAR     ───►  DIBUJAR
  bruto)          VALIDAR            los datos          (calcular)         (gráficos)
                  (Persona A)        (Persona B)        (Persona B)        (Persona C)
```

- **Estación 1, cargar y validar:** abre el archivo y comprueba que es el correcto y que no está roto.
- **Estación 2, limpiar:** corrige los datos sucios (títulos con símbolos raros, huecos vacíos, columnas que sobran…).
- **Estación 3, analizar:** responde a preguntas: ¿qué porcentaje aprueba?, ¿se ha mejorado con los años?, ¿ganan más dinero las que aprueban?
- **Estación 4, dibujar:** convierte las respuestas en gráficos y los guarda en una carpeta.

Al final hay un "encargado de la fábrica", el archivo `main.py`, que pone en marcha las cuatro estaciones en orden y avisa si algo falla.

### ¿Qué hay que entregar?

1. El código (los archivos `.py`).
2. La carpeta `resultados/` con los gráficos y el CSV limpio.
3. Una presentación (PPT) que explique cómo lo hemos hecho y qué hemos descubierto.

### Lo que el profesor va a mirar con lupa

- Que **cada estación haga solo su trabajo**: la que limpia no dibuja y la que dibuja no lee archivos.
- Que aparezcan unas **técnicas obligatorias** (herencia, encapsulación, excepciones…). Las explicamos abajo y ya está decidido dónde va cada una.
- Que el programa **se ejecute de principio a fin sin romperse**.
- Que nuestra solución **no se parezca a la de otros grupos**.

---

## 2. Diccionario para no perderse

No hace falta memorizarlo. Vuelve aquí cada vez que veas una palabra rara.

| Palabra | Qué significa, en sencillo | Ejemplo en nuestro proyecto |
|---|---|---|
| **Python** | El lenguaje en el que escribimos el programa. | Todo el proyecto. |
| **Archivo `.py`** | Un archivo de texto con código Python. | `carga.py`, `limpieza.py`… |
| **Módulo** | Otra forma de llamar a un archivo `.py`. | `limpieza.py` es el módulo de limpieza. |
| **Paquete** | Una carpeta que agrupa módulos. Se reconoce porque tiene dentro un archivo `__init__.py`. | La carpeta `bechdel/`. |
| **Importar** | Usar en un archivo algo que está escrito en otro. | `from bechdel.carga import LectorBechdel` |
| **Variable** | Una caja con nombre donde guardas un valor. | `total_peliculas = 1794` |
| **Función** | Una receta con nombre: recibe ingredientes (parámetros) y devuelve un resultado. | `porcentaje(803, 1794)` → `44.8` |
| **Parámetro** | Cada ingrediente que recibe una función. | En `porcentaje(parte, total)`, los parámetros son `parte` y `total`. |
| **Parámetro por defecto** | Un ingrediente que, si no lo das, tiene un valor ya puesto. | `decimales=1`: si no dices nada, redondea a 1 decimal. |
| **`*args`** | "Puedes pasarme **tantos** valores como quieras". | `comprobar_columnas(df, "anio", "titulo", "roi")` |
| **`**kwargs`** | "Puedes pasarme tantos pares **nombre=valor** como quieras". | `filtrar(decada=2000, aprueba=True)` |
| **Clase** | Un **molde** o plano para fabricar cosas. | `LectorBechdel` es el molde de "un lector de CSV". |
| **Objeto (instancia)** | Una cosa concreta fabricada con el molde. | `lector = LectorBechdel("data/archivo.csv")` |
| **Atributo** | Un dato que guarda el objeto dentro de sí. | La ruta del archivo que va a leer. |
| **Método** | Una función que pertenece a una clase: algo que el objeto **sabe hacer**. | `lector.cargar()` |
| **`__init__`** | El método que se ejecuta **al fabricar** el objeto. Prepara sus atributos. | Guarda la ruta cuando creas el lector. |
| **`self`** | Dentro de una clase, significa "yo mismo, este objeto". | `self.ruta` es la ruta de **este** lector. |
| **Herencia** | Una clase "hija" que **copia todo** lo de una clase "madre" y añade o cambia algunas cosas. | Todos los gráficos heredan de `GraficoBechdel`. |
| **`super()`** | Desde la hija, **llamar a la madre** para que haga su parte. | La hija le pasa a la madre el título del gráfico para que lo prepare. |
| **Encapsulación** | **Proteger** los datos de un objeto para que nadie los cambie por error desde fuera. | La ruta del lector solo se cambia por una "puerta controlada". |
| **`_atributo`** | Un guion bajo significa "esto es interno, no lo toques desde fuera" (es un aviso). | `self._informe` |
| **`__atributo`** | Dos guiones bajos significan "esto es privado" (Python lo esconde más). | `self.__ruta` |
| **`@property`** | La "puerta controlada" para leer un atributo protegido como si fuera normal. | `lector.ruta` funciona aunque por dentro sea `__ruta`. |
| **Setter** | La "puerta controlada" para **cambiar** un atributo **comprobando antes** que el valor es válido. | No deja poner una ruta que no termine en `.csv`. |
| **Excepción** | Una **alarma** que salta cuando algo va mal. Si nadie la "atrapa", el programa se para. | El archivo no existe → salta la alarma. |
| **Excepción propia** | Una alarma que creamos nosotros con un nombre que explica el problema. | `EsquemaIncorrectoError` = "faltan columnas". |
| **`raise`** | **Hacer sonar** la alarma. | `raise EsquemaIncorrectoError(...)` |
| **`try / except`** | "**Intenta** hacer esto; **si** salta tal alarma, haz esto otro". | Intenta cargar; si el archivo no existe, avisa con un mensaje amable. |
| **`else`** (en un try) | Lo que se hace **solo si no saltó ninguna alarma**. | "Pipeline ejecutado correctamente". |
| **`finally`** | Lo que se hace **siempre**, haya alarma o no. | "Fin de la ejecución". |
| **pandas** | La librería para trabajar con tablas, como un Excel dentro de Python. | Leer el CSV, filtrar, agrupar. |
| **DataFrame** | Una **tabla** de pandas: filas y columnas. | Nuestras 1.794 películas. |
| **Series** | **Una sola columna** de un DataFrame. | La columna `titulo`. |
| **NaN** | Un **hueco vacío** en la tabla (dato que falta). | Películas sin dato de recaudación. |
| **numpy** | Una librería para hacer cálculos con muchos números a la vez. | Medianas, logaritmos. |
| **matplotlib** | La librería para hacer gráficos. | Todos los gráficos. |
| **CSV** | Un archivo de tabla en texto, con las columnas separadas por comas. | `grupo02_cine_test_bechdel.csv` |
| **Terminal** | La ventana donde escribes órdenes al ordenador. | Para ejecutar `python main.py`. |
| **Entorno virtual (venv)** | Una "caja" aislada con las librerías del proyecto, para no mezclarlas con otras. | La carpeta `.venv/`. |
| **git** | Un programa que guarda el historial de cambios del código y permite trabajar en equipo. | Cada uno sube sus cambios sin pisar los del resto. |
| **Rama (branch)** | Una copia paralela del proyecto donde trabajas sin molestar a nadie. | `persona-a-carga` |
| **Commit** | Una "foto" guardada de tus cambios, con un mensaje. | "Añade las excepciones propias" |
| **Pull Request (PR)** | Pedir que tus cambios de tu rama se unan a la rama principal. | Los demás lo revisan antes de aceptarlo. |

---

## 3. Antes de empezar: preparar el ordenador (los tres)

Hacedlo **juntos el primer día**. Si alguien se atasca, los otros ayudan.

### Paso 3.1: Instalar Python

1. Abre la terminal:
   - **Mac:** pulsa `Cmd + Espacio`, escribe `Terminal` y pulsa Enter.
   - **Windows:** pulsa la tecla Windows, escribe `PowerShell` y pulsa Enter.
2. Escribe esto y pulsa Enter:
   ```bash
   python3 --version
   ```
   En Windows prueba `python --version` si no funciona.
3. Si aparece algo como `Python 3.12.x`, ya lo tienes. Si da error, descárgalo de [python.org](https://www.python.org/downloads/) e instálalo. **En Windows, marca la casilla "Add Python to PATH"** durante la instalación.
4. ✅ **Acordad los tres la misma versión** (recomendado: 3.12) para evitar sorpresas.

### Paso 3.2: Instalar un editor de código

Recomendado: **Visual Studio Code** ([code.visualstudio.com](https://code.visualstudio.com/)).
Después de instalarlo, instala la extensión **"Python"** de Microsoft desde el menú de extensiones (el icono de los cuatro cuadraditos).

### Paso 3.3: Descargar el proyecto

La Persona A sube el proyecto a GitHub y añade a los otros dos como colaboradores. Cada uno, en la terminal:

```bash
git clone <enlace-del-repositorio>
cd trabajo_grupal
```

> `cd` significa "entrar en esta carpeta".

### Paso 3.4: Crear el entorno virtual e instalar las librerías

Dentro de la carpeta del proyecto:

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

Si todo ha ido bien, al principio de la línea de la terminal verás `(.venv)`.
⚠️ **Cada vez que abras una terminal nueva para trabajar en el proyecto, tienes que volver a "activar"** el entorno (la segunda línea).

### Paso 3.5: Comprobar que todo funciona

```bash
python -c "import pandas, numpy, matplotlib; print('Todo listo')"
```

Si sale `Todo listo`, ya puedes empezar. 🎉

---

## 4. Cómo trabajar en equipo con git (los tres)

### La regla de oro

> **Nadie trabaja directamente en la rama `main`.** Cada uno trabaja en **su rama** y, cuando una parte funciona, la une a `main` con un Pull Request.

### Ramas de cada persona

| Persona | Rama |
|---|---|
| A | `persona-a-carga` |
| B | `persona-b-datos` |
| C | `persona-c-graficos` |

### La rutina de cada día (receta)

```bash
# 1. Ponerte al día con lo que han subido los demás
git checkout main
git pull

# 2. Ir a tu rama y traerte las novedades de main
git checkout persona-b-datos        # (pon tu rama)
git merge main

# 3. ... trabajas en tus archivos ...

# 4. Guardar una "foto" de tus cambios
git add bechdel/limpieza.py          # (los archivos que hayas tocado)
git commit -m "Limpieza: decodifica los títulos HTML"

# 5. Subirlo a GitHub
git push
```

La **primera vez** tienes que crear tu rama:
```bash
git checkout -b persona-b-datos
git push -u origin persona-b-datos
```

### Consejos

- Haz **commits pequeños y a menudo**, con mensajes que expliquen qué has hecho.
- **Toca solo tus archivos.** Si necesitas cambiar un archivo de otra persona (por ejemplo `config.py`), **avísala antes**.
- Cuando una parte funcione, abre un **Pull Request** en GitHub y pide a otra persona que lo revise. Revisar el código de los demás también sirve para entenderlo (¡os pueden preguntar por todo!).

---

## 5. Los acuerdos del equipo (los contratos)

Esta es **la sección más importante de toda la guía**.

Imagina que tres personas construyen un coche: una el motor, otra las ruedas y otra la carrocería. Si no acuerdan **antes** de qué tamaño son los tornillos, al final nada encaja.
En programación, esos "tornillos" son **qué recibe y qué devuelve** cada parte. Si todos respetáis estos acuerdos, podéis trabajar a la vez sin esperaros.

> ⚠️ Esta es una **propuesta**. Revisadla juntos el primer día. Si cambiáis algo, **actualizad esta sección** para que siempre refleje lo acordado.

### 5.1 Qué recibe y qué devuelve cada pieza

```
 CSV ──► LectorBechdel.cargar() ──► DataFrame CRUDO (validado, sin tocar)
                                         │
                                         ▼
          DepuradorPeliculas.limpiar() ──► DataFrame LIMPIO (ver 5.2)
                                         │
                                         ▼
          AnalizadorBechdel.<método>() ──► Tablas pequeñas con resultados (ver 5.3)
                                         │
                                         ▼
          Grafico<...>.generar()  ──► Archivo PNG en resultados/graficos/
```

### 5.2 Cómo es la tabla LIMPIA (contrato entre B y C)

Así tiene que quedar la tabla después de la limpieza. Persona B se compromete a entregarla exactamente así, y Persona C puede contar con ello.

| Columna limpia | Tipo | Ejemplo | De dónde sale (columna original) |
|---|---|---|---|
| `imdb` | texto | `tt1711425` | `imdb`, siempre `tt` + 7 dígitos |
| `titulo` | texto | `21 & Over` | `title`, con los símbolos HTML arreglados |
| `anio` | número entero | `2013` | `year` |
| `decada` | número entero | `2010` | se calcula a partir de `anio` |
| `resultado` | categoría | `notalk` | `clean_test`: `ok`, `notalk`, `men`, `dubious` o `nowomen` |
| `aprueba` | verdadero/falso | `False` | `binary`: PASS → `True`, FAIL → `False` |
| `hay_desacuerdo` | verdadero/falso | `True` | `True` si `test` termina en `-disagree` |
| `presupuesto_2013` | número entero | `13000000` | `budget_2013$` |
| `recaudacion_nacional_2013` | número entero (puede estar vacío) | `25682380` | `domgross_2013$` |
| `recaudacion_internacional_2013` | número entero (puede estar vacío) | `42195766` | `intgross_2013$` |
| `roi` | número decimal (puede estar vacío) | `3.25` | `recaudacion_internacional_2013 / presupuesto_2013` |

**Columnas que desaparecen:** `test` (ya está repartida entre `resultado` y `hay_desacuerdo`), `binary` (ahora es `aprueba`), `code`, `period code`, `decade code` y las columnas de dinero sin ajustar (`budget`, `domgross`, `intgross`).

> 💡 **¿Por qué usamos solo el dinero "_2013"?** Porque 1 millón de dólares de 1975 no vale lo mismo que 1 millón de 2013 (por la inflación). Las columnas `_2013$` ya están ajustadas, así que se pueden comparar entre años.

### 5.3 Qué devuelve cada método del análisis (contrato entre B y C)

| Método de `AnalizadorBechdel` | Qué devuelve | Para qué gráfico |
|---|---|---|
| `tasa_aprobado_global()` | Un número: el % de películas que aprueban (≈ 44,8) | Texto del PPT |
| `tasa_por_decada()` | Tabla: una fila por década, con las columnas `n_peliculas`, `n_aprueban` y `pct_aprueba` | Gráfico 1 (líneas) |
| `motivos_suspenso()` | Una columna (Series): cuántas películas hay por cada motivo de suspenso, sin `ok`, en el orden `nowomen`, `notalk`, `men`, `dubious` | Gráfico 2 (barras horizontales) |
| `composicion_por_decada()` | Tabla: filas = décadas, columnas = los 5 resultados, valores = % (cada fila suma 100) | Gráfico 3 (barras apiladas) |
| `datos_economicos()` | La tabla limpia **sin las filas que no tienen dinero**, solo con las columnas `aprueba`, `presupuesto_2013`, `recaudacion_internacional_2013` y `roi` | Base de los métodos por presupuesto |
| `comparar_economia()` | Tabla: una fila para "Aprueba" y otra para "Suspende", con las medianas de presupuesto, recaudación y ROI y el número de películas | Texto del PPT |
| `aprobado_por_presupuesto()` | Tabla: una fila por tramo de presupuesto (5 tramos con las mismas películas), con `n_peliculas`, `n_aprueban` y `pct_aprueba` | Gráfico 4 (barras) |
| `rentabilidad_por_presupuesto()` | Tabla: una fila por tramo de presupuesto, con `roi_aprueba`, `roi_suspende` (medianas), `n_aprueba` y `n_suspende` | Gráfico 5 (barras agrupadas) |
| `presupuesto_por_decada()` | Tabla: una fila por década, con `presupuesto_aprueba` y `presupuesto_suspende` (medianas, en $ de 2013) | Gráfico 6 (líneas) |
| `desacuerdo_por_categoria()` | Una columna (Series): % de películas con desacuerdo en cada resultado | Gráfico 7 (barras) |
| `filtrar(**condiciones)` | La tabla limpia, filtrada | Uso general |

### 5.4 Las alarmas (excepciones) del proyecto

| Nombre | Cuándo salta | Quién la hace sonar |
|---|---|---|
| `ErrorPipelineBechdel` | Es la "madre" de todas; no se usa directamente | — |
| `FicheroNoValidoError` | El archivo está vacío, no es `.csv` o no se puede leer | Persona A (carga) |
| `EsquemaIncorrectoError` | Faltan columnas en una tabla | Persona A (carga) y Persona B (`comprobar_columnas`) |
| `ValorFueraDeDominioError` | Aparece un valor que no debería existir (una categoría inventada o un año de 1850) | Persona A (reglas de validación) |
| `DatosInsuficientesError` | Un cálculo se queda con muy pocas películas para ser fiable | Persona B (análisis) |

---

## 6. Normas de estilo

Que el código parezca escrito por **una sola persona** da muy buena impresión.

1. **Nombres en español**, en minúsculas y separados por guiones bajos: `tasa_por_decada`, `presupuesto_2013`.
2. **Clases** con mayúscula inicial y sin guiones: `DepuradorPeliculas`, `GraficoBechdel`.
3. **Constantes** (en `config.py`) en MAYÚSCULAS: `RUTA_DATOS`, `COLOR_APRUEBA`.
4. **No uses tildes ni la "ñ" en los nombres** de variables, funciones o archivos: `anio`, no `año`. En los textos que se muestran sí puedes usarlas.
5. Cada clase y cada función lleva un **docstring**: un comentario entre triples comillas justo debajo que explica qué hace, qué recibe y qué devuelve.
6. **Nunca escribas rutas a mano** tipo `"/Users/maria/Desktop/..."`, porque en el ordenador de otra persona no funcionarán. Todas las rutas están en `config.py`.
7. **Nunca modifiques la tabla que recibes**: trabaja sobre una copia (`df = df.copy()`).
8. No dejes `print` de pruebas olvidados en la versión final.

---

## 7. Guía de la Persona A: base, carga e integración

### Tu misión, en una frase

> Eres quien **pone los cimientos** (configuración y alarmas), quien **abre la puerta** (cargar y validar el CSV) y quien **une todas las piezas** al final (`main.py`).

### Tus archivos

| Archivo | Qué es |
|---|---|
| `requirements.txt` | La lista de librerías y sus versiones |
| `.gitignore` | Los archivos que git no debe subir |
| `README.md` | Las instrucciones del proyecto |
| `bechdel/config.py` | Las constantes compartidas |
| `bechdel/excepciones.py` | Las alarmas propias |
| `bechdel/carga.py` | Leer y validar el CSV |
| `main.py` | El encargado que pone en marcha todo |

### Técnicas obligatorias que te tocan

- ✅ **Excepciones propias** (las creas tú).
- ✅ **Herencia con `super()`**, dos veces: en la familia de excepciones y en la familia de reglas de validación.
- ✅ **Encapsulación**: la ruta privada del lector, con `@property` y setter.
- ✅ **`try / except / else / finally`** en `main.py`.

---

### Paso A1: `requirements.txt` ⏱️ 10 min · 🔴 HAZLO EL PRIMER DÍA

**Qué es:** una lista de la compra de librerías. Así, cuando alguien escribe `pip install -r requirements.txt`, se instala exactamente lo mismo en todos los ordenadores.

**Qué hacer:**
1. Instala las tres librerías en tu entorno: `pip install pandas numpy matplotlib`.
2. Mira qué versiones se han instalado: `pip freeze`.
3. Escribe en `requirements.txt` solo esas tres líneas, con su versión exacta (por ejemplo `pandas==2.2.3`).
4. Súbelo enseguida para que B y C puedan instalar lo mismo.

> ⚠️ Ojo: hay una versión nueva, **pandas 3**, que cambia algunas cosas. Decidid juntos cuál usar y que sea la misma para los tres.

### Paso A2: `.gitignore` ⏱️ 5 min · 🔴 PRIMER DÍA

**Qué es:** una lista de cosas que git debe **ignorar** (no subir).

**Qué escribir** (una por línea):
- `__pycache__/`: archivos temporales que crea Python.
- `.venv/`: el entorno virtual; cada uno tiene el suyo.
- `.DS_Store`: archivos basura de Mac.
- `.vscode/` y `.idea/`: la configuración del editor de cada uno.

### Paso A3: `config.py` ⏱️ 30 min · 🔴 PRIMER DÍA (con B y C delante)

**Qué es:** el **tablón de anuncios** del proyecto. Todos los valores que se usan en varios sitios se escriben aquí **una sola vez**. Si mañana cambia algo, se cambia solo aquí.

**Qué poner:**
1. **Rutas**, construidas con `pathlib` (una librería de Python para manejar rutas):
   - `RAIZ_PROYECTO`: la carpeta del proyecto, calculada a partir de la posición de este archivo (`Path(__file__)`). Así funciona en cualquier ordenador.
   - `RUTA_DATOS`: `RAIZ_PROYECTO / "data" / "grupo02_cine_test_bechdel.csv"`.
   - `CARPETA_RESULTADOS` y `CARPETA_GRAFICOS`.
   - `RUTA_CSV_LIMPIO`: `CARPETA_RESULTADOS / "peliculas_limpio.csv"`.
2. **Columnas obligatorias** del CSV original: una lista con los 15 nombres.
3. **Categorías válidas**:
   - para `clean_test`: `ok`, `notalk`, `men`, `dubious`, `nowomen`;
   - para `binary`: `PASS`, `FAIL`.
4. **Rango de años válido**: de 1970 a 2013.
5. **Diccionario para renombrar** las columnas originales a las del contrato (sección 5.2). Por ejemplo, `"year": "anio"`.
6. **Orden de los motivos de suspenso**: `nowomen`, `notalk`, `men`, `dubious`.
7. **Colores y estilo**: `COLOR_APRUEBA`, `COLOR_SUSPENDE` y `DPI_GRAFICOS` (por ejemplo, 150).

**Cómo saber si está bien:** desde la terminal, `python -c "from bechdel import config; print(config.RUTA_DATOS.exists())"` debe imprimir `True`.

### Paso A4: `excepciones.py` ⏱️ 45 min · 🔴 PRIMER O SEGUNDO DÍA

**Qué es:** el sitio donde creamos **nuestras propias alarmas**, con nombres que explican el problema. Es mucho más claro ver `EsquemaIncorrectoError: faltan las columnas ['year']` que un error genérico de Python.

**Qué hacer:**
1. Crea la clase madre `ErrorPipelineBechdel`, que **hereda de `Exception`**. No necesita casi nada dentro.
2. Crea las cuatro hijas de la sección 5.4. **Cada una hereda de `ErrorPipelineBechdel`**, no de `Exception` directamente.
3. A cada hija dale un `__init__` que reciba **los datos útiles del problema**. Por ejemplo:
   - `EsquemaIncorrectoError` recibe la lista de columnas que faltan;
   - `ValorFueraDeDominioError` recibe el nombre de la columna y los valores raros.
4. Dentro de ese `__init__`:
   - guarda esos datos como atributos (`self.columnas_faltantes = ...`);
   - construye un mensaje claro en español;
   - llama a **`super().__init__(mensaje)`**, que significa "madre, guarda tú este mensaje como haces siempre". Esto cuenta como herencia con `super()`.

> 💡 **¿Por qué una madre común?** Porque en `main.py` podremos escribir `except ErrorPipelineBechdel` y atrapar **cualquiera** de nuestras alarmas de una vez.

**Cómo saber si está bien:** en la terminal, `python -c "from bechdel.excepciones import *; raise EsquemaIncorrectoError(['year'])"` debe mostrar tu mensaje.

### Paso A5: `carga.py`, las reglas de validación ⏱️ 1–2 h

**Qué es:** antes de dejar pasar los datos, un "portero" los revisa. Cada **regla** comprueba **una sola cosa**.

**Qué hacer:**
1. Crea la clase madre `ReglaValidacion`:
   - en `__init__` guarda un `nombre` o `descripcion` de la regla;
   - tiene un método `comprobar(df)` que en la madre **no hace nada útil**: solo lanza `NotImplementedError` para avisar de que "las hijas deben escribir su versión".
2. Crea tres hijas. Cada una llama a `super().__init__(...)` con su descripción y escribe **su propia versión** de `comprobar(df)`:

   | Regla | Qué comprueba | Si falla, lanza… |
   |---|---|---|
   | `ReglaColumnasObligatorias` | Que están todas las columnas de `config` | `EsquemaIncorrectoError` |
   | `ReglaCategoriasValidas` | Que `clean_test` y `binary` solo tienen valores permitidos | `ValorFueraDeDominioError` |
   | `ReglaRangoAnios` | Que todos los años están entre 1970 y 2013 | `ValorFueraDeDominioError` |

> 💡 **¿Por qué así?** Si mañana queremos una regla nueva, solo hay que crear otra hija, sin tocar nada más. Además, este diseño es propio y nos diferencia de otros grupos.

### Paso A6: `carga.py`, el lector ⏱️ 1–2 h

**Qué es:** la clase `LectorBechdel`, que abre el CSV y le pasa al portero todas las reglas.

**Qué hacer:**
1. En `__init__(self, ruta, reglas=None)`:
   - `reglas=None` es un **parámetro por defecto**: si no se pasan reglas, usa las tres de siempre;
   - guarda la ruta en un atributo **privado**, `self.__ruta`, pero **pasando por el setter** (punto 2), para que se valide.
2. **Encapsulación** de la ruta:
   - un `@property ruta`: la "puerta" para **leer** la ruta desde fuera (`lector.ruta`);
   - un `@ruta.setter`: la "puerta" para **cambiarla**. Antes de aceptar la ruta comprueba:
     - que el archivo existe; si no, lanza `FileNotFoundError` (una alarma que ya trae Python);
     - que termina en `.csv`; si no, lanza `FicheroNoValidoError`.
3. Un método `cargar()` que:
   1. lee el CSV con pandas (`pd.read_csv`);
   2. si la tabla está **vacía**, lanza `FicheroNoValidoError`;
   3. pasa **una a una todas las reglas** por la tabla;
   4. **devuelve** la tabla tal cual: aquí no se limpia nada, eso es cosa de B.

**Cómo saber si está bien:** al final del archivo, añade un bloque `if __name__ == "__main__":`. Es un truco que hace que ese código **solo se ejecute cuando lanzas este archivo directamente** (`python -m bechdel.carga`), y no cuando otro archivo lo importa. Dentro, carga el CSV e imprime cuántas filas tiene: deben salir **1794**.

### Paso A7: `main.py` ⏱️ 1–2 h · cuando B y C tengan algo funcionando

**Qué es:** el **encargado de la fábrica**. No hace cálculos: solo **llama a las estaciones en orden** y gestiona las alarmas.

**Qué hacer:** dentro de una función `main()`, escribe esta estructura (explicada en lenguaje normal):

```
INTENTA (try):
    1. Crear el lector y cargar los datos.
    2. Crear el depurador, limpiar y exportar el CSV limpio.
    3. Crear el analizador.
    4. Crear cada gráfico pasándole lo que devuelve el analizador, y generarlo.
SI SALTA FileNotFoundError o FicheroNoValidoError (except):
    → "No se ha podido cargar el archivo: <mensaje>"
SI SALTA EsquemaIncorrectoError o ValorFueraDeDominioError:
    → "Los datos no tienen el formato esperado: <mensaje>"
SI SALTA cualquier otra de nuestras alarmas (ErrorPipelineBechdel):
    → "Error en el pipeline: <mensaje>"
SI SALTA CUALQUIER OTRA COSA (Exception):     ← red de seguridad, va SIEMPRE la última
    → "Error inesperado: <mensaje>"
SI NO SALTÓ NADA (else):
    → "Pipeline completado: X películas limpias, Y gráficos generados."
SIEMPRE (finally):
    → "Fin de la ejecución (tardó Z segundos)."
```

Al final del archivo, el bloque `if __name__ == "__main__": main()`.

> ⚠️ **El orden de los `except` importa:** Python mira de arriba abajo y se queda con el primero que encaja. Los concretos van arriba y el general (`Exception`) siempre el último.

### Paso A8: la demo de errores ⏱️ 30 min

El enunciado dice que las excepciones deben **usarse**, no solo existir. Preparad una prueba para enseñarlo en el PPT:

1. **Ruta que no existe:** cambia temporalmente la ruta por una inventada → debe salir tu mensaje amable, no un error rojo enorme.
2. **Columna que falta:** haz una copia del CSV, borra la columna `year` y apunta a esa copia → debe saltar `EsquemaIncorrectoError`.
3. **Valor inventado:** en otra copia, cambia un `PASS` por `MAYBE` → debe saltar `ValorFueraDeDominioError`.

Haz **capturas de pantalla** de las tres para el PPT y **deshaz los cambios** después.

### Paso A9: `README.md` ⏱️ 30 min · al final

Explica:
1. Qué hace el proyecto (2–3 líneas).
2. Cómo instalarlo (los pasos de la sección 3.4).
3. Cómo ejecutarlo: `python main.py`.
4. Qué se genera y dónde.
5. Estructura de carpetas y quién hizo cada parte.

### ✅ Checklist de la Persona A

- [ ] `requirements.txt` con versiones exactas, subido el primer día
- [ ] `.gitignore`
- [ ] `config.py` con rutas que funcionan en cualquier ordenador
- [ ] 5 excepciones con madre común, todas usando `super().__init__`
- [ ] 3 reglas de validación que heredan de `ReglaValidacion` y llaman a `super()`
- [ ] `LectorBechdel` con `__ruta` privada, `@property` y setter que valida
- [ ] `cargar()` devuelve 1.794 filas
- [ ] `main.py` con `try / except / else / finally` en el orden correcto
- [ ] Demo de los tres errores, con capturas
- [ ] `README.md`

---

## 8. Guía de la Persona B: limpieza y análisis

### Tu misión, en una frase

> Eres el **corazón de los datos**: conviertes la tabla sucia en una tabla limpia y fiable y, después, le **haces preguntas** para sacar conclusiones.

### Tus archivos

| Archivo | Qué es |
|---|---|
| `bechdel/utilidades.py` | Funciones pequeñas que usa todo el equipo |
| `bechdel/limpieza.py` | La clase que limpia |
| `bechdel/analisis.py` | La clase que analiza |

### Técnicas obligatorias que te tocan

- ✅ **Funciones auxiliares fuera de las clases** (`utilidades.py`).
- ✅ **`*args`** en `comprobar_columnas`.
- ✅ **`**kwargs`** en `filtrar`.
- ✅ **Parámetros por defecto** en varias funciones.
- ✅ **Encapsulación**: `_informe` con `@property` y `_datos` con `@property`.
- ✅ Usar **numpy** (lo dice el título del trabajo).

### 🔴 Tu primera tarea, antes de nada

**Confirma con C la tabla de la sección 5.2.** C va a dibujar contando con esos nombres de columna exactos. Si cambias uno, **avisa**.

---

### Paso B1: `utilidades.py` ⏱️ 1 h · 🔴 PRIMEROS DÍAS (los demás la necesitan)

**Qué es:** una **caja de herramientas** con funciones pequeñas, **sin clases**, que cualquiera puede usar.

**Funciones que debes crear:**

| Función | Qué hace | Técnica que demuestra |
|---|---|---|
| `comprobar_columnas(df, *columnas)` | Comprueba que la tabla tiene todas las columnas que le pases. Si falta alguna, lanza `EsquemaIncorrectoError` con la lista de las que faltan | **`*args`**: puedes pasarle 1, 2 o 10 columnas |
| `porcentaje(parte, total, decimales=1)` | Calcula `parte / total * 100` redondeado. Si `total` es 0, devuelve 0 en vez de romperse | **Parámetro por defecto** |
| `formatear_millones(valor, decimales=1)` | Convierte `45000000` en el texto `"45.0 M$"` | **Parámetro por defecto** |
| `anio_a_decada(anio)` | Convierte `1987` en `1980` (división entera: `anio // 10 * 10`) | Función reutilizable |
| `asegurar_carpeta(ruta)` | Crea una carpeta si no existe | Función reutilizable |

> 💡 `asegurar_carpeta` y `formatear_millones` las usará C en los gráficos, y `comprobar_columnas` la usaréis todos. Por eso esta tarea va primero.

### Paso B2: `limpieza.py`, la estructura ⏱️ 30 min

**Qué es:** la clase `DepuradorPeliculas`, una "lavadora" de datos.

**Estructura:**
1. `__init__(self)`: crea `self._informe`, un **diccionario vacío** donde irás apuntando lo que haces (por ejemplo, `{"titulos_html_corregidos": 98, ...}`).
2. `@property informe`: devuelve **una copia** del informe. Así se puede leer desde fuera pero no estropear (esto es la **encapsulación**).
3. `limpiar(df)`: el método principal. Hace una **copia** de la tabla, llama **en orden** a los pasos de limpieza y devuelve la tabla limpia.
4. Un **método pequeño y protegido** (que empieza por `_`) **para cada paso**. Así cada paso se entiende solo y es fácil de probar.
5. `exportar(df, ruta)`: guarda la tabla limpia como CSV.

### Paso B3: `limpieza.py`, los pasos ⏱️ 3–4 h

Hazlos **en este orden**. En cada paso, **apunta en `_informe`** qué ha pasado: cuántas filas o celdas se han tocado. ¡Esos números irán al PPT!

| # | Paso | Qué hacer | Datos reales que vas a encontrar |
|---|---|---|---|
| 1 | **Renombrar columnas** | Usa el diccionario de `config.py` para pasar a los nombres en español | `budget_2013$` y `period code` tienen `$` y espacios: son incómodas |
| 2 | **Arreglar títulos** | Aplica `html.unescape` (de la librería estándar de Python) y quita los espacios sobrantes del principio y el final (`strip`) | **98 títulos** tienen códigos raros: `&amp;` es `&`, `&#39;` es `'` y `&uuml;` es `ü` |
| 3 | **Arreglar códigos IMDb** | Deben ser `tt` + **7 dígitos**. Quita `tt`, rellena con ceros a la izquierda o quita los que sobren, y vuelve a poner `tt` | 2 casos: `tt420238` (le falta un dígito) y `tt00293564` (le sobra un cero) |
| 4 | **Separar el desacuerdo** | Crea `hay_desacuerdo` = `True` si la columna `test` contiene `"disagree"` | **425 películas** (23,7 %) |
| 5 | **Resultado y aprueba** | `resultado` sale de `clean_test`. `aprueba` = `True` si `binary == "PASS"` | 803 aprueban y 991 suspenden |
| 6 | **Ceros falsos** | Una recaudación de 0 $ no tiene sentido: conviértela en hueco vacío (NaN) | *I Come with the Rain* tiene recaudación nacional = 0 |
| 7 | **Huecos vacíos (NaN)** | **No los rellenes con números inventados.** Déjalos vacíos. Las películas siguen sirviendo para el análisis del test; solo se quitan en los cálculos de dinero | 17–18 películas sin recaudación nacional y 11 sin internacional |
| 8 | **Duplicados** | Elimina filas repetidas **según `imdb`**, nunca según el título | Hoy hay 0 duplicados, pero el código debe estar preparado. ⚠️ **Trampa:** hay **26 títulos repetidos** que son **remakes** (*Carrie* 2002 y 2013, *Dawn of the Dead* 1978 y 2004…). ¡Son películas distintas! |
| 9 | **Calcular la década** | Usa `anio_a_decada` de utilidades | Las columnas originales `period code` y `decade code` están vacías antes de 1990, así que no sirven |
| 10 | **Calcular el ROI** | `roi = recaudacion_internacional_2013 / presupuesto_2013`. Si falta la recaudación, el ROI queda vacío | Ojo: *El Mariachi* costó 7.000 $, así que su ROI es enorme |
| 11 | **Borrar columnas sobrantes** | Las de la sección 5.2: `test`, `binary`, `code`, los códigos de periodo y el dinero sin ajustar | `code` es solo año + PASS/FAIL pegados |
| 12 | **Tipos** | `resultado` como categoría; el dinero como entero que admite vacíos (`"Int64"`, con mayúscula) | |
| 13 | **Comprobación final** | Usa `comprobar_columnas` para verificar que la tabla tiene exactamente las columnas del contrato | |

> 💡 **¿Por qué no rellenamos los huecos de dinero con la media?** Porque nos estaríamos **inventando** cuánto ganó una película. Es más honesto dejarlos vacíos y explicarlo en el PPT. Son solo 11–18 películas de 1.794.

**Cómo saber si está bien:** en el bloque `if __name__ == "__main__":`, carga con el lector de A (o directamente con `pd.read_csv` si A aún no ha terminado), limpia, y luego:
- imprime `df.info()`: deben salir las columnas del contrato con sus tipos;
- imprime el `informe`;
- comprueba que siguen saliendo **1.794 filas**.

### Paso B4: `analisis.py` ⏱️ 3–4 h

**Qué es:** la clase `AnalizadorBechdel`. Recibe la tabla limpia y tiene **un método por cada pregunta**.

**Estructura:**
1. `__init__(self, df)`: comprueba con `comprobar_columnas` que la tabla tiene lo necesario y la guarda en `self._datos`.
2. `@property datos`: devuelve **una copia** (encapsulación: nadie puede estropear los datos del analizador).
3. Los métodos de la tabla de la sección 5.3. Explicados en sencillo:

| Método | Qué pregunta responde | Cómo se calcula, en palabras |
|---|---|---|
| `tasa_aprobado_global()` | ¿Qué % aprueba? | Cuenta cuántas tienen `aprueba = True` y usa `porcentaje()` |
| `tasa_por_decada()` | ¿Ha mejorado con el tiempo? | **Agrupa por década** (`groupby`) y, en cada grupo, cuenta el total y cuántas aprueban |
| `motivos_suspenso()` | ¿Por qué suspenden? | Quédate solo con las que suspenden, **cuenta cada resultado** y ordénalo según `config` |
| `composicion_por_decada()` | ¿Cómo cambian los motivos con los años? | Tabla cruzada década × resultado, en % por fila (`pd.crosstab` con `normalize="index"`) |
| `datos_economicos()` | — | Devuelve las películas que tienen todos los datos de dinero (quita los huecos) |
| `comparar_economia()` | ¿Ganan más o menos dinero las que aprueban? | Agrupa por `aprueba` y calcula **medianas** con numpy (`np.median`) |
| `desacuerdo_por_categoria()` | ¿Dónde discrepa más la gente? | Agrupa por `resultado` y calcula el % de `hay_desacuerdo` |
| `filtrar(**condiciones)` | Filtro genérico | Recorre cada pareja nombre=valor y se queda con las filas que cumplen todas. Antes, comprueba que las columnas existen (`comprobar_columnas`) |

4. **Alarma de pocos datos:** si alguna década tiene menos de, por ejemplo, 5 películas, o si un filtro deja la tabla vacía, lanza `DatosInsuficientesError`. Guardad ese mínimo en `config.py`.

> 💡 **¿Por qué la mediana y no la media?** La media se deja engañar por casos extremos. Una película que costó 7.000 $ y ganó 2 millones dispara la media del ROI. La **mediana** (el valor del medio) es mucho más justa aquí.

> 💡 **¿Por qué agrupar por década y no por año?** Porque en 1970 solo hay **1 película** y en 2010 hay 129. Un porcentaje calculado con una sola película no significa nada.

**Resultados que deberías obtener** (para comprobar que lo has hecho bien):

| Pregunta | Resultado aproximado |
|---|---|
| % que aprueba en total | 44,8 % |
| % que aprueba por década | 70s: 26 % · 80s: 29 % · 90s: 44 % · 2000s: 49 % · 2010s: 45 % |
| Motivos de suspenso | notalk 514 · men 194 · dubious 142 · nowomen 141 |
| Mediana del presupuesto (2013 $) | Aprueban: 31,7 M · Suspenden: 44,9 M |
| Mediana del ROI | Aprueban: 2,70 · Suspenden: 2,60 |

### Paso B5: exportar y ayudar con el PPT ⏱️ 1 h

1. Verifica que el CSV limpio se guarda en `resultados/peliculas_limpio.csv` y que se abre bien (puedes abrirlo con Excel).
2. Opcional: guarda también `resumen_por_decada.csv` con la tabla de `tasa_por_decada()`.
3. Pásale a C:
   - el **informe de limpieza** (los números de cada paso) para la diapositiva de limpieza;
   - la **tabla de resultados** de arriba para las conclusiones.

### ✅ Checklist de la Persona B

- [ ] Confirmado con C el contrato de la tabla limpia (5.2)
- [ ] `utilidades.py` con `comprobar_columnas(df, *columnas)` y funciones con parámetros por defecto
- [ ] `DepuradorPeliculas` con `_informe` y `@property informe`
- [ ] Los 13 pasos de limpieza, cada uno en su método
- [ ] Remakes **no** eliminados (deduplicar por `imdb`)
- [ ] Huecos de dinero **no** inventados
- [ ] CSV limpio exportado en `resultados/`
- [ ] `AnalizadorBechdel` con `_datos` y `@property`
- [ ] `filtrar(**condiciones)` funcionando
- [ ] numpy usado en los cálculos (medianas, etc.)
- [ ] `DatosInsuficientesError` lanzado cuando corresponde
- [ ] Los resultados coinciden con la tabla de referencia

---

## 9. Guía de la Persona C: gráficos y presentación

### Tu misión, en una frase

> Eres quien **convierte los números en imágenes** que se entienden de un vistazo, y quien **cuenta la historia** del proyecto en la presentación.

### Tus archivos

| Archivo | Qué es |
|---|---|
| `bechdel/visualizacion.py` | Las clases de gráficos |
| `resultados/graficos/` | Donde se guardan los PNG |
| La presentación (PPT) | La coordinas tú; cada persona aporta su parte |

### Técnicas obligatorias que te tocan

- ✅ **Herencia con `super()`**: la más importante y más visible del trabajo.
- ✅ **`**kwargs`** en el método `guardar`.
- ✅ **Encapsulación**: la carpeta de salida protegida, con `@property`.
- ✅ **Mínimo 3 gráficos distintos**, con título y ejes, guardados en `resultados/` (haremos 5).

### 🔴 Cómo empezar sin esperar a B

B tardará unos días en tener la limpieza y el análisis. **No esperes.** Mira la sección 5.3: ahí pone qué te va a dar B. Crea **a mano** tablas pequeñas de mentira con esa misma forma (por ejemplo, una tabla con 3 décadas inventadas) y dibuja con ellas. Cuando B termine, solo tendrás que cambiar los datos de mentira por los de verdad.

---

### Paso C1: entender la idea de la herencia en los gráficos ⏱️ 30 min de lectura

Todos los gráficos tienen cosas **en común**:
- hay que crear una figura en blanco;
- hay que ponerle **título** y **nombres a los ejes** (lo exige el enunciado);
- hay que **guardarla** como PNG en `resultados/graficos/`;
- hay que **cerrarla** para no gastar memoria.

Y solo hay **una cosa distinta** en cada uno: **lo que se dibuja** (líneas, barras, puntos…).

Por eso:
- **La clase madre `GraficoBechdel`** hace todo lo común, **una sola vez**.
- **Cada clase hija** solo escribe **lo que dibuja**.

Es como una **plantilla de diapositiva**: el título, el logo y el pie de página ya vienen puestos, y tú solo rellenas el contenido. Esto se llama patrón **"plantilla"** (*template method*). Además, **garantiza por diseño** que ningún gráfico se queda sin título ni ejes. Explícalo así en el PPT.

### Paso C2: la clase madre `GraficoBechdel` ⏱️ 2 h

**Qué debe tener:**

1. `__init__(self, datos, titulo, etiqueta_x, etiqueta_y, nombre_archivo, carpeta=None)`:
   - guarda todo en atributos **protegidos** (`self._titulo`, `self._carpeta`…);
   - `carpeta=None` es un **parámetro por defecto**: si no se indica, usa `CARPETA_GRAFICOS` de `config`.
2. `@property carpeta` (y si quieres `titulo`): las "puertas" de lectura (**encapsulación**).
3. `_dibujar(self, ax)`: en la madre **no dibuja nada**; solo lanza `NotImplementedError` ("cada hija debe escribir el suyo"). `ax` es el "lienzo" donde se pinta.
4. `generar(self)`: el método que se llama desde fuera. Hace, en orden:
   1. crear la figura y el lienzo (`plt.subplots`);
   2. llamar a `self._dibujar(ax)` (aquí entra la hija);
   3. poner título y nombres de ejes;
   4. llamar a `guardar`;
   5. **cerrar la figura** (`plt.close(fig)`);
   6. devolver la ruta del archivo guardado.
5. `guardar(self, fig, **opciones)`:
   - usa `asegurar_carpeta` de utilidades;
   - llama a `fig.savefig(ruta, **opciones)`. El `**opciones` deja pasar cosas como `dpi=150` o `bbox_inches="tight"` sin tener que escribirlas una a una (esto es **`**kwargs`**).

### Paso C3: las clases hijas (un gráfico cada una) ⏱️ 4–5 h en total

Cada hija:
1. En su `__init__`, recibe los datos y llama a **`super().__init__(datos, "Título…", "Eje X…", "Eje Y…", "nombre_archivo.png")`**. Es decir, le pasa a la madre lo que la madre necesita.
2. Escribe **su propia versión** de `_dibujar(ax)`.

| # | Clase hija | Tipo de gráfico | Datos que recibe (de B) | Qué debe verse | Detalles que lo hacen brillar |
|---|---|---|---|---|---|
| 1 | `GraficoEvolucionDecadas` | **Líneas** con puntos | `tasa_por_decada()` | % de aprobado en cada década | Una línea horizontal discontinua al **50 %** como referencia, y encima de cada punto el número de películas (`n=…`) |
| 2 | `GraficoMotivosSuspenso` | **Barras horizontales** | `motivos_suspenso()` | Cuántas suspenden por cada motivo | Ordenadas según `config`, con el número escrito al final de cada barra y las etiquetas en español ("No hablan entre ellas", etc.) |
| 3 | `GraficoComposicionDecadas` | **Barras apiladas al 100 %** | `composicion_por_decada()` | De qué se compone cada década | Un color por resultado y la leyenda fuera del gráfico para que no tape |
| 4 | `GraficoAprobadoPresupuesto` | **Barras** | `aprobado_por_presupuesto()` y `tasa_aprobado_global()` | % de aprobado en cada tramo de presupuesto | Línea discontinua con la media global y `n=…` bajo cada tramo |
| 5 | `GraficoRentabilidadPresupuesto` | **Barras agrupadas** | `rentabilidad_por_presupuesto()` | ROI mediano de las que aprueban frente a las que suspenden, **dentro de cada tramo** de presupuesto | Escala lineal (se lee como "3,5× = recauda 3,5 $ por cada $ invertido") y línea en 1× ("recupera lo invertido") |
| 6 | `GraficoPresupuestoDecadas` | **Líneas** | `presupuesto_por_decada()` | Presupuesto mediano de las que aprueban y las que suspenden en cada década | La brecha entre las dos líneas sombreada y etiquetas directas al final |
| 7 | `GraficoDesacuerdo` | Barras verticales | `desacuerdo_por_categoria()` | % de desacuerdo por categoría | |

Todos los títulos dicen **la conclusión** del gráfico, no solo lo que muestra. La función `crear_graficos(analizador)` crea los 7 y es la que usa `main.py`.

**Reglas para todos los gráficos:**
- Usa **siempre los mismos colores** para "aprueba" y "suspende" (los de `config.py`).
- **Textos en español**, con tildes (en los textos visibles sí se pueden usar).
- Los números de dinero, en millones: usa `formatear_millones` de utilidades.
- Si la tabla que recibes no tiene las columnas que esperas, usa `comprobar_columnas` y deja que salte `EsquemaIncorrectoError`.

> 💡 **Traducción de los resultados para las etiquetas** (ponlo en `config.py`):
> `ok` → "Aprueba" · `nowomen` → "Menos de 2 mujeres" · `notalk` → "No hablan entre ellas" · `men` → "Solo hablan de hombres" · `dubious` → "Dudoso"

**Cómo saber si está bien:** en el bloque `if __name__ == "__main__":`, genera cada gráfico con los datos de mentira y abre el PNG. Revisa:
- [ ] ¿tiene título?
- [ ] ¿tiene nombre en los dos ejes?
- [ ] ¿se lee bien?
- [ ] ¿se ha guardado en la carpeta correcta?

### Paso C4: conectar con los datos reales ⏱️ 1 h · cuando B termine

1. Sustituye los datos de mentira por las llamadas reales al analizador.
2. Avisa a A de cómo se crea y se genera cada gráfico, para que lo ponga en `main.py`.
3. Ejecuta `python main.py` y revisa los 5 PNG definitivos.

### Paso C5: la presentación (coordinas tú) ⏱️ 3–4 h

**Estructura propuesta (unas 12 diapositivas):**

| # | Diapositiva | Quién aporta el contenido | Qué poner |
|---|---|---|---|
| 1 | Portada | C | Título, nombres, asignatura |
| 2 | ¿Qué es el test de Bechdel? | C | Las 3 reglas y nuestra pregunta: *¿ha mejorado la representación de las mujeres en el cine y tiene relación con el dinero?* |
| 3 | El dataset | B | 1.794 películas, 1970–2013, columnas principales. Fuente: FiveThirtyEight (2014) |
| 4 | Arquitectura | A | **Diagrama** de archivos y clases, con flechas del flujo (la imagen de la "fábrica") |
| 5 | Técnicas obligatorias | Los tres | Tabla: técnica → dónde está → por qué tiene sentido ahí |
| 6 | Validación y excepciones | A | Las reglas, las alarmas y las **capturas de la demo de errores** |
| 7 | Limpieza | B | Problemas encontrados **con números** (98 títulos, 2 IMDb, 1 cero falso…) y la **trampa de los remakes** |
| 8 | Resultado 1: evolución | C | Gráfico 1 + una frase de conclusión |
| 9 | Resultado 2: por qué suspenden | C | Gráficos 2 y 3 + conclusión |
| 10 | Resultado 3: el dinero | C | Gráficos 4 y 5 + conclusión |
| 11 | Conclusiones y limitaciones | Los tres | Ver abajo |
| 12 | Reparto y aprendizajes | Los tres | Quién hizo qué y qué ha costado más |

**Las conclusiones (en lenguaje sencillo):**
1. Algo menos de la mitad de las películas (**44,8 %**) aprueba un test muy básico.
2. Ha **mejorado** desde los años 70 (26 %), pero **se ha estancado** desde los 2000 (≈ 45–49 %).
3. El motivo más común de suspenso es que **las mujeres no hablan entre ellas**.
4. Las películas que aprueban **reciben menos presupuesto**, pero son **igual de rentables o algo más**. El argumento de que "no es rentable" no se sostiene con estos datos.

**Las limitaciones (¡importante ser honestos!):**
- Las películas las eligieron los usuarios de una web, así que **no es una muestra aleatoria**.
- Hay **muy pocas películas antes de 1990**.
- Que dos cosas vayan juntas **no significa que una cause la otra** (correlación no es causalidad).
- El test de Bechdel es un **indicador muy básico**: aprobarlo no hace que una película sea feminista.

### ✅ Checklist de la Persona C

- [ ] Clase madre `GraficoBechdel` con `generar()`, `guardar(**opciones)` y `_dibujar()` sin implementar
- [ ] Atributos protegidos y `@property carpeta`
- [ ] 5 clases hijas, todas llamando a `super().__init__(...)`
- [ ] Todos los gráficos con título, eje X y eje Y
- [ ] Mismos colores en todos los gráficos
- [ ] `plt.close()` después de guardar cada gráfico
- [ ] PNG guardados en `resultados/graficos/`
- [ ] PPT con estructura acordada, conclusiones y limitaciones

---

## 10. Calendario sugerido

> Ajustadlo a vuestra fecha de entrega (el PDF que tenemos no la incluye: **preguntadla al profesor**, junto con los criterios de evaluación).

| Fase | Duración | Persona A | Persona B | Persona C |
|---|---|---|---|---|
| **0. Arranque** (los tres juntos) | 1 sesión de 2 h | Preparar el ordenador · leer esta guía · **acordar los contratos (sección 5)** · `requirements.txt`, `.gitignore`, `config.py` | ← igual | ← igual |
| **1. Cimientos** | 2–3 días | `excepciones.py` | `utilidades.py` | Clase madre de gráficos, con datos de mentira |
| **2. Desarrollo** | 4–5 días | Reglas y lector (`carga.py`) | `limpieza.py` y luego `analisis.py` | Las 5 clases hijas, con datos de mentira |
| **3. Integración** | 2 días | `main.py` y demo de errores | Ayuda a A, revisa resultados | Conecta los gráficos con los datos reales |
| **4. Cierre** | 2–3 días | `README.md` y revisión del código de B | Revisión del código de C, números para el PPT | PPT |
| **5. Prueba final** (los tres juntos) | 1 sesión | Checklist de la sección 12 | ← igual | ← igual |

**Reuniones cortas:** 15 minutos cada 2–3 días para contar qué has hecho, qué vas a hacer y en qué estás atascado.

---

## 11. Errores típicos y cómo resolverlos

| Lo que ves | Qué significa | Cómo arreglarlo |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | No tienes el entorno activado o no has instalado las librerías | Activa el entorno (sección 3.4) y ejecuta `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'bechdel'` | Estás ejecutando desde la carpeta equivocada | Entra en la carpeta raíz del proyecto (`cd trabajo_grupal`) y ejecuta desde ahí. Para probar un módulo: `python -m bechdel.limpieza` |
| `FileNotFoundError` | La ruta del archivo está mal | Usa siempre las rutas de `config.py`, nunca escritas a mano |
| `KeyError: 'year'` | Buscas una columna con un nombre que no existe (quizá ya la renombraste) | Mira el contrato (5.2) para ver el nombre correcto. Imprime `df.columns` |
| `SettingWithCopyWarning` | Estás modificando un trozo de tabla en lugar de una copia | Haz `.copy()` al filtrar |
| Los gráficos salen unos encima de otros | No cierras la figura | `plt.close(fig)` después de guardar |
| Los gráficos están vacíos o blancos | Has guardado **después** de cerrar | El orden es: dibujar → guardar → cerrar |
| `IndentationError` | Los espacios del principio de línea están mal | Python usa los espacios para saber qué va dentro de qué. Usa siempre 4 espacios |
| Conflicto en git (`CONFLICT`) | Dos personas cambiaron la misma línea | No entres en pánico: abre el archivo en VS Code, que te deja elegir qué versión quedarte. Si dudas, pregunta al equipo |
| "En mi ordenador funciona y en el tuyo no" | Versiones distintas o rutas a mano | Comprobad `requirements.txt` y las rutas |

**Cuando te atasques:**
1. **Lee el error de abajo arriba.** La última línea dice **qué** pasó; las de encima dicen **dónde** (archivo y número de línea).
2. Pon un `print()` justo antes de la línea que falla para ver qué valor tienen las variables.
3. Pregunta al equipo. **Atascarse más de 30 minutos solo es perder el tiempo.**

---

## 12. Checklist final antes de entregar

Hacedla **los tres juntos**, en un ordenador donde el proyecto se acabe de descargar (`git clone`) desde cero.

### Requisitos obligatorios del enunciado

- [ ] **Herencia real con `super()`**: gráficos, reglas de validación y excepciones
- [ ] **Encapsulación** con atributos protegidos o privados y `@property`/setter: lector, depurador, analizador y gráficos
- [ ] **`*args`**: `comprobar_columnas`
- [ ] **`**kwargs`**: `filtrar` y `guardar`
- [ ] **Parámetros por defecto**: `porcentaje`, `formatear_millones`, `LectorBechdel(reglas=None)`…
- [ ] **≥2 excepciones propias** heredando de `Exception`, **lanzadas y capturadas**
- [ ] **`try / except / else / finally`** en `main.py`
- [ ] **≥3 gráficos distintos** con título y ejes, en `resultados/graficos/`
- [ ] **CSV limpio** en `resultados/`
- [ ] **Funciones auxiliares fuera de clases** en `utilidades.py`
- [ ] Solo **pandas, numpy, matplotlib** y la librería estándar
- [ ] **Varios archivos** organizados por responsabilidad: ni un único archivo ni un notebook

### Calidad

- [ ] `python main.py` funciona de principio a fin **sin errores rojos**
- [ ] Funciona en el ordenador de **los tres**
- [ ] Cada clase y cada función tiene su docstring
- [ ] No quedan `print` de pruebas ni código comentado sin usar
- [ ] No hay rutas escritas a mano
- [ ] Nombres coherentes en todo el proyecto (sección 6)
- [ ] `README.md` explica cómo ejecutarlo
- [ ] **Los tres entendemos todo el código**, no solo nuestra parte

### Entrega

- [ ] PPT terminado, con gráficos, conclusiones y limitaciones
- [ ] Un único `.zip` (o el enlace al repositorio) con el código, `resultados/` y el PPT
- [ ] El `.zip` **no** incluye `.venv/` ni `__pycache__/`

---

> 💬 **Último consejo:** el profesor valora más un código **sencillo, claro y bien explicado** que uno complicado. Si no sabéis justificar por qué algo está hecho de una manera, simplificadlo. ¡Mucho ánimo! 🎬
