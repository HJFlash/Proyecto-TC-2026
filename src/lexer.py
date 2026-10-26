"""Analizador léxico del DSL para automatizar el gallinero."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterator


@dataclass(frozen=True)
class Token:
    """Token producido por el analizador léxico."""

    tipo: str
    lexema: str
    linea: int
    columna: int


palabras_reservadas: dict[str, str] = {
    "WHEN": "WHEN",
    "THEN": "THEN",
    "AND": "AND",
    "OR": "OR",
    "NOT": "NOT",
    "TRUE": "TRUE",
    "FALSE": "FALSE",
}


# El orden de los operadores garantiza coincidencia más larga.
especificacion_tokens: tuple[tuple[str, str], ...] = (
    ("ESPACIO", r"[ \t\r\n]+"),
    ("OP_REL", r">=|<=|==|!=|>|<"),
    ("PUNTO_COMA", r";"),
    ("COMA", r","),
    ("NUM", r"[0-9]+"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("ERROR", r"."),
)

_patron_tokens = re.compile(
    "|".join(f"(?P<{tipo}>{patron})" for tipo, patron in especificacion_tokens),
    re.ASCII,
)


class Lexer:
    """Convierte el texto del DSL en una secuencia de tokens."""

    def __init__(self, texto: str) -> None:
        self.texto = texto

    def tokens(self) -> Iterator[Token]:
        """Genera tokens, incluyendo un token ``EOF`` al final."""
        posicion = 0
        linea = 1
        columna = 1

        while posicion < len(self.texto):
            coincidencia = _patron_tokens.match(self.texto, posicion)
            if coincidencia is None:
                # La especificación termina en ERROR, por lo que esta rama
                # solo protege el contrato si se modifica la especificación.
                lexema = self.texto[posicion]
                yield Token("ERROR", lexema, linea, columna)
                posicion += 1
                columna += 1
                continue

            tipo = coincidencia.lastgroup
            if tipo is None:
                raise RuntimeError("La especificación léxica produjo un grupo vacío")

            lexema = coincidencia.group()
            posicion = coincidencia.end()
            inicio_linea = linea
            inicio_columna = columna

            if tipo == "ESPACIO":
                linea, columna = _avanzar_posicion(lexema, linea, columna)
                continue

            if tipo == "ID":
                tipo = palabras_reservadas.get(lexema.upper(), "ID")

            yield Token(tipo, lexema, inicio_linea, inicio_columna)
            linea, columna = _avanzar_posicion(lexema, linea, columna)

        yield Token("EOF", "", linea, columna)

    def analizar(self) -> list[Token]:
        """Devuelve todos los tokens de la entrada."""
        return list(self.tokens())


def _avanzar_posicion(lexema: str, linea: int, columna: int) -> tuple[int, int]:
    """Calcula la posición posterior a un lexema."""
    saltos = lexema.count("\n")
    if saltos:
        return linea + saltos, len(lexema.rsplit("\n", 1)[1]) + 1
    return linea, columna + len(lexema)


def analizar(texto: str) -> list[Token]:
    """Analiza ``texto`` y devuelve sus tokens."""
    return Lexer(texto).analizar()


def analizar_lexico(texto: str) -> list[Token]:
    """Alias descriptivo para integrar el lexer con el parser."""
    return analizar(texto)


def tokenizar(texto: str) -> list[Token]:
    """Alias de ``analizar``."""
    return analizar(texto)


AnalizadorLexico = Lexer

