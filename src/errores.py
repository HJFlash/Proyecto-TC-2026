"""Mensajes y excepción para errores sintácticos del DSL del gallinero.

Este módulo centraliza la forma en que se reportan los errores de sintaxis.
Se encarga de traducir tokens técnicos a frases legibles y de ofrecer pistas
contextuales para los errores más frecuentes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import Token

__all__ = [
    "ErrorSintactico",
    "describir_token",
    "describir_tipo",
]


# Ayudas para símbolos léxicos que suelen confundir al usuario.
AYUDAS_SIMBOLO: dict[str, str] = {
    "(": "los paréntesis no forman parte del lenguaje",
    ")": "los paréntesis no forman parte del lenguaje",
    "=": "para comparar igualdad use '=='",
    "#": "los comentarios no están soportados",
}


def describir_token(token: "Token") -> str:
    """Devuelve una descripción legible de un token concreto."""
    tipo = token.tipo
    lexema = token.lexema

    if tipo == "EOF":
        return "el final de la entrada"

    if tipo == "ERROR":
        base = f"el símbolo no reconocido {lexema!r}"
        ayuda = AYUDAS_SIMBOLO.get(lexema)
        if ayuda:
            return f"{base} ({ayuda})"
        return base

    if tipo in {"WHEN", "THEN", "AND", "OR", "NOT"}:
        return f"la palabra reservada {tipo}"

    if tipo in {"TRUE", "FALSE"}:
        return f"el valor booleano {tipo}"

    if tipo == "ID":
        return f"el identificador {lexema!r}"

    if tipo == "NUM":
        return f"el número {lexema!r}"

    if tipo == "OP_REL":
        return f"el operador {lexema!r}"

    if tipo == "COMA":
        return "la coma ','"

    if tipo == "PUNTO_COMA":
        return "el punto y coma ';'"

    return f"el token {tipo} {lexema!r}"


def describir_tipo(tipo: str) -> str:
    """Devuelve una descripción legible de un tipo de token esperado."""
    if tipo == "WHEN":
        return "la palabra reservada WHEN"

    if tipo == "THEN":
        return "la palabra reservada THEN"

    if tipo == "AND":
        return "la palabra reservada AND"

    if tipo == "OR":
        return "la palabra reservada OR"

    if tipo == "NOT":
        return "la palabra reservada NOT"

    if tipo == "ID":
        return "un identificador"

    if tipo == "NUM":
        return "un número"

    if tipo == "TRUE":
        return "el valor booleano TRUE"

    if tipo == "FALSE":
        return "el valor booleano FALSE"

    if tipo == "OP_REL":
        return "un operador relacional (>, <, >=, <=, ==, !=)"

    if tipo == "COMA":
        return "la coma ','"

    if tipo == "PUNTO_COMA":
        return "el punto y coma ';'"

    if tipo == "EOF":
        return "el final de la entrada"

    return f"un token {tipo}"


class ErrorSintactico(Exception):
    """Error de sintaxis localizado en un token de la entrada."""

    def __init__(
        self,
        token: "Token",
        esperado: str,
        *,
        sugerencia: str | None = None,
        mensaje: str | None = None,
    ) -> None:
        self.token = token
        self.esperado = esperado
        self.encontrado = describir_token(token)
        self.sugerencia = sugerencia

        if mensaje is None:
            mensaje = (
                f"Error sintáctico en línea {token.linea}, columna {token.columna}: "
                f"se esperaba {esperado}; se encontró {self.encontrado}."
            )

        if sugerencia:
            mensaje += f" {sugerencia}"

        super().__init__(mensaje)

    @classmethod
    def entrada_vacia(cls, token: "Token") -> "ErrorSintactico":
        """Construye el error para una entrada completamente vacía."""
        return cls(
            token,
            "al menos una regla iniciada por WHEN",
            mensaje=(
                f"Error sintáctico en línea {token.linea}, columna {token.columna}: "
                "la entrada está vacía; se esperaba al menos una regla iniciada por WHEN."
            ),
        )
