"""Scraper para obtener total de clientes por región desde SEC.

Endpoint: GetClientesRegional
Payload: {"region": "nombre_region"}
"""

import requests
import json
from pathlib import Path
import time

# Regiones de Chile (según SEC)
REGIONES = [
    "Region de Arica y Parinacota",
    "Region de Tarapaca",
    "Region de Antofagasta",
    "Region de Atacama",
    "Region de Coquimbo",
    "Region de Valparaiso",
    "Region Metropolitana de Santiago",
    "Region del Libertador General Bernardo O'Higgins",
    "Region del Maule",
    "Region del Biobio",
    "Region de La Araucania",
    "Region de Los Rios",
    "Region de Los Lagos",
    "Region de Aysen del General Carlos Ibanez del Campo",
    "Region de Magallanes y de la Antartica Chilena",
    "Region de Nuble",
]


def scrape_clientes_region(region_nombre):
    """Obtiene total de clientes para una región."""

    url = "https://apps.sec.cl/INTONLINEv1/ClientesAfectados/GetClientesRegional"

    payload = {"region": region_nombre}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # El API devuelve una lista, tomar el primer elemento
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        else:
            item = data

        return {
            "region": region_nombre,
            "clientes": item.get("CLIENTES"),
            "region_id": item.get("REGION_ID"),
            "success": True,
        }

    except Exception as e:
        print(f"  ❌ Error en {region_nombre}: {e}")
        return {
            "region": region_nombre,
            "clientes": None,
            "region_id": None,
            "success": False,
            "error": str(e),
        }


def scrape_todas_regiones():
    """Scrapea total de clientes para todas las regiones."""

    print("=" * 70)
    print("SCRAPING TOTAL DE CLIENTES POR REGIÓN")
    print("=" * 70)
    print()

    resultados = []

    for i, region in enumerate(REGIONES, 1):
        print(f"📍 {i}/{len(REGIONES)}: {region}...", end=" ")

        resultado = scrape_clientes_region(region)
        resultados.append(resultado)

        if resultado["success"]:
            clientes = int(resultado["clientes"]) if resultado["clientes"] else 0
            print(f"✅ {clientes:,} clientes")
        else:
            print(f"❌ Error")

        # Pausa para no saturar
        time.sleep(0.5)

    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    exitosos = sum(1 for r in resultados if r["success"])
    total_clientes = sum(
        int(r["clientes"]) for r in resultados if r["success"] and r["clientes"]
    )

    print(f"✅ Exitosos: {exitosos}/{len(REGIONES)}")
    print(f"📊 Total clientes nacional: {total_clientes:,}")
    print()

    # Guardar resultados
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "clientes_por_region.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "total_regiones": len(REGIONES),
                    "exitosos": exitosos,
                    "total_clientes_nacional": total_clientes,
                    "fecha_scraping": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                "regiones": resultados,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"💾 Guardado en: {output_file}")

    # Guardar también en CSV para fácil uso
    import pandas as pd

    df = pd.DataFrame(resultados)
    df_exitosos = df[df["success"] == True].copy()
    df_exitosos["clientes"] = df_exitosos["clientes"].astype(int)

    csv_file = output_dir / "clientes_por_region.csv"
    df_exitosos[["region", "region_id", "clientes"]].to_csv(
        csv_file, index=False, encoding="utf-8"
    )
    print(f"💾 CSV guardado en: {csv_file}")

    return resultados


if __name__ == "__main__":
    print("🚀 Iniciando scraping de clientes por región...\n")
    resultados = scrape_todas_regiones()
    print("\n✅ Scraping completado!")
