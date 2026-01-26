"""Retry handler with exponential backoff for robust scraping.

This module provides decorators and utilities to handle transient failures
with configurable retry strategies.
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional, Tuple, Type
from enum import Enum


class RetryStrategy(Enum):
    """Available retry strategies."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"


class RetryHandler:
    """Handles retry logic with various backoff strategies."""

    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize retry handler.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds between retries
            max_delay: Maximum delay cap in seconds
            strategy: Retry strategy to use
            exceptions: Tuple of exceptions to catch and retry
            logger: Optional logger instance
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.exceptions = exceptions
        self.logger = logger or logging.getLogger(__name__)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on strategy and attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        if self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (2**attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        elif self.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13...
            fib = self._fibonacci(attempt + 1)
            delay = self.base_delay * fib
        else:
            delay = self.base_delay

        return min(delay, self.max_delay)

    @staticmethod
    def _fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return 1
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return a

    def __call__(self, func: Callable) -> Callable:
        """Decorator to add retry logic to a function.

        Args:
            func: Function to wrap with retry logic

        Returns:
            Wrapped function
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    self.logger.info(
                        f"Intento {attempt + 1}/{self.max_attempts} - {func.__name__}"
                    )
                    result = func(*args, **kwargs)

                    if attempt > 0:
                        self.logger.info(f"✅ Éxito después de {attempt + 1} intentos")

                    return result

                except self.exceptions as e:
                    last_exception = e

                    if attempt < self.max_attempts - 1:
                        delay = self.calculate_delay(attempt)
                        self.logger.warning(
                            f"⚠️ Error en intento {attempt + 1}: {str(e)[:100]}"
                        )
                        self.logger.info(
                            f"⏳ Esperando {delay:.1f}s antes del siguiente intento..."
                        )
                        time.sleep(delay)
                    else:
                        self.logger.error(
                            f"❌ Falló después de {self.max_attempts} intentos"
                        )

            # Si llegamos aquí, todos los intentos fallaron
            raise last_exception

        return wrapper


def retry_with_backoff(
    max_attempts: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    strategy: str = "exponential",
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[logging.Logger] = None,
):
    """Decorator factory for retry with backoff.

    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        def my_function():
            # code that might fail
            pass

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay cap in seconds
        strategy: Retry strategy ("exponential", "linear", "fibonacci")
        exceptions: Tuple of exceptions to catch and retry
        logger: Optional logger instance
    """
    strategy_enum = RetryStrategy(strategy)
    handler = RetryHandler(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=strategy_enum,
        exceptions=exceptions,
        logger=logger,
    )
    return handler


# Configuración de logging por defecto
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
