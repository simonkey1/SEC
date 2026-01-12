import psycopg2
import pandas as pd

# Lee tu CSV
df = pd.read_csv("clientes_afectados_historico_2025.0.csv")

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="sec",
    user="postgres",
    password="acidosa123",
    host="localhost",  # o la IP/host si es remoto
    port=5432
)
cursor = conn.cursor()

for index, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO clientes_afectados (ID_UNICO, TIMESTAMP, FECHA, REGION, COMUNA, EMPRESA, CLIENTES_AFECTADOS, ACTUALIZADO_HACE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ID_UNICO) DO NOTHING
        """, (
            row["ID_UNICO"],
            row["TIMESTAMP"],
            row["FECHA"],
            row["REGION"],
            row["COMUNA"],
            row["EMPRESA"],
            row["CLIENTES_AFECTADOS"],
            row["ACTUALIZADO_HACE"]
        ))
    except Exception as e:
        print("Error insertando fila:", e)

conn.commit()
cursor.close()
conn.close()
print("¡Datos insertados exitosamente!")
