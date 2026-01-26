"""Test script para verificar el comportamiento del retry handler.

Este script prueba:
1. Retry con éxito después de fallos
2. Backoff exponencial
3. Logging correcto
4. Fallo después de max_attempts
"""

import logging
import sys
import pytest
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
def always_fails_func():
    """Función auxiliar que siempre falla."""
    raise Exception("Esta función siempre falla")


def test_retry_logic_success():
    """Verifica que el retry tenga éxito eventualmente."""
    global attempt_counter
    attempt_counter = 0
    result = test_function_success_after_3_attempts()
    assert "¡Éxito" in result


def test_retry_logic_failure():
    """Verifica que el retry falle después de max_attempts."""
    with pytest.raises(Exception) as excinfo:
        always_fails_func()
    assert "Esta función siempre falla" in str(excinfo.value)


def test_backoff_strategies():
    """Verifica el cálculo de delays."""
    from core.retry_handler import RetryHandler, RetryStrategy

    handler_exp = RetryHandler(strategy=RetryStrategy.EXPONENTIAL, base_delay=2.0)
    # Simple check de que incremente
    assert handler_exp.calculate_delay(2) > handler_exp.calculate_delay(1)
