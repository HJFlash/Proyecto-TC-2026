# src/arbol.py

class NodoAST:
    """Clase base para todos los nodos del árbol."""
    def imprimir(self, nivel=0):
        raise NotImplementedError

class Programa(NodoAST):
    def __init__(self, reglas):
        self.reglas = reglas

    def imprimir(self, nivel=0):
        print("  " * nivel + "└── Programa")
        for regla in self.reglas:
            regla.imprimir(nivel + 1)

class Regla(NodoAST):
    def __init__(self, condicion, acciones):
        self.condicion = condicion
        self.acciones = acciones  # Lista de nodos Accion

    def imprimir(self, nivel=0):
        print("  " * nivel + "├── Regla (WHEN ... THEN ...)")
        print("  " * (nivel + 1) + "├── Condicion:")
        self.condicion.imprimir(nivel + 2)
        print("  " * (nivel + 1) + "└── Acciones:")
        for accion in self.acciones:
            accion.imprimir(nivel + 2)

class OperacionBinaria(NodoAST):
    """Para operadores AND y OR."""
    def __init__(self, operador, izquierdo, derecho):
        self.operador = operador
        self.izquierdo = izquierdo
        self.derecho = derecho

    def imprimir(self, nivel=0):
        print("  " * nivel + f"├── Operador Binario: {self.operador}")
        self.izquierdo.imprimir(nivel + 1)
        self.derecho.imprimir(nivel + 1)

class OperacionUnaria(NodoAST):
    """Para el operador NOT."""
    def __init__(self, operador, operando):
        self.operador = operador
        self.operando = operando

    def imprimir(self, nivel=0):
        print("  " * nivel + f"├── Operador Unario: {self.operador}")
        self.operando.imprimir(nivel + 1)

class Comparacion(NodoAST):
    """Para ID OP_REL VALOR."""
    def __init__(self, id_izq, op_rel, valor_der):
        self.id_izq = id_izq
        self.op_rel = op_rel
        self.valor_der = valor_der

    def imprimir(self, nivel=0):
        print("  " * nivel + f"└── Comparacion: {self.id_izq} {self.op_rel} {self.valor_der}")

class Accion(NodoAST):
    """Para ID ID (ej: encender ventilador)."""
    def __init__(self, verbo, dispositivo):
        self.verbo = verbo
        self.dispositivo = dispositivo

    def imprimir(self, nivel=0):
        print("  " * nivel + f"└── Accion: {self.verbo} {self.dispositivo}")

# --- Ejemplo de uso y prueba para el informe ---
if __name__ == "__main__":
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