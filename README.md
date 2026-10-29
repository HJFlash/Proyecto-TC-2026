# Analizador Sintáctico para un DSL

Proyecto grupal de **Teoría de la Computación (INFO1148)**, Universidad Católica de Temuco.

Diseño e implementación de un analizador sintáctico predictivo **LL(1)** en Python para un lenguaje de dominio específico (DSL), con construcción de árbol sintáctico y detección de errores.

> **Estado:** en desarrollo (inicio del proyecto)

## Integrantes

- Tomás Curihual
- Rodrigo Gutierrez
- Carlos Huenuman

## Dominio y lenguaje

**Dominio:** _por definir_

**Descripción:** _por definir (ver `docs/lenguaje.md`)_

**Ejemplo de sentencia:**

```
(por definir)
```

## Estructura del repositorio

```
README.md
requirements.txt
docs/
  lenguaje.md            # Definición del lenguaje y tokens
  extension.md           # Extensión creativa
  gramatica.md           # Gramática libre de contexto
  analisis_gramatica.md  # Recursión, factorización, ambigüedad
  first_follow.md        # Conjuntos FIRST y FOLLOW
  tabla_ll1.md           # Tabla predictiva LL(1)
src/
  lexer.py               # Analizador léxico
  parser.py              # Analizador sintáctico predictivo
  arbol.py               # Árbol sintáctico / AST
tests/
  casos_prueba.md        # Tabla de casos de prueba
  test_parser.py         # Ejecución automática de pruebas
  test_errores.py        # Pruebas del manejo de errores
informe/
  main.tex               # Informe en LaTeX
  capturas/              # Capturas de la demostración
```

## Requisitos

- Python 3.10 o superior
- Dependencias adicionales: ver `requirements.txt` (_por definir_)

## Instalación

```powershell
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso

```powershell
python src/parser.py "<entrada>"
```

_(por definir: formato de entrada, uso por archivo o modo interactivo)_

### Ejemplo de entrada válida

```
(por definir)
```

### Ejemplo de salida

```
(por definir)
```

### Ejemplo de entrada inválida

```
(por definir)
```

## Pruebas

```powershell
python tests/test_parser.py
```

El script ejecuta la matriz de 46 casos: 25 entradas válidas y 21 inválidas,
con 9 casos límite y 10 casos de la extensión creativa. Muestra el detalle de
los fallos y devuelve código de salida `0` solo cuando todos pasan. La tabla
completa está en `tests/casos_prueba.md` y puede regenerarse con:

```powershell
python tests/test_parser.py --tabla
```

Las pruebas del manejo de errores se ejecutan aparte:

```powershell
python tests/test_errores.py
```

## Restricciones del proyecto

- No se utiliza ningún generador automático de parsers.
- El parser está implementado a mano a partir de la gramática y la tabla LL(1) documentadas en `docs/`.

## Documentación

- [Definición del lenguaje](docs/lenguaje.md)
- [Gramática](docs/gramatica.md)
- [FIRST y FOLLOW](docs/first_follow.md)
- [Tabla LL(1)](docs/tabla_ll1.md)
- Informe final: `informe/`
