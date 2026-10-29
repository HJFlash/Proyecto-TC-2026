"""Analizador sintáctico predictivo LL(1) del DSL del gallinero con generación de AST.

El parser se implementa a mano por descenso recursivo, sin generadores.
Construye el Árbol de Sintaxis Abstracta (AST) de forma concurrente con el análisis.
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence
import sys
from typing import NoReturn

if __package__:
    from .lexer import Token, analizar
    from .arbol import (Programa, Regla, Comparacion, Accion,
                        OperacionBinaria, OperacionUnaria)
    from .errores import ErrorSintactico, describir_tipo
else:
    from lexer import Token, analizar
    from arbol import (Programa, Regla, Comparacion, Accion,
                       OperacionBinaria, OperacionUnaria)
    from errores import ErrorSintactico, describir_tipo

__all__ = [
    "AnalizadorSintactico",
    "ErrorSintactico",
    "Parser",
    "parsear",
    "parsear_tokens",
    "validar",
]

class Parser:
    """Parser LL(1) por descenso recursivo que construye el AST."""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.tokens = list(tokens)
        if not self.tokens or self.tokens[-1].tipo != "EOF":
            raise ValueError("La secuencia de tokens debe terminar con EOF")
        self.posicion = 0

    @property
    def actual(self) -> Token:
        return self.tokens[self.posicion]

    def avanzar(self) -> Token:
        token = self.actual
        self.posicion += 1
        return token

    def consumir(
        self,
        tipo: str,
        esperado: str | None = None,
        *,
        sugerencia: str | None = None,
    ) -> Token:
        """Consume un token del tipo esperado o reporta un error sintáctico."""
        if self.actual.tipo != tipo:
            self.error(
                esperado if esperado is not None else describir_tipo(tipo),
                sugerencia=sugerencia,
            )
        return self.avanzar()

    def error(self, esperado: str, *, sugerencia: str | None = None) -> NoReturn:
        """Lanza un error sintáctico indicando lo que se esperaba."""
        raise ErrorSintactico(self.actual, esperado, sugerencia=sugerencia)

    def parse(self) -> Programa:
        """Valida la entrada completa y devuelve el nodo raíz del AST (Programa)."""
        ast = self.programa()
        if self.posicion != len(self.tokens):
            raise ValueError("La secuencia contiene tokens después de EOF")
        return ast

    # ------------------------------------------------------------------
    # Métodos que devuelven nodos del AST
    # ------------------------------------------------------------------

    def programa(self) -> Programa:
        """``programa ::= lista_reglas EOF``."""
        if self.actual.tipo == "EOF":
            raise ErrorSintactico.entrada_vacia(self.actual)
        reglas = self.lista_reglas()
        self.consumir("EOF")
        return Programa(reglas)

    def lista_reglas(self) -> list[Regla]:
        r = self.regla()
        resto = self.lista_reglas_prima()
        return [r] + resto

    def lista_reglas_prima(self) -> list[Regla]:
        if self.actual.tipo == "WHEN":
            r = self.regla()
            resto = self.lista_reglas_prima()
            return [r] + resto
        elif self.actual.tipo != "EOF":
            self.error(
                "la palabra reservada WHEN para comenzar otra regla "
                "o el final de la entrada"
            )
        return []

    def regla(self) -> Regla:
        """``regla ::= WHEN condicion THEN acciones PUNTO_COMA``."""
        self.consumir("WHEN")
        cond = self.condicion()

        sugerencia_then = None
        if self.actual.tipo == "ID":
            sugerencia_then = (
                "Si la condición continúa, falta un operador AND u OR."
            )
        self.consumir(
            "THEN",
            "la palabra reservada THEN después de la condición",
            sugerencia=sugerencia_then,
        )

        accs = self.acciones()

        sugerencia_pyc = None
        if self.actual.tipo == "ID":
            sugerencia_pyc = (
                "Si hay otra acción, sepárela con una coma (',')."
            )
        self.consumir(
            "PUNTO_COMA",
            "el punto y coma ';' para terminar la regla",
            sugerencia=sugerencia_pyc,
        )
        return Regla(cond, accs)

    def condicion(self) -> OperacionBinaria | OperacionUnaria | Comparacion:
        return self.cond_or()

    def cond_or(self) -> OperacionBinaria | OperacionUnaria | Comparacion:
        izq = self.cond_and()
        return self.cond_or_prima(izq)

    def cond_or_prima(
        self,
        izq: OperacionBinaria | OperacionUnaria | Comparacion,
    ) -> OperacionBinaria | OperacionUnaria | Comparacion:
        if self.actual.tipo == "OR":
            op = self.avanzar().lexema
            der = self.cond_and(contexto="después de OR")
            nuevo_nodo = OperacionBinaria(op, izq, der)
            return self.cond_or_prima(nuevo_nodo)
        return izq

    def cond_and(
        self,
        contexto: str | None = None,
    ) -> OperacionBinaria | OperacionUnaria | Comparacion:
        izq = self.factor(contexto)
        return self.cond_and_prima(izq)

    def cond_and_prima(
        self,
        izq: OperacionBinaria | OperacionUnaria | Comparacion,
    ) -> OperacionBinaria | OperacionUnaria | Comparacion:
        if self.actual.tipo == "AND":
            op = self.avanzar().lexema
            der = self.factor(contexto="después de AND")
            nuevo_nodo = OperacionBinaria(op, izq, der)
            return self.cond_and_prima(nuevo_nodo)
        return izq

    def factor(
        self,
        contexto: str | None = None,
    ) -> OperacionUnaria | Comparacion:
        if self.actual.tipo == "NOT":
            op = self.avanzar().lexema
            comp = self.comparacion(contexto="después de NOT")
            return OperacionUnaria(op, comp)
        elif self.actual.tipo == "ID":
            return self.comparacion(contexto)
        else:
            esperado = "el inicio de una comparación (NOT o un identificador)"
            if contexto:
                esperado = f"una comparación {contexto}"
            self.error(esperado)

    def comparacion(
        self,
        contexto: str | None = None,
    ) -> Comparacion:
        esperado_id = "un identificador (sensor)"
        if contexto:
            esperado_id = f"un identificador (sensor) {contexto}"

        id_izq = self.consumir("ID", esperado_id).lexema
        op_rel = self.consumir(
            "OP_REL",
            "un operador relacional (>, <, >=, <=, ==, !=)",
        ).lexema
        valor_der = self.valor(op_rel)
        return Comparacion(id_izq, op_rel, valor_der)

    def valor(self, operador: str) -> str:
        if self.actual.tipo in {"NUM", "TRUE", "FALSE"}:
            return self.avanzar().lexema
        else:
            self.error(
                f"un valor (número, TRUE o FALSE) después del operador {operador!r}"
            )

    def acciones(self) -> list[Accion]:
        acc = self.accion()
        resto = self.acciones_prima()
        return [acc] + resto

    def acciones_prima(self) -> list[Accion]:
        if self.actual.tipo == "COMA":
            self.avanzar()
            acc = self.accion()
            resto = self.acciones_prima()
            return [acc] + resto
        return []

    def accion(self) -> Accion:
        verbo = self.consumir(
            "ID",
            "el verbo de la acción (un identificador)",
        ).lexema
        dispositivo = self.consumir(
            "ID",
            f"el dispositivo (un identificador) después del verbo {verbo!r}",
        ).lexema
        return Accion(verbo, dispositivo)

AnalizadorSintactico = Parser


def parsear_tokens(tokens: Iterable[Token]) -> Programa:
    return Parser(tokens).parse()


def parsear(texto: str) -> Programa:
    return parsear_tokens(analizar(texto))


def validar(texto: str) -> bool:
    try:
        parsear(texto)
        return True
    except ErrorSintactico:
        return False

def main(argv: Sequence[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argv is None else argv)
    if not argumentos:
        print('Uso: python src/parser.py "<programa>"', file=sys.stderr)
        return 2

    try:
        ast = parsear(" ".join(argumentos))
    except ErrorSintactico as error:
        print(error, file=sys.stderr)
        return 1

    print("Entrada sintácticamente válida. Árbol generado:")
    ast.imprimir()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())