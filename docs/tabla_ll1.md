# Tabla Predictiva LL(1)

A partir de los conjuntos FIRST y FOLLOW calculados previamente, se construye la tabla de análisis predictivo mapeando cada No Terminal y Token hacia su respectiva regla de producción[cite: 5]. 

## 1. Tabla de parsing

| No Terminal | Token (Terminal) | Producción a aplicar |
| :--- | :--- | :--- |
| **programa** | `WHEN` | `programa ::= lista_reglas EOF` |
| **lista_reglas** | `WHEN` | `lista_reglas ::= regla lista_reglas_prima` |
| **lista_reglas_prima**| `WHEN` | `lista_reglas_prima ::= regla lista_reglas_prima` |
| **lista_reglas_prima**| `EOF` | `lista_reglas_prima ::= epsilon` |
| **regla** | `WHEN` | `regla ::= WHEN condicion THEN acciones PUNTO_COMA` |
| **condicion** | `NOT`, `ID` | `condicion ::= cond_or` |
| **cond_or** | `NOT`, `ID` | `cond_or ::= cond_and cond_or_prima` |
| **cond_or_prima** | `OR` | `cond_or_prima ::= OR cond_and cond_or_prima` |
| **cond_or_prima** | `THEN` | `cond_or_prima ::= epsilon` |
| **cond_and** | `NOT`, `ID` | `cond_and ::= factor cond_and_prima` |
| **cond_and_prima** | `AND` | `cond_and_prima ::= AND factor cond_and_prima` |
| **cond_and_prima** | `OR`, `THEN` | `cond_and_prima ::= epsilon` |
| **factor** | `NOT` | `factor ::= NOT comparacion` |
| **factor** | `ID` | `factor ::= comparacion` |
| **comparacion** | `ID` | `comparacion ::= ID OP_REL valor` |
| **valor** | `NUM` | `valor ::= NUM` |
| **valor** | `TRUE` | `valor ::= TRUE` |
| **valor** | `FALSE` | `valor ::= FALSE` |
| **acciones** | `ID` | `acciones ::= accion acciones_prima` |
| **acciones_prima** | `COMA` | `acciones_prima ::= COMA accion acciones_prima` |
| **acciones_prima** | `PUNTO_COMA` | `acciones_prima ::= epsilon` |
| **accion** | `ID` | `accion ::= ID ID` |

Las celdas vacías (intersecciones no listadas) corresponden a errores sintácticos.

## 2. Validación de la propiedad LL(1)

La gramática es estrictamente LL(1)[cite: 5]. Tras la factorización por la izquierda aplicada en la issue anterior, no existen conflictos en la tabla; ninguna combinación de No Terminal y Token genera más de una producción posible[cite: 5]. El parser siempre podrá predecir la derivación correcta basándose en un único token de anticipación (lookahead).