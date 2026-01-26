"""Análisis detallado de datos de enero 2017 incluyendo duración de interrupciones."""

import json
from pathlib import Path
from collections import Counter
import re


def parse_duration(duration_str):
    """Parse 'X Dias Y Horas Z Minutos' to total hours."""
    if not duration_str:
        return 0

    days = hours = minutes = 0

    # Extract days
    day_match = re.search(r"(\d+)\s*Dias?", duration_str)
    if day_match:
        days = int(day_match.group(1))

    # Extract hours
    hour_match = re.search(r"(\d+)\s*Horas?", duration_str)
    if hour_match:
        hours = int(hour_match.group(1))

    # Extract minutes
    min_match = re.search(r"(\d+)\s*Minutos?", duration_str)
    if min_match:
        minutes = int(min_match.group(1))

    return days * 24 + hours + minutes / 60


def analyze_enero_2017():
    """Análisis completo de enero 2017."""

    output_file = Path("outputs") / "enero_2017_completo.json"

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data["metadata"]
    results = data["datos"]

    print("=" * 70)
    print("ANÁLISIS DETALLADO: ENERO 2017")
    print("=" * 70)

    # Estadísticas básicas
    total_records = sum(len(r["data"]) for r in results)
    total_clientes = 0
    duraciones = []
    empresas_duracion = {}
    regiones_duracion = {}

    empresas = []
    regiones = []

    for snapshot in results:
        for record in snapshot["data"]:
            empresas.append(record.get("NOMBRE_EMPRESA", "N/A"))
            regiones.append(record.get("NOMBRE_REGION", "N/A"))
            clientes = record.get("CLIENTES_AFECTADOS", 0)
            total_clientes += clientes

            # Analizar duración
            duration_str = record.get("ACTUALIZADO_HACE", "")
            duration_hours = parse_duration(duration_str)

            if duration_hours > 0:
                duraciones.append(duration_hours)

                # Por empresa
                empresa = record.get("NOMBRE_EMPRESA", "N/A")
                if empresa not in empresas_duracion:
                    empresas_duracion[empresa] = []
                empresas_duracion[empresa].append(duration_hours)

                # Por región
                region = record.get("NOMBRE_REGION", "N/A")
                if region not in regiones_duracion:
                    regiones_duracion[region] = []
                regiones_duracion[region].append(duration_hours)

    print(f"\n📊 RESUMEN GENERAL")
    print(f"  Total de interrupciones: {total_records:,}")
    print(f"  Total de clientes afectados: {total_clientes:,}")
    print(f"  Promedio clientes/interrupción: {total_clientes / total_records:.1f}")

    # Análisis de duración
    if duraciones:
        avg_duration = sum(duraciones) / len(duraciones)
        max_duration = max(duraciones)

        # Categorías de duración
        cortas = sum(1 for d in duraciones if d < 24)  # < 1 día
        medias = sum(1 for d in duraciones if 24 <= d < 168)  # 1-7 días
        largas = sum(1 for d in duraciones if d >= 168)  # > 7 días

        print(f"\n⏱️ DURACIÓN DE INTERRUPCIONES")
        print(
            f"  Duración promedio: {avg_duration:.1f} horas ({avg_duration / 24:.1f} días)"
        )
        print(
            f"  Duración máxima: {max_duration:.1f} horas ({max_duration / 24:.1f} días)"
        )
        print(f"\n  Por categoría:")
        print(
            f"    Cortas (< 1 día): {cortas:,} ({cortas / len(duraciones) * 100:.1f}%)"
        )
        print(
            f"    Medias (1-7 días): {medias:,} ({medias / len(duraciones) * 100:.1f}%)"
        )
        print(
            f"    Largas (> 7 días): {largas:,} ({largas / len(duraciones) * 100:.1f}%)"
        )

    # Top empresas por duración promedio
    print(f"\n🏢 TOP 5 EMPRESAS CON INTERRUPCIONES MÁS LARGAS")
    empresa_avg = {
        emp: sum(durs) / len(durs)
        for emp, durs in empresas_duracion.items()
        if len(durs) > 10
    }
    for empresa, avg_dur in sorted(
        empresa_avg.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"  {empresa}: {avg_dur:.1f}h ({avg_dur / 24:.1f} días)")

    # Top regiones por duración promedio
    print(f"\n🗺️ TOP 5 REGIONES CON INTERRUPCIONES MÁS LARGAS")
    region_avg = {
        reg: sum(durs) / len(durs)
        for reg, durs in regiones_duracion.items()
        if len(durs) > 10
    }
    for region, avg_dur in sorted(region_avg.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]:
        print(f"  {region}: {avg_dur:.1f}h ({avg_dur / 24:.1f} días)")

    # Top empresas por frecuencia
    print(f"\n🏢 TOP 5 EMPRESAS CON MÁS INTERRUPCIONES")
    empresa_counts = Counter(empresas)
    for empresa, count in empresa_counts.most_common(5):
        pct = (count / total_records) * 100
        print(f"  {empresa}: {count:,} ({pct:.1f}%)")

    # Top regiones por frecuencia
    print(f"\n🗺️ TOP 5 REGIONES CON MÁS INTERRUPCIONES")
    region_counts = Counter(regiones)
    for region, count in region_counts.most_common(5):
        pct = (count / total_records) * 100
        print(f"  {region}: {count:,} ({pct:.1f}%)")

    print("\n" + "=" * 70)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 70)

    # Guardar resumen
    summary = {
        "periodo": "Enero 2017",
        "total_interrupciones": total_records,
        "total_clientes_afectados": total_clientes,
        "duracion_promedio_horas": avg_duration if duraciones else 0,
        "duracion_maxima_horas": max_duration if duraciones else 0,
        "top_empresas_frecuencia": dict(empresa_counts.most_common(5)),
        "top_regiones_frecuencia": dict(region_counts.most_common(5)),
        "top_empresas_duracion": dict(
            sorted(empresa_avg.items(), key=lambda x: x[1], reverse=True)[:5]
        ),
        "top_regiones_duracion": dict(
            sorted(region_avg.items(), key=lambda x: x[1], reverse=True)[:5]
        ),
    }

    summary_file = Path("outputs") / "enero_2017_analisis.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Análisis guardado en: {summary_file}")


if __name__ == "__main__":
    analyze_enero_2017()
