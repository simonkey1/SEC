# tests/test_circuit_breaker.py
import time
import pytest
from circuitbreaker import CircuitBreaker

class TestCircuitBreaker:
    """Tests para circuit breaker"""
    
    def test_circuit_breaker_success(self):
        """✅ Circuit breaker permite requests cuando OK"""
        breaker = CircuitBreaker(threshold=3)
        
        assert breaker.is_healthy() == True
        breaker.record_success()
        assert breaker.is_healthy() == True
    
    def test_circuit_breaker_fails_after_threshold(self):
        """✅ Circuit breaker detiene después de 3 fallos"""
        breaker = CircuitBreaker(threshold=3)
        
        breaker.record_failure()
        assert breaker.is_healthy() == True
        
        breaker.record_failure()
        assert breaker.is_healthy() == True
        
        breaker.record_failure()
        assert breaker.is_healthy() == False  # ← ABIERTO
    
    def test_circuit_breaker_resets(self):
        """✅ Circuit breaker se resetea después de cooldown"""
        breaker = CircuitBreaker(threshold=3, cooldown_seconds=0.1)
        
        # Genera 3 fallos
        for _ in range(3):
            breaker.record_failure()
        
        assert breaker.is_healthy() == False
        
        # Espera cooldown
        time.sleep(0.2)
        
        # Intenta reset
        breaker.attempt_reset()
        assert breaker.is_healthy() == True

# Ejecutar: pytest tests/test_circuit_breaker.py -v