# Analizador Sintáctico para un DSL — Gallinero inteligente

Proyecto grupal de **Teoría de la Computación (INFO1148)**, Universidad Católica
de Temuco.

Diseño e implementación de un analizador sintáctico predictivo **LL(1)** en
Python para un lenguaje de dominio específico (DSL) que automatiza un gallinero
inteligente. El analizador valida programas, construye el árbol de sintaxis
abstracta (AST) y reporta errores sintácticos con mensajes contextuales.

> **Estado:** implementación y pruebas completas. Informe final pendiente
> (issue #13).

## Integrantes

- Tomás Curihual
- Rodrigo Gutierrez
- Carlos Huenuman

## Dominio y lenguaje

El DSL permite describir reglas declarativas para automatizar un gallinero de
pequeña escala: abrir y cerrar la puerta, controlar la iluminación y la
ventilación, reponer alimento y agua, y activar alarmas.

Cada regla compara sensores numéricos o booleanos (`luz`, `temperatura`,
`humedad`, `movimiento`, `nivel_agua`, entre otros) y, si la condición se
cumple, ejecuta una o más acciones sobre los actuadores. Las comparaciones se
combinan con `AND`, `OR` y `NOT`; la extensión creativa del lenguaje permite
varias acciones separadas por comas dentro de una misma regla.

Ejemplo de sentencia válida con múltiples acciones:

```text
WHEN temperatura > 30 THEN encender ventilador, abrir puerta;
```

La definición completa del vocabulario, los tokens y las reglas de composición
está en [`docs/lenguaje.md`](docs/lenguaje.md) y
[`docs/extension.md`](docs/extension.md).

## Estructura del repositorio

```text
README.md
requirements.txt
docs/
  lenguaje.md
  extension.md
  gramatica.md
  analisis_gramatica.md
  first_follow.md
  tabla_ll1.md
src/
  lexer.py
  parser.py
  errores.py
  arbol.py
tests/
  casos_prueba.md
  test_parser.py
  test_errores.py
```

El informe final en LaTeX se incorporará en la issue #13; por eso todavía no
aparece en el repositorio.

## Requisitos

- **Python 3.10 o superior**.
- **Sin dependencias externas**: el proyecto usa únicamente la biblioteca
  estándar de Python. El archivo `requirements.txt` no instala paquetes.

## Instalación

### Linux / macOS

```bash
git clone https://github.com/HJFlash/Proyecto-TC-2026.git
cd Proyecto-TC-2026
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone https://github.com/HJFlash/Proyecto-TC-2026.git
cd Proyecto-TC-2026
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En Windows también se puede activar el entorno desde `cmd.exe` con
`.venv\Scripts\activate.bat`. En todos los casos, `python` debe corresponder a
Python 3.10 o superior.

## Uso

El analizador recibe el programa como argumento de la línea de comandos:

```bash
python src/parser.py "WHEN luz < 100 THEN abrir puerta;"
```

También se puede ejecutar como módulo:

```bash
python -m src.parser "WHEN luz < 100 THEN abrir puerta;"
```

**Formato de entrada:** un programa completo entre comillas. Si se pasan varios
argumentos, el analizador los une con espacios antes de procesarlos. No existe
modo archivo ni modo interactivo: cada ejecución analiza una sola entrada.

### Ejemplo de salida válida

Para la entrada anterior, la salida es:

```text
Entrada sintácticamente válida. Árbol generado:
└── Programa
  ├── Regla (WHEN ... THEN ...)
    ├── Condicion:
      └── Comparacion: luz < 100
    └── Acciones:
      └── Accion: abrir puerta
```

### Ejemplo de entrada inválida

Si se omite el punto y coma final:

```bash
python src/parser.py "WHEN luz < 100 THEN abrir puerta"
```

el analizador reporta el error por la salida de error estándar:

```text
Error sintáctico en línea 1, columna 33: se esperaba el punto y coma ';' para terminar la regla; se encontró el final de la entrada.
```

### Códigos de salida

| Código | Significado |
|---|---|
| `0` | Entrada sintácticamente válida; el árbol se imprimió correctamente. |
| `1` | Error sintáctico o léxico en la entrada. |
| `2` | No se proporcionaron argumentos; se muestra el uso del comando. |

## Pruebas

La matriz de casos de prueba se ejecuta con:

```bash
python tests/test_parser.py
```

El script recorre **46 casos**: 25 entradas válidas y 21 inválidas, e incluye
9 casos límite y 10 casos de la extensión creativa. Muestra el detalle de los
fallos y devuelve código de salida `0` solo cuando todos los casos pasan. La
tabla completa está en [`tests/casos_prueba.md`](tests/casos_prueba.md) y puede
regenerarse con:

```bash
python tests/test_parser.py --tabla tests/casos_prueba.md
```

Las pruebas del manejo de errores se ejecutan aparte:

```bash
python tests/test_errores.py
```

Son **30 pruebas** que verifican los mensajes, las posiciones y los códigos de
salida ante entradas inválidas.

La suite basada en `unittest` ejecuta la matriz completa (una prueba que recorre
los 46 casos) y las 30 pruebas del manejo de errores:

```bash
python -m unittest discover -s tests -v
```

## Documentación

- [Definición del lenguaje y tokens](docs/lenguaje.md)
- [Extensión creativa: múltiples acciones](docs/extension.md)
- [Gramática libre de contexto](docs/gramatica.md)
- [Análisis de la gramática](docs/analisis_gramatica.md)
- [Conjuntos FIRST y FOLLOW](docs/first_follow.md)
- [Tabla predictiva LL(1)](docs/tabla_ll1.md)

## Restricciones del proyecto

- No se utiliza ningún generador automático de parsers.
- El parser está implementado a mano según la gramática y la tabla LL(1)
  documentadas en `docs/`.
