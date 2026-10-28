"""Analizador sintáctico predictivo LL(1) del DSL del gallinero con generación de AST.

El parser se implementa a mano por descenso recursivo, sin generadores.
Construye el Árbol de Sintaxis Abstracta (AST) de forma concurrente con el análisis.
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence
import sys
from typing import NoReturn, Optional

if __package__:
    from .lexer import Token, analizar
    from .arbol import (Programa, Regla, Comparacion, Accion, 
                        OperacionBinaria, OperacionUnaria)
else:
    from lexer import Token, analizar
    from arbol import (Programa, Regla, Comparacion, Accion, 
                       OperacionBinaria, OperacionUnaria)

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

    def consumir(self, tipo: str) -> Token:
        if self.actual.tipo != tipo:
            self.error(tipo)
        return self.avanzar()

    def error(self, esperado: str) -> NoReturn:
        raise ErrorSintactico(self.actual, esperado)

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
            self.error("WHEN o EOF")
        return []

    def regla(self) -> Regla:
        self.consumir("WHEN")
        cond = self.condicion()
        self.consumir("THEN")
        accs = self.acciones()
        self.consumir("PUNTO_COMA")
        return Regla(cond, accs)

    def condicion(self) -> OperacionBinaria | OperacionUnaria | Comparacion:
        return self.cond_or()

    def cond_or(self) -> OperacionBinaria | OperacionUnaria | Comparacion:
        izq = self.cond_and()
        return self.cond_or_prima(izq)

    def cond_or_prima(self, izq: OperacionBinaria | OperacionUnaria | Comparacion) -> OperacionBinaria | OperacionUnaria | Comparacion:
        if self.actual.tipo == "OR":
            op = self.avanzar().lexema
            der = self.cond_and()
            nuevo_nodo = OperacionBinaria(op, izq, der)
            return self.cond_or_prima(nuevo_nodo)
        elif self.actual.tipo != "THEN":
            self.error("OR o THEN")
        return izq

    def cond_and(self) -> OperacionBinaria | OperacionUnaria | Comparacion:
        izq = self.factor()
        return self.cond_and_prima(izq)

    def cond_and_prima(self, izq: OperacionBinaria | OperacionUnaria | Comparacion) -> OperacionBinaria | OperacionUnaria | Comparacion:
        if self.actual.tipo == "AND":
            op = self.avanzar().lexema
            der = self.factor()
            nuevo_nodo = OperacionBinaria(op, izq, der)
            return self.cond_and_prima(nuevo_nodo)
        elif self.actual.tipo not in {"OR", "THEN"}:
            self.error("AND, OR o THEN")
        return izq

    def factor(self) -> OperacionUnaria | Comparacion:
        if self.actual.tipo == "NOT":
            op = self.avanzar().lexema
            comp = self.comparacion()
            return OperacionUnaria(op, comp)
        elif self.actual.tipo == "ID":
            return self.comparacion()
        else:
            self.error("NOT o ID")

    def comparacion(self) -> Comparacion:
        id_izq = self.consumir("ID").lexema
        op_rel = self.consumir("OP_REL").lexema
        valor_der = self.valor()
        return Comparacion(id_izq, op_rel, valor_der)

    def valor(self) -> str:
        if self.actual.tipo in {"NUM", "TRUE", "FALSE"}:
            return self.avanzar().lexema
        else:
            self.error("NUM, TRUE o FALSE")

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
        elif self.actual.tipo != "PUNTO_COMA":
            self.error("COMA o PUNTO_COMA")
        return []

    def accion(self) -> Accion:
        verbo = self.consumir("ID").lexema
        dispositivo = self.consumir("ID").lexema
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