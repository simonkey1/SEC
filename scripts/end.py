
"""Script principal de ejecución (Orquestador).

Este script inicializa el scraper y el transformador, ejecutando un bucle
infinito que captura datos de la SEC cada 5 minutos, los procesa y los guarda
en el almacenamiento local.
"""
import time
import sys
import os
from datetime import datetime

# Añadir el directorio raíz al path para importaciones modulares
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scraper import SECScraper
from core.tranformer import SecDataTransformer
from core.database import save_data_csv
from core.circuitbreaker import CircuitBreaker
import logging
logger = logging.getLogger(__name__)
from helper.check_variacion_historica import check_variacion_historico
from scripts.cleanup_old_data import cleanup_old_records
from core.database import check_database_capacity

def main():
    """Bucle principal de ejecución.
    
    Instancia los componentes del core y gestiona el ciclo cronometrado
    de captura, transformación y persistencia.
    """

    breaker = CircuitBreaker(3, 600)

    bot = SECScraper()
    transformer = SecDataTransformer()

    ciclo_contador = 0
    
    while True:
        ahora = datetime.now().strftime('%H:%M:%S')
        print(f"\n🔍 [{ahora}] Iniciando captura de datos...")
        if breaker.puede_ejecutar():
            try:
                resultado = bot.run()
                breaker.registrar_exito()
                datos_raw = resultado.get("data", [])
                hora_server = resultado.get("hora_server")
                
                if datos_raw:
                    print(f"✅ Se capturaron {len(datos_raw)} registros crudos.")
                    datos_listos = transformer.transform(datos_raw, server_time=hora_server)
                    save_data_csv(datos_listos)
                    check_variacion_historico()
                else:
                    print("⚠️ No se detectaron datos (posible lentitud de la página o sin cortes).")
                
                

            except Exception as e:
                breaker.registrar_fallo()
                logger.warning(f'Falla {e}')
        else:
            logger.info("Circuito abierto...")

        if ciclo_contador % 288 == 0:
            estado = check_database_capacity(threshold_percent=85)
            logger.info(f"📊 DB: {estado['porcentaje']:.1f}% ({estado['size_mb']} MB)")
            
        if ciclo_contador % 2016 == 0:
            deleted = cleanup_old_records(days_to_keep=30)
            logger.info(f'Limpieza : {deleted} registros borrados')    

        ciclo_contador +=1
        print("⏳ Esperando 5 minutos para la próxima actualización...")
        time.sleep(300)
        
if __name__ == "__main__":
    main()



