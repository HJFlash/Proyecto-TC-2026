"""Matriz automatizada de casos de prueba para el parser del DSL."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Sequence
from unittest import TestCase

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.parser import ErrorSintactico, parsear


@dataclass(frozen=True)
class Caso:
    identificador: str
    categoria: str
    entrada: str
    esperado: bool
    observacion: str
    reglas: int | None = None
    acciones: int | None = None


CASOS: tuple[Caso, ...] = (
    # ------------------------------------------------------------------
    # Entradas válidas
    # ------------------------------------------------------------------
    Caso("V01", "Válida", "WHEN luz < 100 THEN abrir puerta;",
         True, "Regla mínima con comparación numérica.", 1, 1),
    Caso("V02", "Válida", "WHEN temperatura > 30 THEN encender ventilador;",
         True, "Operador mayor que y una acción.", 1, 1),
    Caso("V03", "Válida", "WHEN humedad >= 80 THEN encender ventilador;",
         True, "Operador mayor o igual.", 1, 1),
    Caso("V04", "Válida", "WHEN nivel_agua <= 30 THEN activar bebedero;",
         True, "Identificador con guion bajo y operador menor o igual.", 1, 1),
    Caso("V05", "Válida", "WHEN ventilacion != TRUE THEN activar alarma;",
         True, "Comparación booleana con !=.", 1, 1),
    Caso("V06", "Válida", "WHEN NOT alarma_activa == FALSE THEN notificar dueno;",
         True, "Negación de una comparación.", 1, 1),
    Caso("V07", "Válida",
         "WHEN luz < 100 AND puerta_cerrada == TRUE THEN abrir puerta;",
         True, "Condición compuesta con AND.", 1, 1),
    Caso("V08", "Válida",
         "WHEN temperatura > 30 OR ventilacion == FALSE THEN "
         "encender ventilador, abrir puerta;",
         True, "OR y dos acciones de la extensión creativa.", 1, 2),
    Caso("V09", "Válida",
         "WHEN movimiento == TRUE THEN activar alarma, notificar dueno, "
         "cerrar puerta;",
         True, "Tres acciones ordenadas separadas por comas.", 1, 3),
    Caso("V10", "Válida",
         "WHEN nivel_alimento < 20 THEN activar comedero; "
         "WHEN nivel_agua <= 30 THEN activar bebedero;",
         True, "Programa con dos reglas.", 2, 2),
    Caso("V11", "Válida",
         "when LUZ < 100 then abrir puerta;",
         True, "Palabras reservadas sin distinguir mayúsculas.", 1, 1),
    Caso("V12", "Válida",
         "WHEN temperatura == 000000 THEN encender calefactor;",
         True, "Número con ceros y longitud mayor.", 1, 1),
    Caso("V13", "Válida",
         "WHEN humedad >= 80 AND ventilacion != TRUE OR "
         "movimiento == FALSE THEN activar alarma, notificar dueno;",
         True, "Precedencia AND sobre OR y acciones múltiples.", 1, 2),
    # ------------------------------------------------------------------
    # Entradas inválidas
    # ------------------------------------------------------------------
    Caso("I01", "Inválida", "WHEN luz < 100 THEN abrir puerta", False,
         "Falta el punto y coma final."),
    Caso("I02", "Inválida", "WHEN luz < 100 abrir puerta;", False,
         "Falta la palabra reservada THEN."),
    Caso("I03", "Inválida", "WHEN luz < THEN abrir puerta;", False,
         "Falta el valor de la comparación."),
    Caso("I04", "Inválida", "WHEN THEN abrir puerta;", False,
         "Falta la condición."),
    Caso("I05", "Inválida", "WHEN luz < 100 THEN abrir;", False,
         "La acción no tiene dispositivo."),
    Caso("I06", "Inválida", "WHEN luz < 100 THEN , abrir puerta;", False,
         "La coma no puede iniciar la lista de acciones."),
    Caso("I07", "Inválida", "WHEN luz < 100 THEN abrir puerta,;", False,
         "La coma final debe ir seguida de otra acción."),
    Caso("I08", "Inválida",
         "WHEN luz < 100 THEN abrir puerta,, encender lampara;",
         False, "No se permiten comas consecutivas."),
    Caso("I09", "Inválida",
         "WHEN luz < 100 THEN abrir puerta encender lampara;",
         False, "Las acciones deben separarse con coma."),
    Caso("I10", "Inválida",
         "WHEN luz < 100 THEN abrir puerta @;",
         False, "El símbolo @ no pertenece al lenguaje."),
    Caso("I11", "Inválida",
         "WHEN luz < 100 THEN (abrir puerta);",
         False, "Los paréntesis no están soportados."),
    Caso("I12", "Inválida",
         "WHEN luz = 100 THEN abrir puerta;",
         False, "La igualdad requiere ==."),
    Caso("I13", "Inválida",
         "WHEN luz < -1 THEN abrir puerta;",
         False, "No se admiten números negativos."),
    Caso("I14", "Inválida",
         "WHEN luz < 10.5 THEN abrir puerta;",
         False, "No se admiten números decimales."),
    # ------------------------------------------------------------------
    # Casos límite
    # ------------------------------------------------------------------
    Caso("L01", "Límite",
         "WHEN luz < 100 THEN abrir puerta;",
         True, "Una sola regla y una sola acción.", 1, 1),
    Caso("L02", "Límite",
         " \t WHEN luz < 100 \n THEN \t abrir \t puerta , "
         "encender lampara ; \r\n",
         True, "Espacios, tabulaciones y saltos de línea.", 1, 2),
    Caso("L03", "Límite",
         "WHEN sensor_1 < 1 AND sensor_2 < 2 AND sensor_3 < 3 AND "
         "sensor_4 < 4 AND sensor_5 < 5 AND sensor_6 < 6 AND "
         "sensor_7 < 7 AND sensor_8 < 8 AND sensor_9 < 9 "
         "THEN activar alarma;",
         True, "Cadena profunda de nueve comparaciones con AND.", 1, 1),
    Caso("L04", "Límite",
         "WHEN sensor_1 < 1 OR sensor_2 < 2 OR sensor_3 < 3 OR "
         "sensor_4 < 4 OR sensor_5 < 5 OR sensor_6 < 6 "
         "THEN activar alarma;",
         True, "Cadena profunda de comparaciones con OR.", 1, 1),
    Caso("L05", "Límite",
         "WHEN movimiento == TRUE THEN activar alarma, notificar dueno, "
         "encender lampara, cerrar puerta, activar camara;",
         True, "Rutina de cinco acciones.", 1, 5),
    Caso("L06", "Límite",
         "WHEN a == TRUE THEN x y;\n"
         "WHEN b == FALSE THEN z w;\n"
         "WHEN c > 999999 THEN q r;",
         True, "Tres reglas en líneas separadas.", 3, 3),
    Caso("L07", "Límite",
         "WHEN sensor_1234567890 != FALSE THEN "
         "activar dispositivo_1234567890;",
         True, "Identificadores largos con números y guiones bajos.", 1, 1),
    Caso("L08", "Límite", "", False,
         "Entrada vacía: límite inferior del lenguaje."),
    Caso("L09", "Límite", " \t\r\n ", False,
         "Solo espacios: el lexer produce únicamente EOF."),
    # ------------------------------------------------------------------
    # Extensión creativa: múltiples acciones por regla (5 válidas)
    # ------------------------------------------------------------------
    Caso("E01", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador, abrir puerta;",
         True, "Dos acciones separadas por coma.", 1, 2),
    Caso("E02", "Extensión",
         "WHEN luz < 100 THEN abrir puerta, encender lampara, cerrar ventana;",
         True, "Rutina de tres acciones en orden.", 1, 3),
    Caso("E03", "Extensión",
         "WHEN movimiento == TRUE THEN activar alarma, notificar dueno;",
         True, "Alarma y notificación en una misma regla.", 1, 2),
    Caso("E04", "Extensión",
         "WHEN nivel_alimento < 20 OR nivel_agua <= 30 THEN "
         "activar comedero, activar bebedero;",
         True, "Dos actuadores activados por una condición con OR.", 1, 2),
    Caso("E05", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador, abrir puerta; "
         "WHEN luz < 20 THEN cerrar puerta, apagar lampara;",
         True, "Dos reglas, cada una con dos acciones.", 2, 4),
    # ------------------------------------------------------------------
    # Extensión creativa: errores de la lista de acciones (5 inválidas)
    # ------------------------------------------------------------------
    Caso("E06", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador,;",
         False, "Coma final sin una acción que la siga."),
    Caso("E07", "Extensión",
         "WHEN temperatura > 30 THEN , encender ventilador;",
         False, "Coma inicial antes de la primera acción."),
    Caso("E08", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador abrir puerta;",
         False, "Falta la coma entre dos acciones."),
    Caso("E09", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador,, abrir puerta;",
         False, "Dos comas consecutivas sin acción entre ellas."),
    Caso("E10", "Extensión",
         "WHEN temperatura > 30 THEN encender ventilador, abrir;",
         False, "La acción después de la coma no tiene dispositivo."),
)


def ejecutar_caso(caso: Caso) -> tuple[bool, str, str]:
    """Ejecuta un caso y devuelve éxito, resultado obtenido y detalle."""
    try:
        ast = parsear(caso.entrada)
    except ErrorSintactico as error:
        if caso.esperado:
            return False, "Inválida", f"se esperaba válida: {error}"
        return True, "Inválida", ""

    if not caso.esperado:
        return False, "Válida", "se esperaba una entrada inválida"

    if caso.reglas is not None and len(ast.reglas) != caso.reglas:
        return (
            False,
            "Válida",
            f"se esperaban {caso.reglas} reglas y se obtuvieron "
            f"{len(ast.reglas)}",
        )

    cantidad_acciones = sum(len(regla.acciones) for regla in ast.reglas)
    if caso.acciones is not None and cantidad_acciones != caso.acciones:
        return (
            False,
            "Válida",
            f"se esperaban {caso.acciones} acciones y se obtuvieron "
            f"{cantidad_acciones}",
        )

    return True, "Válida", ""


class TestMatrizParser(TestCase):
    """Ejecuta la matriz completa cuando se usa unittest."""

    def test_matriz_completa(self) -> None:
        for caso in CASOS:
            with self.subTest(caso=caso.identificador):
                correcto, obtenido, detalle = ejecutar_caso(caso)
                esperado = "Válida" if caso.esperado else "Inválida"
                mensaje = (
                    f"{caso.identificador}: se esperaba {esperado} y se obtuvo "
                    f"{obtenido}"
                )
                if detalle:
                    mensaje = f"{mensaje}: {detalle}"
                self.assertTrue(correcto, mensaje)


def _celda_markdown(texto: str) -> str:
    """Escapa un texto para que pueda usarse dentro de una tabla Markdown."""
    return (
        texto.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


ENCABEZADO = r"""# Casos de prueba del parser

La matriz contiene 46 casos: 25 entradas válidas y 21 inválidas, organizadas en
13 casos `V`, 14 casos `I`, 9 casos límite `L` y 10 casos de la extensión
creativa `E`. Los 10 casos de extensión incluyen 5 entradas válidas y 5
inválidas. El resultado obtenido se verifica automáticamente con:

```bash
python tests/test_parser.py
```

En las entradas válidas también se comprueba la cantidad de reglas y acciones
generadas en el AST. Las palabras reservadas pueden escribirse en minúsculas,
pero los identificadores conservan su distinción entre mayúsculas y minúsculas.
Las tabulaciones, retornos de carro y saltos de línea se muestran escapados
como `\t`, `\r` y `\n` para que la entrada sea legible en la tabla.
"""

PIE = r"""## Cómo interpretar los resultados

- **Válida:** el parser construye el AST sin lanzar `ErrorSintactico`.
- **Inválida:** el parser lanza `ErrorSintactico` al analizar la entrada.
- Además de la validez, se comprueba que el AST tenga la cantidad de reglas y
  acciones indicada en la observación de cada caso.

Los casos `L08` y `L09` representan el límite inferior del lenguaje: una entrada
vacía y una entrada con solo espacios en blanco. Ambos deben ser rechazados
porque el programa exige al menos una regla.

El script informa el estado individual de cada caso, muestra el detalle de los
fallos y devuelve código de salida `0` solo cuando todos coinciden con el
resultado esperado. La opción `--tabla` genera este documento Markdown completo
a partir de los mismos casos:

```bash
python tests/test_parser.py --tabla tests/casos_prueba.md
```
"""

USO = "Uso: python tests/test_parser.py [--tabla [ARCHIVO]]"


def generar_tabla_markdown() -> str:
    """Genera la tabla Markdown a partir de los mismos casos ejecutados."""
    lineas = [
        "| ID | Categoría | Entrada | Resultado esperado | "
        "Resultado obtenido | Observación |",
        "|---|---|---|---|---|---|",
    ]
    for caso in CASOS:
        _, obtenido, _ = ejecutar_caso(caso)
        entrada = _celda_markdown(caso.entrada) or '""'
        esperado = "Válida" if caso.esperado else "Inválida"
        lineas.append(
            f"| {caso.identificador} | {caso.categoria} | `{entrada}` | "
            f"{esperado} | {obtenido} | {caso.observacion} |"
        )
    return "\n".join(lineas)


def generar_documento_markdown() -> str:
    """Genera el documento completo con encabezado, tabla y pie."""
    return f"{ENCABEZADO}\n{generar_tabla_markdown()}\n\n{PIE}"


def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta los casos o genera el documento Markdown."""
    argumentos = list(sys.argv[1:] if argv is None else argv)

    if argumentos:
        if argumentos[0] != "--tabla" or len(argumentos) > 2:
            print(USO, file=sys.stderr)
            return 2

        documento = generar_documento_markdown()
        if len(argumentos) == 1:
            print(documento, end="")
            return 0

        destino = Path(argumentos[1])
        try:
            # newline="\n" mantiene LF también al regenerar desde Windows.
            destino.write_text(documento, encoding="utf-8", newline="\n")
        except OSError as error:
            print(f"No se pudo escribir {destino}: {error}", file=sys.stderr)
            return 1
        return 0

    print("ID   Categoría   Esperado  Obtenido  Estado")
    print("---  ----------  --------  --------  ------")

    fallos: list[tuple[Caso, str]] = []
    for caso in CASOS:
        correcto, obtenido, detalle = ejecutar_caso(caso)
        esperado = "Válida" if caso.esperado else "Inválida"
        estado = "OK" if correcto else "FALLO"
        print(f"{caso.identificador:<4} {caso.categoria:<10} "
              f"{esperado:<8}  {obtenido:<8}  {estado}")
        if not correcto:
            fallos.append((caso, detalle))

    if fallos:
        print("\nDetalle de los fallos:")
        for caso, detalle in fallos:
            print(f"- {caso.identificador}: {detalle}")

    print(f"\n{len(CASOS)} casos ejecutados; {len(fallos)} fallos.")
    return int(bool(fallos))


if __name__ == "__main__":
    raise SystemExit(main())
