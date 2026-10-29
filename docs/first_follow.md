# Conjuntos FIRST y FOLLOW

Los cálculos se basan en la gramática factorizada, que mantiene la recursión por la derecha y resuelve el conflicto FIRST-FIRST de `lista_reglas`.

## 1. Conjuntos FIRST
El conjunto FIRST incluye los terminales con los que puede iniciar una cadena derivada.
* `FIRST(valor)` = `{ NUM, TRUE, FALSE }`
* `FIRST(comparacion)` = `{ ID }`
* `FIRST(factor)` = `{ NOT, ID }`
* `FIRST(cond_and_prima)` = `{ AND, epsilon }`
* `FIRST(cond_and)` = `{ NOT, ID }`
* `FIRST(cond_or_prima)` = `{ OR, epsilon }`
* `FIRST(cond_or)` = `{ NOT, ID }`
* `FIRST(condicion)` = `{ NOT, ID }`
* `FIRST(accion)` = `{ ID }`
* `FIRST(acciones_prima)` = `{ COMA, epsilon }`
* `FIRST(acciones)` = `{ ID }`
* `FIRST(regla)` = `{ WHEN }`
* `FIRST(lista_reglas_prima)` = `{ WHEN, epsilon }`
* `FIRST(lista_reglas)` = `{ WHEN }`
* `FIRST(programa)` = `{ WHEN }`

## 2. Conjuntos FOLLOW
El conjunto FOLLOW incluye los terminales que pueden aparecer a la derecha de un no terminal.
* `FOLLOW(programa)` = `{ EOF }` (fin de entrada)
* `FOLLOW(lista_reglas)` = `{ EOF }`
* `FOLLOW(lista_reglas_prima)` = `{ EOF }`
* `FOLLOW(regla)` = `{ WHEN, EOF }`
* `FOLLOW(condicion)` = `{ THEN }`
* `FOLLOW(cond_or)` = `{ THEN }`
* `FOLLOW(cond_or_prima)` = `{ THEN }`
* `FOLLOW(cond_and)` = `{ OR, THEN }`
* `FOLLOW(cond_and_prima)` = `{ OR, THEN }`
* `FOLLOW(factor)` = `{ AND, OR, THEN }`
* `FOLLOW(comparacion)` = `{ AND, OR, THEN }`
* `FOLLOW(valor)` = `{ AND, OR, THEN }`
* `FOLLOW(acciones)` = `{ PUNTO_COMA }`
* `FOLLOW(acciones_prima)` = `{ PUNTO_COMA }`
* `FOLLOW(accion)` = `{ COMA, PUNTO_COMA }`
