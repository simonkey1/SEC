"""Data persistence and path management module.

This module defines storage paths and provides functions
to save processed data in CSV formats (local).
"""
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from supabase import create_client, Client
logger = logging.getLogger(__name__)

# Rutas globales para gestión de archivos


# En core/database.py

class SupabaseRepository:
    """Repository pattern for Supabase data persistence.
    
    Manages dimension tables (get_or_create) and fact table insertions.
    """
    
    def __init__(self):
        """Initialize Supabase client with credentials from .env"""
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase = create_client(url, key)
    
    def get_or_create_geografia(self, region: str, comuna: str) -> int:
        """Get or create geography dimension record."""
        
        resultado = self.supabase.table('dim_geografia') \
        .select('id_geografia') \
        .eq('nombre_region', region) \
        .eq('nombre_comuna', comuna) \
        .execute()

        if resultado.data and len(resultado.data) > 0:
            return resultado.data[0]['id_geografia']
        
        nuevo = self.supabase.table('dim_geografia') \
                .insert({'nombre_region': region,
                        'nombre_comuna': comuna
                        }) \
                        .execute()
        return nuevo.data[0]['id_geografia']
        

    
    def get_or_create_empresa(self, empresa: str) -> int:
        """Get or create company dimension record."""
        resultado = self.supabase.table('dim_empresa') \
        .select('id_empresa') \
        .eq('nombre_empresa', empresa) \
        .execute()

        if resultado.data and len(resultado.data) > 0:
            return resultado.data[0]['id_empresa']
        
        nuevo = self.supabase.table('dim_empresa') \
                .insert({'nombre_empresa': empresa
                        }) \
                        .execute()
        return nuevo.data[0]['id_empresa']
    
    def get_or_create_tiempo(self, timestamp_str: str) -> int:
        """Get or create time dimension record."""
    
    
    # 1. Parsear timestamp
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        # 2. Generar id_tiempo como entero (YYYYMMDDHHMM)
        id_tiempo = int(dt.strftime("%Y%m%d%H%M"))
        
        # 3. Buscar si existe
        resultado = self.supabase.table('dim_tiempo') \
            .select('id_tiempo') \
            .eq('id_tiempo', id_tiempo) \
            .execute()

        if resultado.data and len(resultado.data) > 0:
            return id_tiempo  # ← Retornar el id_tiempo, no .data[0]
        
        # 4. Insertar nuevo
        self.supabase.table('dim_tiempo') \
            .insert({
                'id_tiempo': id_tiempo,
                'fecha': dt.date().isoformat(),  # "2026-01-23"
                'hora': dt.time().isoformat(),   # "14:30:00"
                'año': dt.year,
                'mes': dt.month,
                'dia': dt.day
            }) \
            .execute()
        
        return id_tiempo  # ← Retornar el id_tiempo
    
    def save_records(self, registros: list) -> dict:
        """Save processed records to fact table."""
        insertados = 0
        duplicados = 0
        errores = 0
        
        for registro in registros:
            try:
                # Obtener FKs usando self (ya tienes la instancia)
                id_geografia = self.get_or_create_geografia(
                    region=registro['REGION'],
                    comuna=registro['COMUNA']
                )
                id_empresa = self.get_or_create_empresa(
                    empresa=registro['EMPRESA']
                )
                id_tiempo = self.get_or_create_tiempo(
                    timestamp_str=registro['TIMESTAMP']
                )
                
                # Insertar en fact table
                self.supabase.table('fact_interrupciones').insert({
                    'id_tiempo': id_tiempo,
                    'id_geografia': id_geografia,
                    'id_empresa': id_empresa,
                    'clientes_afectados': registro['CLIENTES_AFECTADOS'],
                    'hash_id': registro['ID_UNICO']
                }).execute()
                
                insertados += 1
                
            except Exception as e:
                if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                    duplicados += 1
                else:
                    errores += 1
                    logger.error(f"Error insertando: {e}")
        
        # Logging DESPUÉS del for (misma indentación que el for)
        logger.info(f"✅ Insertados: {insertados} | Duplicados: {duplicados} | Errores: {errores}")
        
        return {
            'insertados': insertados,
            'duplicados': duplicados,
            'errores': errores
        }



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Cerciorarse de que el directorio de salida existe

os.makedirs(OUTPUT_DIR, exist_ok=True)

csv_tiempo_real = os.path.join(OUTPUT_DIR, "clientes_afectados_tiempo_real.csv")
csv_historico = os.path.join(OUTPUT_DIR, "clientes_afectados_historico.csv")

def save_data_csv(registros):
    """Saves processed records to local CSV files.
    
    Manages two files: one historical (incremental without duplicates) and
    uno de tiempo real (sobrescritura del estado actual).

    Args:
        registros (list): Lista de diccionarios procesados por el transformer.
    """
    if registros:
        df_new = pd.DataFrame(registros)

        # Guardar en histórico
        if os.path.exists(csv_historico):
            df_hist = pd.read_csv(csv_historico, encoding="utf-8-sig")
            df_hist = pd.concat([df_hist, df_new], ignore_index=True)
            df_hist = df_hist.drop_duplicates(subset=["ID_UNICO", "TIMESTAMP"])
        else:
            df_hist = df_new
            print(f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)")

        df_hist.to_csv(csv_historico, index=False, encoding="utf-8-sig")

        # Guardar en tiempo real (sobrescribe)
        df_new.to_csv(csv_tiempo_real, index=False, encoding="utf-8-sig")

        print(f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)")

def save_data_sql():
     pass



def check_database_capacity(threshold_percent = 85):
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    supabase: Client = create_client(url, key)
    try:

        response = (
        supabase.table('fact_interrupciones')
        .select('*', count='exact').execute()
    )
        total_filas = response.count


        size_mb = (total_filas * 200) / 1024 / 1024

        porcentaje = (size_mb / 500) * 100
        alert_sent = False
        if porcentaje >= threshold_percent:
            from core.notifications import EmailNotifier
            notifier = EmailNotifier()
            notifier.send_capacity_alert(porcentaje=porcentaje, size_mb=size_mb, total_filas=total_filas)
            logger.warning(f"⚠️ Base de datos al {porcentaje:.2f}% de capacidad")
            alert_sent = True
        
        # 5. Retornar estado
        return {
            "size_mb": round(size_mb, 2),
            "porcentaje": round(porcentaje, 2),
            "alert_sent": alert_sent,
            "total_filas": total_filas  # Extra: útil para debugging
            }
        
    except Exception as e:
        logger.error(f"❌ Error verificando capacidad: {e}")
        return {
            "size_mb": 0,
            "porcentaje": 0,
            "alert_sent": False,
            "total_filas": 0
        }

