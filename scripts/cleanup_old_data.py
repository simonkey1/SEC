# scripts/cleanup_old_data.py

# 1. Importar lo necesario
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

def cleanup_old_records(days_to_keep = 30):
    """Borra registros más antiguos que X días."""
# 2. Cargar credenciales
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    # 3. Conectar a Supabase
    supabase: Client = create_client(url, key)

    # 4. Calcular fecha límite (30 días atrás)
    fecha_limite = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

    # 5. Borrar registros antiguos
    # Pista: usa .delete() y .lt('created_at', fecha_limite)
    try:
        result = supabase.table('fact_interrupciones').delete().lt('created_at', fecha_limite).execute()
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"✅ Borrados {deleted_count} registros anteriores a {fecha_limite[:10]}")
        return deleted_count
    except Exception as e: 
        logger.error(f'Falló la limpieza: {e}')
        return 0

    # 6. Loggear cuántos borraste
if __name__ == "__main__":
    deleted = cleanup_old_records(days_to_keep=1)
    print(f"Borrados: {deleted} registros")