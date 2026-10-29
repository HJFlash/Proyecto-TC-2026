# Gramática libre de contexto

## 1. Descripción

Esta gramática define la sintaxis del DSL para automatizar un gallinero
inteligente. Incluye la extensión de múltiples acciones por regla, donde las
acciones se separan mediante comas.

La gramática se presenta en BNF, sin utilizar las notaciones `+`, `*` ni `?`,
para que pueda utilizarse posteriormente en el diseño del parser LL(1).

## 2. Símbolos de la gramática

La gramática es:

```text
G = (N, Sigma, P, S)
```

donde:

- `N` es el conjunto de símbolos no terminales.
- `Sigma` es el conjunto de símbolos terminales.
- `P` es el conjunto de producciones.
- `S` es el símbolo inicial.

### 2.1 Símbolo inicial

```text
programa
```

### 2.2 Símbolos no terminales

```text
programa
lista_reglas
lista_reglas_prima
regla
condicion
cond_or
cond_or_prima
cond_and
cond_and_prima
factor
comparacion
valor
acciones
acciones_prima
accion
```

El sufijo `_prima` representa una continuación recursiva. Por ejemplo,
`cond_or_prima` corresponde a la parte repetible de una expresión con `OR`.

### 2.3 Símbolos terminales

Los terminales son tokens producidos por el analizador léxico:

```text
WHEN
THEN
AND
OR
NOT
TRUE
FALSE
ID
NUM
OP_REL
COMA
PUNTO_COMA
EOF
```

| Terminal | Descripción |
|---|---|
| `WHEN` | Inicio de una regla |
| `THEN` | Separación entre condición y acciones |
| `AND` | Conjunción lógica |
| `OR` | Disyunción lógica |
| `NOT` | Negación de una comparación |
| `TRUE` | Valor booleano verdadero |
| `FALSE` | Valor booleano falso |
| `ID` | Identificador |
| `NUM` | Número entero no negativo |
| `OP_REL` | Operador relacional |
| `COMA` | Separador entre acciones |
| `PUNTO_COMA` | Terminador de una regla |
| `EOF` | Fin de entrada |

Los posibles lexemas de `OP_REL` son:

```text
>
<
>=
<=
==
!=
```

Los espacios, tabulaciones y saltos de línea son ignorados por el lexer.

## 3. Producciones

### 3.1 Programa y reglas

```text
programa ::= lista_reglas EOF

lista_reglas ::= regla lista_reglas_prima

lista_reglas_prima ::= regla lista_reglas_prima
                     | epsilon

regla ::= WHEN condicion THEN acciones PUNTO_COMA
```

Un programa contiene una o más reglas. Cada regla comienza con `WHEN` y termina
obligatoriamente con `PUNTO_COMA`.

### 3.2 Condiciones

```text
condicion ::= cond_or

cond_or ::= cond_and cond_or_prima

cond_or_prima ::= OR cond_and cond_or_prima
                | epsilon

cond_and ::= factor cond_and_prima

cond_and_prima ::= AND factor cond_and_prima
                  | epsilon

factor ::= NOT comparacion
         | comparacion

comparacion ::= ID OP_REL valor

valor ::= NUM
        | TRUE
        | FALSE
```

Estas producciones establecen la precedencia de los operadores:

1. `NOT` tiene mayor precedencia.
2. `AND` tiene mayor precedencia que `OR`.
3. `OR` tiene la menor precedencia.

Una comparación siempre tiene la forma `ID OP_REL valor`. Por lo tanto, el lado
izquierdo debe ser un identificador y el lado derecho debe ser un número o un
valor booleano.

La gramática es recursiva por la derecha. El AST que construye el parser agrupa
las operaciones binarias de `AND` y `OR` de izquierda a derecha mientras avanza
el análisis. Como ambos operadores son asociativos, el valor de verdad no
cambia; la diferencia es solo la forma de agrupación del árbol.

### 3.3 Acciones

La extensión creativa permite una o más acciones separadas por comas:

```text
acciones ::= accion acciones_prima

acciones_prima ::= COMA accion acciones_prima
                 | epsilon

accion ::= ID ID
```

Cada acción está formada por dos identificadores. El primero representa el verbo
de acción y el segundo representa el dispositivo o destinatario:

```text
abrir puerta
encender ventilador
notificar dueno
```

La producción `acciones` exige al menos una acción. La producción
`acciones_prima` permite repetir acciones separadas por `COMA`.

## 4. Forma compacta equivalente

Usando notación EBNF, la gramática puede resumirse como:

```text
programa    ::= regla+ EOF
regla       ::= WHEN condicion THEN acciones PUNTO_COMA

condicion   ::= cond_or
cond_or     ::= cond_and ( OR cond_and )*
cond_and    ::= factor ( AND factor )*
factor      ::= NOT comparacion | comparacion
comparacion ::= ID OP_REL valor
valor       ::= NUM | TRUE | FALSE

acciones    ::= accion ( COMA accion )*
accion      ::= ID ID
```

La gramática final que utiliza el parser es la versión BNF factorizada de la
sección 3, y es la que debe usarse para construir la tabla LL(1). El detalle de
la transformación se describe en `docs/analisis_gramatica.md`.

## 5. Derivación de ejemplos válidos

### 5.1 Regla con una acción

Entrada:

```text
WHEN luz < 100 THEN abrir puerta;
```

Derivación resumida:

```text
programa
=> lista_reglas EOF
=> regla lista_reglas_prima EOF
=> WHEN condicion THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN cond_or THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN cond_and cond_or_prima THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN factor cond_and_prima cond_or_prima THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN comparacion cond_and_prima cond_or_prima THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN ID OP_REL valor THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN acciones PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN accion acciones_prima PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN ID ID acciones_prima PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN abrir puerta acciones_prima PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN abrir puerta epsilon PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN abrir puerta PUNTO_COMA lista_reglas_prima EOF
=> WHEN luz < 100 THEN abrir puerta PUNTO_COMA epsilon EOF
=> WHEN luz < 100 THEN abrir puerta PUNTO_COMA EOF
```

La entrada es válida porque contiene una condición `ID OP_REL NUM`, una acción
`ID ID`, el terminador `PUNTO_COMA` y el fin de entrada.

### 5.2 Regla con múltiples acciones

Entrada:

```text
WHEN temperatura > 30 THEN encender ventilador, abrir puerta;
```

La parte correspondiente a las acciones se deriva así:

```text
acciones
=> accion acciones_prima
=> ID ID acciones_prima
=> encender ventilador acciones_prima
=> encender ventilador COMA accion acciones_prima
=> encender ventilador COMA ID ID acciones_prima
=> encender ventilador COMA abrir puerta acciones_prima
=> encender ventilador COMA abrir puerta
```

Por lo tanto, la extensión permite ejecutar las acciones en el orden en que
aparecen.

### 5.3 Condición con `AND`, `OR` y `NOT`

Entrada:

```text
WHEN movimiento == TRUE AND NOT alarma_activa == TRUE THEN activar alarma;
```

La condición se deriva utilizando:

```text
condicion
=> cond_or
=> cond_and cond_or_prima
=> factor cond_and_prima cond_or_prima
=> comparacion AND factor cond_and_prima cond_or_prima
=> ID OP_REL valor AND NOT comparacion cond_and_prima cond_or_prima
```

Esto demuestra que `NOT` se aplica a una comparación y que `AND` combina
factores dentro de una condición.

## 6. Verificación de entradas válidas

| Entrada | Resultado | Justificación |
|---|---|---|
| `WHEN luz < 100 THEN abrir puerta;` | Válida | Una comparación y una acción |
| `WHEN temperatura > 30 OR ventilacion == FALSE THEN encender ventilador;` | Válida | Dos comparaciones unidas por `OR` |
| `WHEN humedad >= 80 AND ventilacion != TRUE THEN encender ventilador;` | Válida | Dos comparaciones unidas por `AND` |
| `WHEN movimiento == TRUE AND NOT alarma_activa == TRUE THEN activar alarma;` | Válida | Uso de `NOT` y `AND` |
| `WHEN temperatura > 30 THEN encender ventilador, abrir puerta;` | Válida | Dos acciones separadas por `COMA` |
| `WHEN nivel_alimento < 20 THEN activar comedero; WHEN nivel_agua <= 30 THEN activar bebedero;` | Válida | Dos reglas consecutivas |

## 7. Verificación de entradas inválidas

### 7.1 Falta del valor de una comparación

```text
WHEN luz < THEN abrir puerta;
```

No es derivable porque `comparacion ::= ID OP_REL valor` exige un `valor`
después de `OP_REL`, pero aparece `THEN`.

### 7.2 Falta de `THEN`

```text
WHEN luz < 100 abrir puerta;
```

No es derivable porque después de `condicion` la producción `regla` exige
`THEN`, pero aparece un `ID`.

### 7.3 Falta del punto y coma

```text
WHEN luz < 100 THEN abrir puerta
```

No es derivable porque `regla` exige `PUNTO_COMA` antes de terminar.

### 7.4 Condición vacía

```text
WHEN THEN abrir puerta;
```

No es derivable porque `condicion` debe comenzar con una comparación o con
`NOT`; `THEN` no puede iniciar una condición.

### 7.5 Acción incompleta

```text
WHEN luz < 100 THEN abrir;
```

No es derivable porque `accion ::= ID ID` exige un segundo identificador
después de `abrir`.

### 7.6 Coma final

```text
WHEN temperatura > 30 THEN encender ventilador,;
```

No es derivable porque después de `COMA` debe aparecer otra `accion`.

### 7.7 Coma inicial

```text
WHEN temperatura > 30 THEN , encender ventilador;
```

No es derivable porque `acciones` debe comenzar con `accion`, no con `COMA`.

### 7.8 Falta de coma entre acciones

```text
WHEN temperatura > 30 THEN encender ventilador abrir puerta;
```

No es derivable porque después de una acción solo puede aparecer `COMA` para
continuar con otra acción o `PUNTO_COMA` para terminar la regla.

## 8. Propiedades de la gramática

### 8.1 No permite reglas vacías

`programa` deriva al menos una `regla`, por lo que una entrada vacía no
pertenece al lenguaje.

### 8.2 No permite acciones vacías

La producción `acciones ::= accion acciones_prima` obliga a que toda regla
contenga al menos una acción.

### 8.3 No permite comas consecutivas

Después de `COMA` se exige una `accion`; por ello, una secuencia como
`accion,,accion` no puede derivarse.

### 8.4 No permite comparaciones encadenadas

La producción `comparacion ::= ID OP_REL valor` contiene un único operador
relacional. Por ello, `luz < 100 < 200` no puede derivarse.

### 8.5 Compatibilidad con la versión base

Una regla con una sola acción sigue siendo válida porque:

```text
acciones ::= accion acciones_prima
acciones_prima ::= epsilon
```

La extensión, por tanto, conserva todos los programas válidos de la versión
base.

### 8.6 Ausencia de recursión izquierda

La repetición se expresa mediante recursión por la derecha:

```text
lista_reglas_prima ::= regla lista_reglas_prima | epsilon
cond_or_prima ::= OR cond_and cond_or_prima | epsilon
cond_and_prima ::= AND factor cond_and_prima | epsilon
acciones_prima ::= COMA accion acciones_prima | epsilon
```

Esto permite utilizar la gramática en un parser predictivo LL(1).

## 9. Resumen de producciones

```text
programa ::= lista_reglas EOF

lista_reglas ::= regla lista_reglas_prima

lista_reglas_prima ::= regla lista_reglas_prima
                     | epsilon

regla ::= WHEN condicion THEN acciones PUNTO_COMA

condicion ::= cond_or

cond_or ::= cond_and cond_or_prima

cond_or_prima ::= OR cond_and cond_or_prima
                | epsilon

cond_and ::= factor cond_and_prima

cond_and_prima ::= AND factor cond_and_prima
                  | epsilon

factor ::= NOT comparacion
         | comparacion

comparacion ::= ID OP_REL valor

valor ::= NUM
        | TRUE
        | FALSE

acciones ::= accion acciones_prima

acciones_prima ::= COMA accion acciones_prima
                 | epsilon

accion ::= ID ID
```
