"""Nodos del Árbol de Sintaxis Abstracta (AST) del DSL del gallinero.

Cada nodo sabe imprimirse de forma jerárquica, lo que permite inspeccionar
el resultado del parser desde la línea de comandos.
"""

from __future__ import annotations

import sys

__all__ = [
    "Accion",
    "Comparacion",
    "NodoAST",
    "OperacionBinaria",
    "OperacionUnaria",
    "Programa",
    "Regla",
]


class NodoAST:
    """Clase base para todos los nodos del árbol."""

    def imprimir(self, nivel: int = 0) -> None:
        raise NotImplementedError


class Programa(NodoAST):
    def __init__(self, reglas: list[Regla]) -> None:
        self.reglas = reglas

    def imprimir(self, nivel: int = 0) -> None:
        print("  " * nivel + "└── Programa")
        for regla in self.reglas:
            regla.imprimir(nivel + 1)


class Regla(NodoAST):
    def __init__(self, condicion: NodoAST, acciones: list[Accion]) -> None:
        self.condicion = condicion
        self.acciones = acciones  # Lista de nodos Accion

    def imprimir(self, nivel: int = 0) -> None:
        print("  " * nivel + "├── Regla (WHEN ... THEN ...)")
        print("  " * (nivel + 1) + "├── Condicion:")
        self.condicion.imprimir(nivel + 2)
        print("  " * (nivel + 1) + "└── Acciones:")
        for accion in self.acciones:
            accion.imprimir(nivel + 2)


class OperacionBinaria(NodoAST):
    """Para operadores AND y OR."""

    def __init__(
        self,
        operador: str,
        izquierdo: NodoAST,
        derecho: NodoAST,
    ) -> None:
        self.operador = operador
        self.izquierdo = izquierdo
        self.derecho = derecho

    def imprimir(self, nivel: int = 0) -> None:
        print("  " * nivel + f"├── Operador Binario: {self.operador}")
        self.izquierdo.imprimir(nivel + 1)
        self.derecho.imprimir(nivel + 1)


class OperacionUnaria(NodoAST):
    """Para el operador NOT."""

    def __init__(self, operador: str, operando: NodoAST) -> None:
        self.operador = operador
        self.operando = operando

    def imprimir(self, nivel: int = 0) -> None:
        print("  " * nivel + f"├── Operador Unario: {self.operador}")
        self.operando.imprimir(nivel + 1)


class Comparacion(NodoAST):
    """Para ID OP_REL VALOR."""

    def __init__(self, id_izq: str, op_rel: str, valor_der: str) -> None:
        self.id_izq = id_izq
        self.op_rel = op_rel
        self.valor_der = valor_der

    def imprimir(self, nivel: int = 0) -> None:
        print(
            "  " * nivel
            + f"└── Comparacion: {self.id_izq} {self.op_rel} {self.valor_der}"
        )


class Accion(NodoAST):
    """Para ID ID (ej: encender ventilador)."""

    def __init__(self, verbo: str, dispositivo: str) -> None:
        self.verbo = verbo
        self.dispositivo = dispositivo

    def imprimir(self, nivel: int = 0) -> None:
        print("  " * nivel + f"└── Accion: {self.verbo} {self.dispositivo}")


# --- Ejemplo de uso y prueba para el informe ---
if __name__ == "__main__":
    # Evita UnicodeEncodeError cuando la consola no soporta los símbolos del
    # árbol (por ejemplo, cp1252 en Windows).
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")

    # Simulación del árbol para:
    # WHEN luz < 100 AND NOT puerta_cerrada == TRUE THEN encender lampara, abrir puerta;

    comp1 = Comparacion("luz", "<", "100")
    comp2 = Comparacion("puerta_cerrada", "==", "TRUE")
    not_comp2 = OperacionUnaria("NOT", comp2)
    condicion_and = OperacionBinaria("AND", comp1, not_comp2)

    acc1 = Accion("encender", "lampara")
    acc2 = Accion("abrir", "puerta")

    regla = Regla(condicion_and, [acc1, acc2])
    programa = Programa([regla])

    print("Ejemplo de Árbol Sintáctico:")
    programa.imprimir()
