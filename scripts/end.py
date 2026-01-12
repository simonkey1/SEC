
import time
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scraper import SECScraper
from core.tranformer import SecDataTransformer
from core.database import save_data_csv
from helper.check_variacion_historica import check_variacion_historico

def main():
    bot = SECScraper()
    transformer = SecDataTransformer()
    
    while True:
        print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] Iniciando captura de datos...")
        resultado = bot.run() 
        datos_raw = resultado.get("data", [])
        hora_server = resultado.get("hora_server")
        
        if datos_raw:
            print(f"✅ Se capturaron {len(datos_raw)} registros crudos.")
            datos_listos = transformer.transform(datos_raw, server_time=hora_server)
            save_data_csv(datos_listos)
            check_variacion_historico()
        else:
            print("⚠️ No se detectaron datos (posible lentitud de la página o sin cortes).")
        
        print("⏳ Esperando 5 minutos...")
        time.sleep(300)

if __name__ == "__main__":
    main()



