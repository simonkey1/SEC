import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time

import pytest

from core.circuitbreaker import CircuitBreaker, States


class TestCircuitBreaker:
    @pytest.fixture
    def breaker(self):
        # Retorna una instancia fresca para cada test
        return CircuitBreaker(failure_treshold=2, recovery_timeout=2)

    def test_initial_state(self, breaker):
        assert breaker.state == States.CLOSED
        assert breaker.puede_ejecutar() is True

    def test_blocks_when_open(self, breaker):
        breaker.registrar_fallo()
        breaker.registrar_fallo()
        breaker.registrar_fallo()
        assert breaker.puede_ejecutar() is False

    def test_automatically_recovers_after_timeout(self, breaker):
        breaker.registrar_fallo()
        assert breaker.state == States.CLOSED  # Aún no llega al umbral (2)
        breaker.registrar_fallo()
        assert breaker.last_failure_time is not None
        assert breaker.state == States.OPEN
        time.sleep(3)
        assert breaker.puede_ejecutar() is True

    def test_tolerancia_cero(self, breaker):
        breaker.state = States.HALF_OPEN
        breaker.registrar_fallo()
        assert breaker.state == States.OPEN
        assert breaker.fail_counter == breaker.failure_treshold

    def test_happy_end(self, breaker):
        breaker.state = States.HALF_OPEN
        breaker.registrar_exito()
        assert breaker.state == States.CLOSED
        assert breaker.fail_counter == 0

    def test_reset_on_success(self, breaker):
        breaker.registrar_fallo()
        breaker.registrar_exito()

        assert breaker.state == States.CLOSED
        assert breaker.fail_counter == 0
        assert breaker.last_failure_time is None
