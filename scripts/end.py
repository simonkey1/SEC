"""Main execution script (Orchestrator).

This script initializes the scraper and transformer, executing an
infinite loop that captures SEC data every 5 minutes, processes it and saves
it to local storage.
"""

import os
import sys
import time
from datetime import datetime

# Añadir el directorio raíz al path para importaciones modulares
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

from cleanup_old_data import cleanup_old_records

from core.circuitbreaker import CircuitBreaker
from core.database import SupabaseRepository, check_database_capacity
from core.scraper import SECScraper  # Volver a Playwright para GitHub Actions
from core.tranformer import SecDataTransformer

logger = logging.getLogger(__name__)


def main():
    """Main execution loop.

    Instantiates core components and manages the timed cycle
    of capture, transformation and persistence.
    """

    breaker = CircuitBreaker(3, 600)
    repo = SupabaseRepository()

    bot = SECScraper()  # Volver a Playwright
    transformer = SecDataTransformer()

    ciclo_contador = 0

    while True:
        ahora = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔍 [{ahora}] Iniciando captura de datos...")
        if breaker.puede_ejecutar():
            try:
                resultado = bot.run()
                breaker.registrar_exito()
                datos_raw = resultado.get("data", [])
                hora_server = resultado.get("hora_server")

                if datos_raw:
                    print(f"✅ Se capturaron {len(datos_raw)} registros crudos.")
                    datos_listos = transformer.transform(
                        datos_raw, server_time_raw=hora_server
                    )

                    # Save to Supabase (production)
                    resultado_db = repo.save_records(datos_listos)
                    logger.info(
                        f"💾 Supabase: {resultado_db['insertados']} insertados, {resultado_db['duplicados']} duplicados"
                    )
                else:
                    print(
                        "⚠️ No se detectaron datos (posible lentitud de la página o sin cortes)."
                    )

            except Exception as e:
                breaker.registrar_fallo()
                logger.error(f"❌ Error en scraper: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.info("Circuito abierto...")

        if ciclo_contador % 288 == 0:
            estado = check_database_capacity(threshold_percent=85)
            logger.info(f"📊 DB: {estado['porcentaje']:.1f}% ({estado['size_mb']} MB)")

        if ciclo_contador % 2016 == 0:
            deleted = cleanup_old_records(days_to_keep=30)
            logger.info(f"Limpieza : {deleted} registros borrados")

        ciclo_contador += 1
        print("⏳ Esperando 5 minutos para la próxima actualización...")
        time.sleep(300)


if __name__ == "__main__":
    main()
