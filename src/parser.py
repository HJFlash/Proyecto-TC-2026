"""Analizador sintáctico predictivo LL(1) del DSL del gallinero.

El parser se implementa a mano por descenso recursivo, sin generadores.
Cada método de :class:`Parser` corresponde a un no terminal de la gramática
factorizada usada en la tabla LL(1):

``programa ::= lista_reglas EOF``
``lista_reglas ::= regla lista_reglas_prima``
``lista_reglas_prima ::= regla lista_reglas_prima | epsilon``
``regla ::= WHEN condicion THEN acciones PUNTO_COMA``
``condicion ::= cond_or``
``cond_or ::= cond_and cond_or_prima``
``cond_or_prima ::= OR cond_and cond_or_prima | epsilon``
``cond_and ::= factor cond_and_prima``
``cond_and_prima ::= AND factor cond_and_prima | epsilon``
``factor ::= NOT comparacion | comparacion``
``comparacion ::= ID OP_REL valor``
``valor ::= NUM | TRUE | FALSE``
``acciones ::= accion acciones_prima``
``acciones_prima ::= COMA accion acciones_prima | epsilon``
``accion ::= ID ID``

Todas las decisiones se toman con un único token de anticipación, por lo
que el reconocimiento es estrictamente LL(1).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
import sys
from typing import NoReturn

if __package__:
    from .lexer import Token, analizar
else:  # permite ejecutar el archivo directamente: python src/parser.py "..."
    from lexer import Token, analizar

__all__ = [
    "AnalizadorSintactico",
    "ErrorSintactico",
    "Parser",
    "parsear",
    "parsear_tokens",
    "validar",
]


class ErrorSintactico(Exception):
    """Error de sintaxis localizado en un token de la entrada."""

    def __init__(self, token: Token, esperado: str) -> None:
        self.token = token
        self.esperado = esperado

        if token.tipo == "EOF":
            encontrado = "fin de entrada"
        elif token.tipo == "ERROR":
            encontrado = f"símbolo no reconocido {token.lexema!r}"
        else:
            encontrado = f"{token.tipo} {token.lexema!r}"

        super().__init__(
            f"Error sintáctico en línea {token.linea}, columna {token.columna}: "
            f"se esperaba {esperado}; se encontró {encontrado}."
        )


class Parser:
    """Parser LL(1) por descenso recursivo para el DSL del gallinero."""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.tokens = list(tokens)
        if not self.tokens or self.tokens[-1].tipo != "EOF":
            raise ValueError("La secuencia de tokens debe terminar con EOF")
        self.posicion = 0

    @property
    def actual(self) -> Token:
        """Token que se encuentra bajo el cursor (lookahead)."""
        return self.tokens[self.posicion]

    def avanzar(self) -> Token:
        """Consume y devuelve el token actual."""
        token = self.actual
        self.posicion += 1
        return token

    def consumir(self, tipo: str) -> Token:
        """Consume un token del tipo esperado o reporta un error sintáctico."""
        if self.actual.tipo != tipo:
            self.error(tipo)
        return self.avanzar()

    def error(self, esperado: str) -> NoReturn:
        """Lanza un error sintáctico indicando lo que se esperaba."""
        raise ErrorSintactico(self.actual, esperado)

    def parse(self) -> bool:
        """Valida la entrada completa y devuelve ``True`` si es correcta."""
        self.programa()
        if self.posicion != len(self.tokens):
            raise ValueError("La secuencia contiene tokens después de EOF")
        return True

    # ------------------------------------------------------------------
    # Un método por cada no terminal de la gramática.
    # ------------------------------------------------------------------

    def programa(self) -> None:
        """``programa ::= lista_reglas EOF``."""
        self.lista_reglas()
        self.consumir("EOF")

    def lista_reglas(self) -> None:
        """``lista_reglas ::= regla lista_reglas_prima``."""
        self.regla()
        self.lista_reglas_prima()

    def lista_reglas_prima(self) -> None:
        """``lista_reglas_prima ::= regla lista_reglas_prima | epsilon``.

        LL(1): ``WHEN`` inicia otra regla; ``EOF`` cierra la lista.
        """
        if self.actual.tipo == "WHEN":
            self.regla()
            self.lista_reglas_prima()
        elif self.actual.tipo != "EOF":
            self.error("WHEN o EOF")

    def regla(self) -> None:
        """``regla ::= WHEN condicion THEN acciones PUNTO_COMA``."""
        self.consumir("WHEN")
        self.condicion()
        self.consumir("THEN")
        self.acciones()
        self.consumir("PUNTO_COMA")

    def condicion(self) -> None:
        """``condicion ::= cond_or``."""
        self.cond_or()

    def cond_or(self) -> None:
        """``cond_or ::= cond_and cond_or_prima``."""
        self.cond_and()
        self.cond_or_prima()

    def cond_or_prima(self) -> None:
        """``cond_or_prima ::= OR cond_and cond_or_prima | epsilon``.

        LL(1): ``OR`` repite la disyunción; ``THEN`` (FOLLOW) aplica epsilon.
        """
        if self.actual.tipo == "OR":
            self.avanzar()
            self.cond_and()
            self.cond_or_prima()
        elif self.actual.tipo != "THEN":
            self.error("OR o THEN")

    def cond_and(self) -> None:
        """``cond_and ::= factor cond_and_prima``."""
        self.factor()
        self.cond_and_prima()

    def cond_and_prima(self) -> None:
        """``cond_and_prima ::= AND factor cond_and_prima | epsilon``.

        LL(1): ``AND`` repite la conjunción; ``OR`` o ``THEN`` (FOLLOW)
        aplican epsilon.
        """
        if self.actual.tipo == "AND":
            self.avanzar()
            self.factor()
            self.cond_and_prima()
        elif self.actual.tipo not in {"OR", "THEN"}:
            self.error("AND, OR o THEN")

    def factor(self) -> None:
        """``factor ::= NOT comparacion | comparacion``.

        LL(1): ``NOT`` introduce una comparación negada; ``ID`` inicia una
        comparación sin negación.
        """
        if self.actual.tipo == "NOT":
            self.avanzar()
            self.comparacion()
        elif self.actual.tipo == "ID":
            self.comparacion()
        else:
            self.error("NOT o ID")

    def comparacion(self) -> None:
        """``comparacion ::= ID OP_REL valor``."""
        self.consumir("ID")
        self.consumir("OP_REL")
        self.valor()

    def valor(self) -> None:
        """``valor ::= NUM | TRUE | FALSE``."""
        if self.actual.tipo in {"NUM", "TRUE", "FALSE"}:
            self.avanzar()
        else:
            self.error("NUM, TRUE o FALSE")

    def acciones(self) -> None:
        """``acciones ::= accion acciones_prima``."""
        self.accion()
        self.acciones_prima()

    def acciones_prima(self) -> None:
        """``acciones_prima ::= COMA accion acciones_prima | epsilon``.

        LL(1): ``COMA`` agrega otra acción; ``PUNTO_COMA`` (FOLLOW) aplica
        epsilon.
        """
        if self.actual.tipo == "COMA":
            self.avanzar()
            self.accion()
            self.acciones_prima()
        elif self.actual.tipo != "PUNTO_COMA":
            self.error("COMA o PUNTO_COMA")

    def accion(self) -> None:
        """``accion ::= ID ID``."""
        self.consumir("ID")
        self.consumir("ID")


AnalizadorSintactico = Parser


def parsear_tokens(tokens: Iterable[Token]) -> bool:
    """Valida una secuencia de tokens y devuelve ``True`` si es correcta.

    La secuencia debe provenir del lexer y terminar con un token ``EOF``.
    """
    return Parser(tokens).parse()


def parsear(texto: str) -> bool:
    """Analiza léxicamente ``texto`` y valida su sintaxis."""
    return parsear_tokens(analizar(texto))


def validar(texto: str) -> bool:
    """Indica si ``texto`` es sintácticamente válido sin lanzar excepciones."""
    try:
        return parsear(texto)
    except ErrorSintactico:
        return False


def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta el parser desde la línea de comandos."""
    argumentos = list(sys.argv[1:] if argv is None else argv)
    if not argumentos:
        print('Uso: python src/parser.py "<programa>"', file=sys.stderr)
        return 2

    try:
        parsear(" ".join(argumentos))
    except ErrorSintactico as error:
        print(error, file=sys.stderr)
        return 1

    print("Entrada sintácticamente válida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
