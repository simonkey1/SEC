import sys

sys.path.append(".")

import polars as pl
from datetime import datetime, timedelta
import os
from scripts.analysis.storm_analysis import StormAnalyzer


def run_batch_visualization():
    # 1. Cargar Master List
    csv_path = "outputs/lista_maestra_cortes.csv"
    if not os.path.exists(csv_path):
        print("❌ No master list found.")
        return

    df_events = pl.read_csv(csv_path)
    print(f"🚀 Iniciando visualización por lotes para {len(df_events)} eventos...")

    analyzer = StormAnalyzer()
    df_data = analyzer.load_data()

    if df_data is None:
        print("❌ No data.")
        return

    # 2. Iterar y generar reportes
    reports_dir = "outputs/event_reports"
    os.makedirs(reports_dir, exist_ok=True)

    generated_links = []

    for row in df_events.iter_rows(named=True):
        region = row["nombre_region"]
        date_str = row["fecha"]
        affected = row["total_afectados"]

        # Convertir fecha
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Ventana: -2 días a +5 días
        start_date = event_date - timedelta(days=2)
        end_date = event_date + timedelta(days=5)

        nombre_clean = f"{date_str}_{region.replace(' ', '_')}"
        file_name = f"{nombre_clean}.html"
        save_path = os.path.join(reports_dir, file_name)

        event_title = f"{region} ({date_str}) - {affected} afectados"

        print(f"📊 Generando: {event_title}")
        analyzer.analyze_event(
            df_data, event_title, start_date, end_date, save_path=save_path
        )

        generated_links.append({"name": event_title, "link": file_name})

    # 3. Generar Index HTML simple
    index_path = os.path.join(reports_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Galería de Cortes Masivos Chile</title>")
        f.write(
            "<style>body{font-family:sans-serif; background:#111; color:#fff; padding:20px}"
        )
        f.write(
            "a{color:#00d4ff; text-decoration:none; display:block; margin:5px 0} a:hover{text-decoration:underline}</style>"
        )
        f.write("</head><body>")
        f.write("<h1>⚡ Galería de Desastres Eléctricos (53 Casos)</h1>")
        f.write(f"<p>Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}</p><hr>")

        for item in generated_links:
            f.write(f"<a href='{item['link']}' target='_blank'>📄 {item['name']}</a>")

        f.write("</body></html>")

    print(f"\n✅ Galería completa generada en: {index_path}")


if __name__ == "__main__":
    run_batch_visualization()
