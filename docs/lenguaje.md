# Definición del lenguaje — Gallinero inteligente

**Proyecto:** Analizador sintáctico para un DSL — INFO1148, Teoría de la Computación  
**Integrantes:** Tomás Curihual, Rodrigo Gutierrez, Carlos Huenuman  
**Estado:** Versión 1.0 para revisión y aprobación de los tres integrantes.

## 1. Dominio y propósito

### 1.1 Contexto

Un gallinero de pequeña escala requiere tareas repetitivas: abrir la puerta por la mañana, cerrarla al anochecer, vigilar la temperatura y la humedad, reponer alimento y agua, y detectar movimiento de posibles depredadores. Estas decisiones pueden expresarse como reglas simples del tipo “si ocurre una condición, ejecutar una acción”.

### 1.2 Propósito

Diseñar un lenguaje de dominio específico (DSL) declarativo para automatizar un gallinero inteligente. El operador escribe reglas legibles y un controlador las evalúa cíclicamente para accionar la puerta, la iluminación, la ventilación, el comedero, el bebedero y la alarma.

El lenguaje prioriza la claridad y la facilidad de análisis sintáctico. No es un lenguaje de propósito general: no incluye variables, funciones, aritmética, cadenas de texto, horarios ni control de flujo.

### 1.3 Alcance de la versión base

La versión base permite:

- Escribir una o más reglas.
- Comparar sensores con valores numéricos o booleanos.
- Combinar comparaciones con `AND`, `OR` y `NOT`.
- Ejecutar una acción por regla, indicando un verbo y un dispositivo.

Quedan fuera de esta versión los paréntesis, los comentarios y las acciones con parámetros. La extensión creativa permite múltiples acciones separadas por comas. La validez sintáctica no verifica la existencia real de sensores o actuadores ni la compatibilidad de tipos; esa validación es semántica y queda fuera del alcance del proyecto.

## 2. Alternativas de dominio y decisión

### 2.1 Opciones evaluadas

| Opción | Propósito | Ejemplo orientativo | Fortaleza | Punto a cuidar |
|---|---|---|---|---|
| **Gallinero inteligente** | Automatizar puerta, temperatura, alimentación, agua y alertas | `WHEN luz < 100 AND puerta_cerrada == TRUE THEN abrir puerta;` | Dominio concreto, original y con vocabulario simple | Nombres booleanos claros; evitar horarios |
| **Acuario o estanque** | Mantener la calidad del agua y la salud de los peces | `WHEN temperatura > 28 OR oxigeno < 5 THEN encender aireador;` | Sensores variados y pruebas intuitivas | Explicar rangos de pH y oxígeno; usar enteros |
| **Sistema de riego** | Automatizar el riego de una parcela o jardín con ahorro de agua | `WHEN humedad_suelo < 30 AND lluvia == FALSE THEN abrir valvula;` | Muy intuitivo, regional y fácil de probar | Distinguirlo de un invernadero; enfocarlo en parcela o jardín |

Los ejemplos de la tabla son ilustrativos de cada alternativa. La definición del lenguaje y los casos de este documento corresponden al dominio elegido: el gallinero inteligente.

### 2.2 Decisión

Se elige **gallinero inteligente** porque:

- Tiene sensores y actuadores fáciles de identificar y explicar.
- Permite reglas naturales con valores numéricos y booleanos.
- Se adapta bien a la forma `WHEN ... THEN <verbo> <dispositivo>;`.
- Tiene relevancia regional y suficiente originalidad sin aumentar la complejidad sintáctica.
- Facilita ejemplos válidos, inválidos y casos límite comprensibles.

Acuario y sistema de riego siguen siendo alternativas viables; se conservan en esta sección para dejar registrada la comparación.

## 3. Alfabeto y categorías de tokens

### 3.1 Alfabeto

El alfabeto de la versión base es:

```text
Σ = { A-Z, a-z, 0-9, _, espacio, tab, salto de línea, retorno de carro, >, <, =, !, ; }
```

No se incluyen paréntesis, comas, puntos, guiones, comillas, caracteres acentuados ni el símbolo `#`. Los caracteres `=` y `!` solo aparecen como parte de los operadores relacionales compuestos.

Los identificadores son ASCII: se escribe `lampara`, no `lámpara`.

### 3.2 Categorías de tokens

| Categoría | Tokens | Lexemas o patrón | Ejemplo |
|---|---|---|---|
| Estructural | `WHEN`, `THEN` | lexemas reservados | `WHEN` |
| Lógico | `AND`, `OR`, `NOT` | lexemas reservados | `AND` |
| Booleano | `TRUE`, `FALSE` | lexemas reservados | `TRUE` |
| Identificador | `ID` | `[A-Za-z_][A-Za-z0-9_]*` | `humedad` |
| Número | `NUM` | `[0-9]+` | `100` |
| Relacional | `OP_REL` | `>=`, `<=`, `==`, `!=`, `>`, `<` | `>=` |
| Separador | `PUNTO_COMA` | `;` | `;` |
| Fin de entrada | `EOF` | interno | — |
| Ignorado | `ESPACIO` | espacios, tabs y saltos de línea | — |
| Error | `ERROR` | cualquier otro carácter | `@` |

### 3.3 Convenciones léxicas

- Las palabras reservadas se reconocen sin distinguir mayúsculas de minúsculas. Por convención se escriben en mayúsculas.
- Los identificadores distinguen mayúsculas de minúsculas y no pueden coincidir con una palabra reservada.
- Los espacios, tabs y saltos de línea se ignoran.
- Los operadores relacionales se reconocen por la coincidencia más larga: `>=` antes que `>`, `==` antes que `=`.
- Un `=` aislado no es un token válido; la igualdad se escribe `==`.
- Cualquier símbolo no reconocido produce un token de error léxico.

## 4. Palabras reservadas, identificadores, valores, operadores y separadores

### 4.1 Palabras reservadas

La versión base tiene siete palabras reservadas:

| Palabra | Función |
|---|---|
| `WHEN` | Inicia una regla |
| `THEN` | Separa la condición de la acción |
| `AND` | Conjunción lógica binaria |
| `OR` | Disyunción lógica binaria |
| `NOT` | Negación lógica de una comparación |
| `TRUE` | Valor booleano verdadero |
| `FALSE` | Valor booleano falso |

### 4.2 Identificadores

Un identificador es un nombre de sensor, actuador, verbo de acción o destinatario. Su forma es:

```text
[A-Za-z_][A-Za-z0-9_]*
```

Se recomienda `snake_case` y nombres descriptivos. El vocabulario del dominio es:

| Tipo | Identificadores |
|---|---|
| Sensores numéricos | `luz`, `temperatura`, `humedad`, `nivel_alimento`, `nivel_agua` |
| Sensores booleanos | `movimiento`, `puerta_cerrada`, `ventilacion`, `alarma_activa` |
| Actuadores | `puerta`, `lampara`, `ventilador`, `calefactor`, `comedero`, `bebedero`, `alarma` |
| Verbos de acción | `abrir`, `cerrar`, `encender`, `apagar`, `activar`, `desactivar`, `notificar` |
| Destinatario | `dueno` |

Los verbos de acción y los destinatarios son identificadores, no palabras reservadas. Que un verbo pertenezca al vocabulario del dominio es una convención semántica; el analizador sintáctico solo valida que la acción tenga la forma `ID ID`.

### 4.3 Valores

- `NUM`: entero no negativo, formado por uno o más dígitos.
- `TRUE` y `FALSE`: valores booleanos.

No se admiten números negativos, decimales ni cadenas de texto en la versión base.

### 4.4 Operadores

**Relacionales:**

- `>` mayor que
- `<` menor que
- `>=` mayor o igual que
- `<=` menor o igual que
- `==` igual a
- `!=` distinto de

**Lógicos:**

- `AND` conjunción
- `OR` disyunción
- `NOT` negación

En total, la versión base tiene nueve operadores.

### 4.5 Separadores

El punto y coma `;` termina cada regla y es obligatorio. No se usan comas ni otros separadores en la versión base.

### 4.6 Precedencia y restricciones de las comparaciones

- `NOT` se aplica a la comparación que le sigue y tiene mayor precedencia que `AND`; `AND` tiene mayor precedencia que `OR`.
- `AND` y `OR` son asociativos; la asociatividad no altera el valor de verdad.
- Cada comparación tiene exactamente un operador relacional.
- El lado izquierdo de una comparación es un identificador y el lado derecho es un valor.
- No se permiten comparaciones encadenadas como `luz < 100 < 200`.
- No se permiten comparaciones entre dos identificadores en la versión base.

## 5. Sentencia principal y múltiples reglas

### 5.1 Forma general

```text
programa    ::= regla+
regla       ::= WHEN condicion THEN accion ;
condicion   ::= cond_or
cond_or     ::= cond_and ( OR cond_and )*
cond_and    ::= comparacion ( AND comparacion )*
comparacion ::= [ NOT ] ID OP_REL valor
accion      ::= ID ID
valor       ::= NUM | TRUE | FALSE
```

Esta forma general define la estructura de las sentencias. No es la gramática libre de contexto formal; su construcción y análisis se desarrollan en una etapa posterior del proyecto.

### 5.2 Reglas de composición

- Un programa contiene una o más reglas.
- Cada regla termina obligatoriamente en `;`.
- Varias reglas se escriben una después de otra; el punto y coma es el terminador.
- Cada regla tiene exactamente una acción.
- La acción se escribe como un verbo seguido de un dispositivo: `abrir puerta`, `encender ventilador`.
- Una condición puede ser una sola comparación o varias comparaciones unidas por `AND` u `OR`.
- `NOT` se aplica a la comparación que le sigue.
- No se permiten reglas vacías ni secuencias como `;;`.
- El programa termina cuando se alcanza el fin de entrada (`EOF`).

### 5.3 Validez sintáctica

El analizador determina si una entrada respeta la estructura anterior. La existencia del sensor o actuador, la coherencia entre el tipo de sensor y el valor, y la pertenencia del verbo al vocabulario del dominio son validaciones semánticas que no forman parte de esta definición.

## 6. Ejemplos

### 6.1 Cinco sentencias válidas

1. `WHEN luz < 100 AND puerta_cerrada == TRUE THEN abrir puerta;`  
   Compara un sensor numérico y uno booleano, combina con `AND` y ejecuta una acción de dos identificadores.

2. `WHEN temperatura > 30 OR ventilacion == FALSE THEN encender ventilador;`  
   Usa `OR`, un valor booleano falso y una acción sobre el ventilador.

3. `WHEN humedad >= 80 AND ventilacion != TRUE THEN encender ventilador;`  
   Usa `>=`, `!=` y `AND`.

4. `WHEN movimiento == TRUE AND NOT alarma_activa == TRUE THEN activar alarma;`  
   Usa `NOT` dentro de una condición compuesta.

5. Programa con dos reglas:

```text
WHEN nivel_alimento < 20 THEN activar comedero;
WHEN nivel_agua <= 30 THEN activar bebedero;
```

Las cinco sentencias cubren los 11 tokens visibles para el parser y los nueve operadores. La quinta demuestra cómo se escriben varias reglas.

### 6.2 Cinco sentencias inválidas

| # | Entrada | Error esperado | Qué incumple |
|---|---|---|---|
| 1 | `WHEN luz < THEN abrir puerta;` | Se esperaba un valor después de `<` | Falta el operando derecho de la comparación |
| 2 | `WHEN luz < 100 abrir puerta;` | Se esperaba `THEN` | Falta el separador entre condición y acción |
| 3 | `WHEN luz < 100 THEN abrir puerta` | Se esperaba `;` | Falta el terminador de la regla |
| 4 | `WHEN THEN abrir puerta;` | Se esperaba un identificador o `NOT` | Falta la condición |
| 5 | `WHEN luz < 100 THEN abrir;` | Se esperaba un identificador de dispositivo | La acción solo tiene el verbo |

Las cinco entradas son léxicamente válidas: todos sus símbolos pertenecen al alfabeto y forman tokens reconocidos. Los errores son estrictamente sintácticos.
