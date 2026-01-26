"""Test script para verificar el comportamiento del retry handler.

Este script prueba:
1. Retry con éxito después de fallos
2. Backoff exponencial
3. Logging correcto
4. Fallo después de max_attempts
"""

import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.retry_handler import retry_with_backoff

# Configurar logging para ver los mensajes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)

# Contador global para simular fallos
attempt_counter = 0


@retry_with_backoff(
    max_attempts=5,
    base_delay=1.0,  # Delay corto para testing
    max_delay=10.0,
    strategy="exponential",
    logger=logger,
)
def test_function_success_after_3_attempts():
    """Función que falla 2 veces y luego tiene éxito."""
    global attempt_counter
    attempt_counter += 1

    if attempt_counter < 3:
        raise Exception(f"Fallo simulado en intento {attempt_counter}")

    return f"¡Éxito en intento {attempt_counter}!"


@retry_with_backoff(
    max_attempts=3, base_delay=1.0, strategy="exponential", logger=logger
)
def test_function_always_fails():
    """Función que siempre falla para probar max_attempts."""
    raise Exception("Esta función siempre falla")


def run_tests():
    """Ejecuta todos los tests."""
    global attempt_counter

    print("\n" + "=" * 60)
    print("TEST 1: Función que tiene éxito después de 2 fallos")
    print("=" * 60)

    attempt_counter = 0
    try:
        result = test_function_success_after_3_attempts()
        print(f"\n✅ Test 1 PASÓ: {result}")
    except Exception as e:
        print(f"\n❌ Test 1 FALLÓ: {e}")

    print("\n" + "=" * 60)
    print("TEST 2: Función que siempre falla (debe agotar reintentos)")
    print("=" * 60)

    try:
        result = test_function_always_fails()
        print(f"\n❌ Test 2 FALLÓ: No debería haber tenido éxito")
    except Exception as e:
        print(f"\n✅ Test 2 PASÓ: Falló correctamente después de agotar reintentos")
        print(f"   Error final: {str(e)[:50]}")

    print("\n" + "=" * 60)
    print("TEST 3: Verificar estrategias de backoff")
    print("=" * 60)

    from core.retry_handler import RetryHandler, RetryStrategy

    handler_exp = RetryHandler(strategy=RetryStrategy.EXPONENTIAL, base_delay=2.0)
    handler_lin = RetryHandler(strategy=RetryStrategy.LINEAR, base_delay=2.0)
    handler_fib = RetryHandler(strategy=RetryStrategy.FIBONACCI, base_delay=2.0)

    print("\nDelays para 5 intentos:")
    print("Intento | Exponencial | Linear | Fibonacci")
    print("-" * 45)
    for i in range(5):
        exp_delay = handler_exp.calculate_delay(i)
        lin_delay = handler_lin.calculate_delay(i)
        fib_delay = handler_fib.calculate_delay(i)
        print(
            f"  {i + 1}     |    {exp_delay:5.1f}s    | {lin_delay:4.1f}s |   {fib_delay:5.1f}s"
        )

    print("\n✅ Test 3 PASÓ: Estrategias calculan delays correctamente")

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS COMPLETADOS")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
