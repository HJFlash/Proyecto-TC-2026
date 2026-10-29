"""Pruebas del manejo de errores sintácticos del DSL del gallinero."""

from __future__ import annotations

import contextlib
import io
import random
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main

# Permite importar src/ como paquete namespace al ejecutar el archivo directamente.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.arbol import Programa
from src.errores import ErrorSintactico
from src.parser import main as main_parser, parsear, validar


class TestMensajesRequeridos(TestCase):
    """Mensajes claros para los errores típicos de la issue #10."""

    def assert_error(self, entrada: str, *subcadenas: str) -> ErrorSintactico:
        """Verifica que la entrada falle con ErrorSintactico y comprueba subcadenas."""
        with self.assertRaises(ErrorSintactico) as contexto:
            parsear(entrada)
        error = contexto.exception
        mensaje = str(error)
        for sub in subcadenas:
            self.assertIn(sub, mensaje)
        return error

    def test_entrada_vacia(self) -> None:
        error = self.assert_error("", "entrada está vacía", "WHEN")
        self.assertEqual(error.token.linea, 1)
        self.assertEqual(error.token.columna, 1)

    def test_solo_espacios(self) -> None:
        error = self.assert_error("   ", "entrada está vacía")
        self.assertEqual(error.token.tipo, "EOF")

    def test_falta_punto_y_coma(self) -> None:
        error = self.assert_error(
            "WHEN luz < 100 THEN abrir puerta",
            "punto y coma ';' para terminar la regla",
            "final de la entrada",
        )
        self.assertEqual(error.token.tipo, "EOF")

    def test_falta_then(self) -> None:
        error = self.assert_error(
            "WHEN luz < 100 abrir puerta;",
            "palabra reservada THEN después de la condición",
            "identificador 'abrir'",
        )
        self.assertIn("Si la condición continúa", str(error))

    def test_operador_sin_valor(self) -> None:
        self.assert_error(
            "WHEN luz < THEN abrir puerta;",
            "después del operador '<'",
            "valor (número, TRUE o FALSE)",
            "palabra reservada THEN",
        )

    def test_condicion_vacia(self) -> None:
        self.assert_error(
            "WHEN THEN abrir puerta;",
            "inicio de una comparación (NOT o un identificador)",
            "palabra reservada THEN",
        )

    def test_not_sin_comparacion(self) -> None:
        self.assert_error(
            "WHEN NOT THEN abrir puerta;",
            "después de NOT",
            "palabra reservada THEN",
        )

    def test_and_sin_operando(self) -> None:
        self.assert_error(
            "WHEN luz < 100 AND THEN abrir puerta;",
            "después de AND",
            "palabra reservada THEN",
        )

    def test_or_sin_operando(self) -> None:
        self.assert_error(
            "WHEN luz < 100 OR THEN abrir puerta;",
            "después de OR",
            "palabra reservada THEN",
        )

    def test_accion_sin_dispositivo(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir;",
            "dispositivo (un identificador) después del verbo 'abrir'",
            "punto y coma ';'",
        )

    def test_coma_inicial(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN , abrir puerta;",
            "verbo de la acción (un identificador)",
            "coma ','",
        )

    def test_coma_final(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta,;",
            "verbo de la acción (un identificador)",
            "punto y coma ';'",
        )

    def test_falta_coma_entre_acciones(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta abrir puerta;",
            "punto y coma ';' para terminar la regla",
            "identificador 'abrir'",
            "coma (',')",
        )

    def test_simbolo_no_reconocido(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta @;",
            "símbolo no reconocido '@'",
            "punto y coma ';' para terminar la regla",
        )

    def test_parentesis_no_admitidos(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN (abrir puerta);",
            "símbolo no reconocido '('",
            "paréntesis no forman parte",
        )

    def test_igualdad_simple(self) -> None:
        self.assert_error(
            "WHEN luz = 100 THEN abrir puerta;",
            "símbolo no reconocido '='",
            "para comparar igualdad use '=='",
        )

    def test_comentario_no_soportado(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta; #",
            "símbolo no reconocido '#'",
            "comentarios no están soportados",
        )

    def test_token_extra_tras_regla(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta; basura",
            "WHEN para comenzar otra regla",
            "final de la entrada",
            "identificador 'basura'",
        )

    def test_doble_punto_y_coma(self) -> None:
        self.assert_error(
            "WHEN luz < 100 THEN abrir puerta;;",
            "WHEN para comenzar otra regla",
            "final de la entrada",
            "punto y coma ';'",
        )


class TestPosiciones(TestCase):
    """El error reporta línea y columna correctas."""

    def test_posicion_multilinea(self) -> None:
        entrada = (
            "WHEN luz < 100 THEN abrir puerta;\n"
            "WHEN temperatura > THEN encender ventilador;"
        )
        with self.assertRaises(ErrorSintactico) as contexto:
            parsear(entrada)
        error = contexto.exception
        self.assertEqual(error.token.linea, 2)
        self.assertEqual(error.token.columna, 20)
        self.assertIn("línea 2, columna 20", str(error))
        self.assertIn("valor (número, TRUE o FALSE)", str(error))


class TestAtributosDelError(TestCase):
    """La excepción expone la información necesaria para depurar."""

    def test_atributos(self) -> None:
        with self.assertRaises(ErrorSintactico) as contexto:
            parsear("WHEN luz < 100 THEN abrir;")
        error = contexto.exception
        self.assertEqual(error.token.tipo, "PUNTO_COMA")
        self.assertEqual(error.token.lexema, ";")
        self.assertIn("dispositivo", error.esperado)
        self.assertIn("verbo 'abrir'", error.esperado)
        self.assertIn("punto y coma ';'", error.encontrado)
        self.assertIsNone(error.sugerencia)

class TestValidar(TestCase):
    """La función validar no propaga excepciones."""

    def test_validar_verdadero(self) -> None:
        self.assertTrue(
            validar("WHEN luz < 100 THEN abrir puerta;")
        )

    def test_validar_falso(self) -> None:
        self.assertFalse(
            validar("WHEN luz < 100 THEN abrir puerta")
        )


class TestNoCaida(TestCase):
    """El parser no se cae ante entradas malformadas."""

    MALFORMADAS = [
        "",
        "   ",
        "WHEN luz < 100 THEN abrir puerta",
        "WHEN luz < 100 abrir puerta;",
        "WHEN luz < THEN abrir puerta;",
        "WHEN THEN abrir puerta;",
        "WHEN luz < 100 THEN abrir;",
        "WHEN luz < 100 THEN (abrir puerta);",
        "WHEN luz < 100 THEN abrir puerta @;",
        "WHEN luz < 100 THEN abrir puerta,;",
        "WHEN luz < 100 THEN , abrir puerta;",
        "WHEN luz < 100 THEN abrir puerta abrir puerta;",
        "WHEN luz < 100 THEN abrir puerta; basura",
        "WHEN luz < 100 THEN abrir puerta; WHEN ;",
        "WHEN NOT THEN abrir puerta;",
        "WHEN luz < 100 AND THEN abrir puerta;",
        "WHEN luz < 100 OR THEN abrir puerta;",
        "WHEN luz < 100 THEN abrir puerta;;",
        ")",
        "WHEN luz < 100 THEN abrir puerta; #",
        "WHEN luz = 100 THEN abrir puerta;",
    ]

    def test_corpus_no_crash(self) -> None:
        for entrada in self.MALFORMADAS:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ErrorSintactico):
                    parsear(entrada)

    def test_fuzz_no_crash(self) -> None:
        random.seed(2026)
        alfabeto = list(
            "WHEN THEN AND OR NOT TRUE FALSE luz < >= ; , ( ) @ # 123 abc \n\t"
        )
        for _ in range(500):
            entrada = "".join(
                random.choice(alfabeto) for _ in range(random.randint(0, 30))
            )
            try:
                parsear(entrada)
            except ErrorSintactico:
                pass


class TestRegresionValidos(TestCase):
    """Las entradas válidas documentadas siguen parseando y generando AST."""

    VALIDOS = [
        "WHEN luz < 100 THEN abrir puerta;",
        "WHEN temperatura > 30 OR ventilacion == FALSE THEN encender ventilador;",
        "WHEN humedad >= 80 AND ventilacion != TRUE THEN encender ventilador;",
        "WHEN movimiento == TRUE AND NOT alarma_activa == TRUE THEN activar alarma;",
        "WHEN temperatura > 30 THEN encender ventilador, abrir puerta;",
        (
            "WHEN nivel_alimento < 20 THEN activar comedero; "
            "WHEN nivel_agua <= 30 THEN activar bebedero;"
        ),
    ]

    def test_validos_parsean(self) -> None:
        for entrada in self.VALIDOS:
            with self.subTest(entrada=entrada):
                ast = parsear(entrada)
                self.assertIsInstance(ast, Programa)
                self.assertGreater(len(ast.reglas), 0)


class TestCLI(TestCase):
    """El ejecutable por línea de comandos devuelve los códigos esperados."""

    INTERPRETE = sys.executable
    SCRIPT = str(RAIZ / "src" / "parser.py")

    def _correr(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.INTERPRETE, self.SCRIPT, *args],
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
        )

    def test_valido_devuelve_0(self) -> None:
        resultado = self._correr("WHEN luz < 100 THEN abrir puerta;")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("Árbol generado", resultado.stdout)

    def test_invalido_devuelve_1(self) -> None:
        resultado = self._correr("WHEN luz < 100 THEN abrir puerta")
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("punto y coma ';'", resultado.stderr)

    def test_sin_argumentos_devuelve_2(self) -> None:
        resultado = self._correr()
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("Uso:", resultado.stderr)

    def test_main_funcion_error(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            codigo = main_parser(["WHEN luz < 100 THEN abrir puerta"])
        self.assertEqual(codigo, 1)
        self.assertIn("punto y coma ';'", stderr.getvalue())


if __name__ == "__main__":
    main()
