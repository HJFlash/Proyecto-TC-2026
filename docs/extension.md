# Extensión creativa — Rutinas de acciones

**Proyecto:** Analizador sintáctico para un DSL — INFO1148, Teoría de la Computación  
**Integrantes:** Tomás Curihual, Rodrigo Gutierrez, Carlos Huenuman  
**Estado:** Versión 1.0 para revisión.

## 1. Extensión elegida

Se elige **múltiples acciones por regla**, separadas por coma.

La extensión permite que una regla ejecute una rutina de acciones en lugar de una sola acción. Por ejemplo, al detectar temperatura alta el sistema puede encender el ventilador y abrir la puerta en la misma regla.

Se evaluaron también los paréntesis, `ELSE` y las acciones con duración. Se optó por múltiples acciones por su encaje directo con el dominio del gallinero, su bajo impacto en la gramática LL(1) y la facilidad de integrarla en el parser, el AST y las pruebas. Las otras alternativas siguen siendo viables, pero no forman parte de esta extensión.

## 2. Relación con la versión base

La definición base de `docs/lenguaje.md` permite exactamente una acción por regla:

```text
WHEN condicion THEN accion ;
```

Esta extensión reemplaza esa restricción para la versión final del lenguaje:

```text
WHEN condicion THEN accion, accion, ... ;
```

La extensión es compatible con la base: todo programa válido anterior sigue siendo válido, porque una acción puede interpretarse como una lista de un solo elemento. La especificación consolidada de la gramática se realizará en `docs/gramatica.md` (#3); este documento no modifica `docs/lenguaje.md`.

## 3. Sintaxis y semántica

### 3.1 Forma general

```text
regla    ::= WHEN condicion THEN acciones ;
acciones ::= accion ( COMA accion )*
accion   ::= ID ID
```

### 3.2 Token nuevo

| Token | Lexema | Uso |
|---|---|---|
| `COMA` | `,` | Separar acciones dentro de una misma regla |

El carácter `,` se agrega al alfabeto del lenguaje. Los espacios alrededor de la coma son irrelevantes porque el lexer ignora el espacio en blanco.

### 3.3 Reglas de composición

- Debe existir al menos una acción.
- Las acciones se separan mediante `,`.
- La regla termina obligatoriamente en `;`.
- Las acciones se ejecutan de izquierda a derecha.
- No se permite una coma antes de la primera acción.
- No se permite una coma después de la última acción.
- No se permiten dos comas consecutivas.
- Una acción siempre tiene la forma `ID ID`: verbo y dispositivo.
- Una acción por sí sola sigue siendo válida.

## 4. Ejemplos

### 4.1 Cinco sentencias válidas

1. `WHEN temperatura > 30 THEN encender ventilador, abrir puerta;`  
   Ejecuta dos acciones cuando la temperatura supera el umbral.

2. `WHEN luz < 100 THEN abrir puerta, encender lampara;`  
   Combina la apertura de la puerta con la iluminación.

3. `WHEN movimiento == TRUE THEN activar alarma, notificar dueno;`  
   Activa la alarma y notifica al dueño.

4. `WHEN nivel_alimento < 20 THEN activar comedero, notificar dueno;`  
   Repone alimento y avisa al operador.

5. Programa con dos reglas y acciones múltiples:

```text
WHEN temperatura > 30 THEN encender ventilador, abrir puerta;
WHEN luz < 20 THEN cerrar puerta, apagar lampara;
```

### 4.2 Cinco sentencias inválidas

| # | Entrada | Error esperado | Qué incumple |
|---|---|---|---|
| 1 | `WHEN temperatura > 30 THEN encender ventilador,;` | Se esperaba una acción después de `,` | Coma final |
| 2 | `WHEN temperatura > 30 THEN , encender ventilador;` | Se esperaba una acción | Coma inicial |
| 3 | `WHEN temperatura > 30 THEN encender ventilador abrir puerta;` | Se esperaba `,` o `;` | Falta la coma entre acciones |
| 4 | `WHEN temperatura > 30 THEN encender ventilador, ;` | Se esperaba una acción | Coma sin acción |
| 5 | `WHEN temperatura > 30 THEN encender ventilador, abrir;` | Se esperaba un identificador de dispositivo | Acción incompleta |

Las cinco entradas son léxicamente válidas: la coma es un token reconocido. Los errores son estrictamente sintácticos.

## 5. Verificación LL(1)

Para verificar la tabla se usa la versión sin EBNF:

```text
regla     ::= WHEN condicion THEN acciones ;
acciones  ::= accion acciones'
acciones' ::= COMA accion acciones' | ε
accion    ::= ID ID
```

### 5.1 FIRST y FOLLOW nuevos

```text
FIRST(acciones)   = { ID }
FIRST(acciones')  = { COMA, ε }
FOLLOW(acciones)  = { PUNTO_COMA }
FOLLOW(acciones') = { PUNTO_COMA }
FOLLOW(accion)    = { COMA, PUNTO_COMA }
```

### 5.2 Fragmento de tabla LL(1)

| No terminal | `ID` | `COMA` | `PUNTO_COMA` |
|---|---|---|---|
| `acciones` | `acciones -> accion acciones'` | — | — |
| `acciones'` | — | `acciones' -> COMA accion acciones'` | `acciones' -> ε` |

### 5.3 Análisis de conflictos

No hay conflicto LL(1):

- `FIRST(acciones')` contiene `COMA` y `ε`.
- `FOLLOW(acciones')` es `{ PUNTO_COMA }`.
- `COMA` no pertenece a `FOLLOW(acciones')`.
- `PUNTO_COMA` no pertenece a `FIRST(acciones')`.
- Las alternativas de `acciones'` tienen FIRST disjuntos.
- El resto de la gramática no cambia y ya era LL(1).
- No se introduce recursión izquierda ni ambigüedad.
- La producción `acciones' -> COMA accion acciones'` es recursiva por la derecha, lo cual es válido para LL(1).

Por lo tanto, la extensión se puede expresar en LL(1) sin conflictos graves.

## 6. Impacto e integración prevista

Esta issue solo especifica y verifica la extensión. La implementación material se distribuye en los issues posteriores:

| Artefacto | Cambio que habilita la extensión | Issue |
|---|---|---|
| Gramática | `regla` usa `acciones`; se agregan `acciones` y `acciones'` | #3 |
| Análisis | No hay recursión izquierda, ambigüedad ni factorización nueva | #4 |
| FIRST/FOLLOW | Se agregan los conjuntos de `acciones`, `acciones'` y `accion` | #5 |
| Tabla LL(1) | Se agregan filas y columnas para `acciones`, `acciones'` y `COMA` | #6 |
| Lexer | Se agrega el token `COMA` y el lexema `,` | #7 |
| Parser | Se parsea una acción y se repite mientras el siguiente token sea `COMA` | #8 |
| AST | La regla guarda una lista ordenada de acciones | #9 |
| Errores | Mensajes para coma sin acción y para falta de coma o `;` | #10 |
| Pruebas | Se incorporan los 5 casos válidos y 5 inválidos de esta extensión | #11 |

Con esto la extensión no queda decorativa: cada artefacto posterior tiene un cambio identificable. En esta issue no se implementa lexer, parser, AST ni pruebas automáticas; solo se deja la especificación necesaria para hacerlo.
