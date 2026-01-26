import sys
import os
from pathlib import Path

# Agregar raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.postgres_repository import PostgreSQLRepository


def main():
    try:
        repo = PostgreSQLRepository()
        count = repo.get_record_count()
        size = repo.get_database_size()

        print(f"\n📊 ESTADO ACTUAL DE LA DB:")
        print(f"   Total registros: {count:,}")
        print(f"   Tamaño DB: {size['size_pretty']}")

        # Consultar por año
        with repo.conn.cursor() as cur:
            cur.execute("""
                SELECT t.año, COUNT(*) 
                FROM fact_interrupciones f 
                JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo 
                GROUP BY t.año 
                ORDER BY t.año;
            """)
            results = cur.fetchall()

            if results:
                print("\n📅 Conteo por año:")
                for año, total in results:
                    print(f"   {año}: {total:,} registros")
            else:
                print(
                    "\n📅 No hay registros por año aún (o no se ha vinculado dim_tiempo)"
                )

        repo.close()
    except Exception as e:
        print(f"❌ Error al consultar: {e}")


if __name__ == "__main__":
    main()
