# Casos de prueba del parser

La matriz contiene 46 casos: 25 entradas válidas y 21 inválidas, organizadas en
13 casos `V`, 14 casos `I`, 9 casos límite `L` y 10 casos de la extensión
creativa `E`. Los 10 casos de extensión incluyen 5 entradas válidas y 5
inválidas. El resultado obtenido se verifica automáticamente con:

```powershell
python tests/test_parser.py
```

En las entradas válidas también se comprueba la cantidad de reglas y acciones
generadas en el AST. Las palabras reservadas pueden escribirse en minúsculas,
pero los identificadores conservan su distinción entre mayúsculas y minúsculas.
Las tabulaciones, retornos de carro y saltos de línea se muestran escapados
como `\t`, `\r` y `\n` para que la entrada sea legible en la tabla.

| ID | Categoría | Entrada | Resultado esperado | Resultado obtenido | Observación |
|---|---|---|---|---|---|
| V01 | Válida | `WHEN luz < 100 THEN abrir puerta;` | Válida | Válida | Regla mínima con comparación numérica. |
| V02 | Válida | `WHEN temperatura > 30 THEN encender ventilador;` | Válida | Válida | Operador mayor que y una acción. |
| V03 | Válida | `WHEN humedad >= 80 THEN encender ventilador;` | Válida | Válida | Operador mayor o igual. |
| V04 | Válida | `WHEN nivel_agua <= 30 THEN activar bebedero;` | Válida | Válida | Identificador con guion bajo y operador menor o igual. |
| V05 | Válida | `WHEN ventilacion != TRUE THEN activar alarma;` | Válida | Válida | Comparación booleana con !=. |
| V06 | Válida | `WHEN NOT alarma_activa == FALSE THEN notificar dueno;` | Válida | Válida | Negación de una comparación. |
| V07 | Válida | `WHEN luz < 100 AND puerta_cerrada == TRUE THEN abrir puerta;` | Válida | Válida | Condición compuesta con AND. |
| V08 | Válida | `WHEN temperatura > 30 OR ventilacion == FALSE THEN encender ventilador, abrir puerta;` | Válida | Válida | OR y dos acciones de la extensión creativa. |
| V09 | Válida | `WHEN movimiento == TRUE THEN activar alarma, notificar dueno, cerrar puerta;` | Válida | Válida | Tres acciones ordenadas separadas por comas. |
| V10 | Válida | `WHEN nivel_alimento < 20 THEN activar comedero; WHEN nivel_agua <= 30 THEN activar bebedero;` | Válida | Válida | Programa con dos reglas. |
| V11 | Válida | `when LUZ < 100 then abrir puerta;` | Válida | Válida | Palabras reservadas sin distinguir mayúsculas. |
| V12 | Válida | `WHEN temperatura == 000000 THEN encender calefactor;` | Válida | Válida | Número con ceros y longitud mayor. |
| V13 | Válida | `WHEN humedad >= 80 AND ventilacion != TRUE OR movimiento == FALSE THEN activar alarma, notificar dueno;` | Válida | Válida | Precedencia AND sobre OR y acciones múltiples. |
| I01 | Inválida | `WHEN luz < 100 THEN abrir puerta` | Inválida | Inválida | Falta el punto y coma final. |
| I02 | Inválida | `WHEN luz < 100 abrir puerta;` | Inválida | Inválida | Falta la palabra reservada THEN. |
| I03 | Inválida | `WHEN luz < THEN abrir puerta;` | Inválida | Inválida | Falta el valor de la comparación. |
| I04 | Inválida | `WHEN THEN abrir puerta;` | Inválida | Inválida | Falta la condición. |
| I05 | Inválida | `WHEN luz < 100 THEN abrir;` | Inválida | Inválida | La acción no tiene dispositivo. |
| I06 | Inválida | `WHEN luz < 100 THEN , abrir puerta;` | Inválida | Inválida | La coma no puede iniciar la lista de acciones. |
| I07 | Inválida | `WHEN luz < 100 THEN abrir puerta,;` | Inválida | Inválida | La coma final debe ir seguida de otra acción. |
| I08 | Inválida | `WHEN luz < 100 THEN abrir puerta,, encender lampara;` | Inválida | Inválida | No se permiten comas consecutivas. |
| I09 | Inválida | `WHEN luz < 100 THEN abrir puerta encender lampara;` | Inválida | Inválida | Las acciones deben separarse con coma. |
| I10 | Inválida | `WHEN luz < 100 THEN abrir puerta @;` | Inválida | Inválida | El símbolo @ no pertenece al lenguaje. |
| I11 | Inválida | `WHEN luz < 100 THEN (abrir puerta);` | Inválida | Inválida | Los paréntesis no están soportados. |
| I12 | Inválida | `WHEN luz = 100 THEN abrir puerta;` | Inválida | Inválida | La igualdad requiere ==. |
| I13 | Inválida | `WHEN luz < -1 THEN abrir puerta;` | Inválida | Inválida | No se admiten números negativos. |
| I14 | Inválida | `WHEN luz < 10.5 THEN abrir puerta;` | Inválida | Inválida | No se admiten números decimales. |
| L01 | Límite | `WHEN luz < 100 THEN abrir puerta;` | Válida | Válida | Una sola regla y una sola acción. |
| L02 | Límite | ` \t WHEN luz < 100 \n THEN \t abrir \t puerta , encender lampara ; \r\n` | Válida | Válida | Espacios, tabulaciones y saltos de línea. |
| L03 | Límite | `WHEN sensor_1 < 1 AND sensor_2 < 2 AND sensor_3 < 3 AND sensor_4 < 4 AND sensor_5 < 5 AND sensor_6 < 6 AND sensor_7 < 7 AND sensor_8 < 8 AND sensor_9 < 9 THEN activar alarma;` | Válida | Válida | Cadena profunda de nueve comparaciones con AND. |
| L04 | Límite | `WHEN sensor_1 < 1 OR sensor_2 < 2 OR sensor_3 < 3 OR sensor_4 < 4 OR sensor_5 < 5 OR sensor_6 < 6 THEN activar alarma;` | Válida | Válida | Cadena profunda de comparaciones con OR. |
| L05 | Límite | `WHEN movimiento == TRUE THEN activar alarma, notificar dueno, encender lampara, cerrar puerta, activar camara;` | Válida | Válida | Rutina de cinco acciones. |
| L06 | Límite | `WHEN a == TRUE THEN x y;\nWHEN b == FALSE THEN z w;\nWHEN c > 999999 THEN q r;` | Válida | Válida | Tres reglas en líneas separadas. |
| L07 | Límite | `WHEN sensor_1234567890 != FALSE THEN activar dispositivo_1234567890;` | Válida | Válida | Identificadores largos con números y guiones bajos. |
| L08 | Límite | `""` | Inválida | Inválida | Entrada vacía: límite inferior del lenguaje. |
| L09 | Límite | ` \t\r\n ` | Inválida | Inválida | Solo espacios: el lexer produce únicamente EOF. |
| E01 | Extensión | `WHEN temperatura > 30 THEN encender ventilador, abrir puerta;` | Válida | Válida | Dos acciones separadas por coma. |
| E02 | Extensión | `WHEN luz < 100 THEN abrir puerta, encender lampara, cerrar ventana;` | Válida | Válida | Rutina de tres acciones en orden. |
| E03 | Extensión | `WHEN movimiento == TRUE THEN activar alarma, notificar dueno;` | Válida | Válida | Alarma y notificación en una misma regla. |
| E04 | Extensión | `WHEN nivel_alimento < 20 OR nivel_agua <= 30 THEN activar comedero, activar bebedero;` | Válida | Válida | Dos actuadores activados por una condición con OR. |
| E05 | Extensión | `WHEN temperatura > 30 THEN encender ventilador, abrir puerta; WHEN luz < 20 THEN cerrar puerta, apagar lampara;` | Válida | Válida | Dos reglas, cada una con dos acciones. |
| E06 | Extensión | `WHEN temperatura > 30 THEN encender ventilador,;` | Inválida | Inválida | Coma final sin una acción que la siga. |
| E07 | Extensión | `WHEN temperatura > 30 THEN , encender ventilador;` | Inválida | Inválida | Coma inicial antes de la primera acción. |
| E08 | Extensión | `WHEN temperatura > 30 THEN encender ventilador abrir puerta;` | Inválida | Inválida | Falta la coma entre dos acciones. |
| E09 | Extensión | `WHEN temperatura > 30 THEN encender ventilador,, abrir puerta;` | Inválida | Inválida | Dos comas consecutivas sin acción entre ellas. |
| E10 | Extensión | `WHEN temperatura > 30 THEN encender ventilador, abrir;` | Inválida | Inválida | La acción después de la coma no tiene dispositivo. |

## Cómo interpretar los resultados

- **Válida:** el parser construye el AST sin lanzar `ErrorSintactico`.
- **Inválida:** el parser lanza `ErrorSintactico` al analizar la entrada.
- Además de la validez, se comprueba que el AST tenga la cantidad de reglas y
  acciones indicada en la observación de cada caso.

Los casos `L08` y `L09` representan el límite inferior del lenguaje: una entrada
vacía y una entrada con solo espacios en blanco. Ambos deben ser rechazados
porque el programa exige al menos una regla.

El script informa el estado individual de cada caso, muestra el detalle de los
fallos y devuelve código de salida `0` solo cuando todos coinciden con el
resultado esperado. La opción `--tabla` regenera esta tabla en formato
Markdown a partir de los mismos casos:

```powershell
python tests/test_parser.py --tabla
```
