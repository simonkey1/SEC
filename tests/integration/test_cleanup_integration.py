import pytest
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from scripts.cleanup_old_data import cleanup_old_records

def test_cleanup_deletes_only_old_records():
    """Verifies that cleanup deletes only records >30 days old"""
    
    # 1. Setup: Conectar a Supabase
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    # 3. Conectar a Supabase
    supabase: Client = create_client(url, key)

    # 2. Crear hashes únicos
    hash_antiguo = f"test_antiguo_{uuid.uuid4()}"
    hash_reciente = f"test_reciente_{uuid.uuid4()}"

    # 3. Insertar registros en dim_tiempo primero (para cumplir FK)
    id_tiempo_antiguo = 202601010000
    id_tiempo_reciente = 202601200000
    
    # Insertar dim_tiempo si no existen (ignorar si ya existen)
    try:
        supabase.table('dim_tiempo').insert({
            'id_tiempo': id_tiempo_antiguo,
            'fecha': '2026-01-01',
            'hora': '00:00:00',
            'año': 2026,
            'mes': 1,
            'dia': 1
        }).execute()
    except:
        pass  # Ya existe, continuar
    
    try:
        supabase.table('dim_tiempo').insert({
            'id_tiempo': id_tiempo_reciente,
            'fecha': '2026-01-20',
            'hora': '00:00:00',
            'año': 2026,
            'mes': 1,
            'dia': 20
        }).execute()
    except:
        pass  # Ya existe, continuar
    
    # 4. Insertar registro antiguo (36 días)
    supabase.table('fact_interrupciones').insert({
      'id_tiempo': id_tiempo_antiguo, 
      'id_geografia': 1, 
      'id_empresa': 1, 
      'clientes_afectados': 250, 
      'hash_id': hash_antiguo, 
      'created_at': (datetime.now() - timedelta(days=36)).isoformat()
    }).execute()

    # 5. Insertar registro reciente (10 días)
    supabase.table('fact_interrupciones').insert({
        'id_tiempo': id_tiempo_reciente,
        'id_geografia': 1,
        'id_empresa': 1,
        'clientes_afectados': 100,
        'hash_id': hash_reciente,
        'created_at': (datetime.now() - timedelta(days=10)).isoformat()
    }).execute()


    
    # 5. Act: Ejecutar cleanup
    deleted = cleanup_old_records(days_to_keep=30)

    assert deleted >=1

    response_antiguo = supabase.table('fact_interrupciones').select('*').eq('hash_id', hash_antiguo).execute()
    assert len(response_antiguo.data) == 0
    
    # 8. Verificar que el reciente SÍ existe
    response_reciente = supabase.table('fact_interrupciones').select('*').eq('hash_id', hash_reciente).execute()
    assert len(response_reciente.data) == 1
    
    # 9. Cleanup: Borrar registro de prueba reciente
    supabase.table('fact_interrupciones').delete().eq('hash_id', hash_reciente).execute()
    
   