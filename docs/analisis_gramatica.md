# Análisis de la gramática libre de contexto

## 1. Recursión por la izquierda
La gramática original no presenta recursión por la izquierda (ni directa ni indirecta). Las producciones recursivas (`cond_or_prima`, `cond_and_prima` y `acciones_prima`) utilizan recursión por la derecha, lo cual es totalmente compatible con el análisis predictivo LL(1).

## 2. Factorización por la izquierda
La producción `lista_reglas` en la versión base presenta un conflicto FIRST-FIRST:
`lista_reglas ::= regla lista_reglas | regla`

Ambas alternativas comienzan con el no terminal `regla`, cuyo FIRST es `{ WHEN }`. 
Para solucionarlo, extrajimos el factor común (`regla`) e introdujimos un nuevo no terminal `lista_reglas_prima`:
`lista_reglas ::= regla lista_reglas_prima`
`lista_reglas_prima ::= regla lista_reglas_prima | epsilon`

## 3. Análisis de ambigüedad
La gramática no es ambigua. La precedencia de los operadores lógicos está forzada estructuralmente mediante niveles de derivación estandarizados (NOT en factor, AND en cond_and, OR en cond_or). La asociatividad está garantizada por el uso de recursión por la derecha.

## 4. Gramática final transformada para LL(1)
```text
programa ::= lista_reglas EOF
lista_reglas ::= regla lista_reglas_prima
lista_reglas_prima ::= regla lista_reglas_prima | epsilon
regla ::= WHEN condicion THEN acciones PUNTO_COMA
condicion ::= cond_or
cond_or ::= cond_and cond_or_prima
cond_or_prima ::= OR cond_and cond_or_prima | epsilon
cond_and ::= factor cond_and_prima
cond_and_prima ::= AND factor cond_and_prima | epsilon
factor ::= NOT comparacion | comparacion
comparacion ::= ID OP_REL valor
valor ::= NUM | TRUE | FALSE
acciones ::= accion acciones_prima
acciones_prima ::= COMA accion acciones_prima | epsilon
accion ::= ID ID