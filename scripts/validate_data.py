"""Script de validación de datos transformados con visualizaciones.

Este script lee el CSV generado por el Transformer y produce:
- Estadísticas descriptivas
- Detección de problemas de limpieza de strings
- Gráficos de distribución y ranking
- Reporte de anomalías

Uso:
    python scripts/validate_data.py
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def validar_limpieza_strings(df: pd.DataFrame) -> dict:
    """Detecta problemas de normalización en strings."""
    problemas = {}
    
    # Detectar espacios en blanco
    if df['COMUNA'].str.contains(r'^\s|\s$', regex=True).any():
        problemas['espacios_comuna'] = df[df['COMUNA'].str.contains(r'^\s|\s$', regex=True)]['COMUNA'].unique()
    
    # Detectar duplicados por mayúsculas/minúsculas
    comunas_upper = df['COMUNA'].str.upper().unique()
    comunas_original = df['COMUNA'].unique()
    if len(comunas_upper) != len(comunas_original):
        problemas['duplicados_caps'] = True
    
    return problemas


def generar_graficos(df: pd.DataFrame, output_path: str = "outputs/validacion_datos.png"):
    """Genera visualizaciones de validación."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Validación de Datos Transformados - ETL Cortes Eléctricos', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Distribución de clientes afectados
    # Usar bins adaptativos: menos bins para pocos datos, más bins para muchos datos
    num_bins = min(max(len(df) // 2, 3), 20)  # Entre 3 y 20 bins
    axes[0, 0].hist(df['CLIENTES_AFECTADOS'], bins=num_bins, edgecolor='black', color='steelblue')
    axes[0, 0].set_title(f'Distribución de Clientes Afectados ({len(df)} cortes)', fontweight='bold')
    axes[0, 0].set_xlabel('Clientes')
    axes[0, 0].set_ylabel('Frecuencia (cantidad de cortes)')
    axes[0, 0].grid(alpha=0.3)
    
    # Gráfico 2: Top 10 empresas
    top_empresas = df.groupby('EMPRESA')['CLIENTES_AFECTADOS'].sum().nlargest(10)
    axes[0, 1].barh(top_empresas.index, top_empresas.values, color='coral')
    axes[0, 1].set_title('Top 10 Empresas (Clientes Afectados)', fontweight='bold')
    axes[0, 1].set_xlabel('Clientes Afectados')
    axes[0, 1].invert_yaxis()
    axes[0, 1].grid(axis='x', alpha=0.3)
    
    # Gráfico 3: Top 10 comunas
    top_comunas = df.groupby('COMUNA')['CLIENTES_AFECTADOS'].sum().nlargest(10)
    axes[1, 0].barh(top_comunas.index, top_comunas.values, color='seagreen')
    axes[1, 0].set_title('Top 10 Comunas Afectadas', fontweight='bold')
    axes[1, 0].set_xlabel('Clientes Afectados')
    axes[1, 0].invert_yaxis()
    axes[1, 0].grid(axis='x', alpha=0.3)
    
    # Gráfico 4: Distribución de antigüedad
    axes[1, 1].hist(df['DIAS_ANTIGUEDAD'], bins=30, edgecolor='black', color='gold')
    axes[1, 1].set_title('Distribución de Antigüedad de Cortes', fontweight='bold')
    axes[1, 1].set_xlabel('Días desde el corte')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Gráficos guardados en: {output_path}")
    plt.show()


def main():
    """Función principal de validación."""
    csv_path = "outputs/clientes_afectados_tiempo_real.csv"
    
    # Verificar existencia del CSV
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró {csv_path}")
        print("   Ejecuta primero el scraper + transformer para generar datos.")
        return
    
    # Cargar datos
    print("=== VALIDACIÓN DE DATOS TRANSFORMADOS ===\n")
    print(f"📂 Cargando: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✅ {len(df)} registros cargados\n")
    
    # 1. Estadísticas básicas
    print("📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total de clientes afectados: {df['CLIENTES_AFECTADOS'].sum():,}")
    print(f"   • Promedio por corte: {df['CLIENTES_AFECTADOS'].mean():.1f}")
    print(f"   • Mediana: {df['CLIENTES_AFECTADOS'].median():.0f}")
    print(f"   • Máximo en un solo corte: {df['CLIENTES_AFECTADOS'].max():,}")
    print(f"   • Comunas únicas: {df['COMUNA'].nunique()}")
    print(f"   • Empresas únicas: {df['EMPRESA'].nunique()}")
    print(f"   • Regiones únicas: {df['REGION'].nunique()}\n")
    
    # 2. Top rankings
    print("🏆 TOP 5 COMUNAS MÁS AFECTADAS:")
    top_comunas = df.groupby('COMUNA')['CLIENTES_AFECTADOS'].sum().nlargest(5)
    for i, (comuna, clientes) in enumerate(top_comunas.items(), 1):
        print(f"   {i}. {comuna}: {clientes:,} clientes")
    
    print("\n🏭 TOP 5 EMPRESAS CON MÁS CORTES:")
    top_empresas = df.groupby('EMPRESA')['CLIENTES_AFECTADOS'].sum().nlargest(5)
    for i, (empresa, clientes) in enumerate(top_empresas.items(), 1):
        print(f"   {i}. {empresa}: {clientes:,} clientes")
    
    # 3. Validación de limpieza
    print("\n🔍 VALIDACIÓN DE LIMPIEZA DE STRINGS:")
    problemas = validar_limpieza_strings(df)
    
    if not problemas:
        print("   ✅ No se detectaron problemas de normalización")
    else:
        if 'espacios_comuna' in problemas:
            print(f"   ⚠️ Comunas con espacios: {problemas['espacios_comuna']}")
        if 'duplicados_caps' in problemas:
            print("   ⚠️ DUPLICADOS POR MAYÚSCULAS DETECTADOS")
    
    # 4. Detección de anomalías
    print("\n⚠️ DETECCIÓN DE ANOMALÍAS:")
    if df['CLIENTES_AFECTADOS'].max() > 100000:
        print(f"   🚨 Valor sospechoso: {df['CLIENTES_AFECTADOS'].max():,} clientes")
    
    if df['DIAS_ANTIGUEDAD'].max() > 365:
        print(f"   🚨 Corte muy antiguo: {df['DIAS_ANTIGUEDAD'].max()} días")
    
    if (df['DIAS_ANTIGUEDAD'] < 0).any():
        print("   🚨 Días de antigüedad NEGATIVOS detectados (error en cálculo)")
    
    if not problemas and df['CLIENTES_AFECTADOS'].max() <= 100000:
        print("   ✅ No se detectaron anomalías críticas")
    
    # 5. Distribución de antigüedad
    print("\n⏰ DISTRIBUCIÓN DE ANTIGÜEDAD:")
    cortes_recientes = (df['DIAS_ANTIGUEDAD'] <= 1).sum()
    cortes_1_7 = ((df['DIAS_ANTIGUEDAD'] > 1) & (df['DIAS_ANTIGUEDAD'] <= 7)).sum()
    cortes_antiguos = (df['DIAS_ANTIGUEDAD'] > 7).sum()
    
    print(f"   • ≤ 1 día: {cortes_recientes} cortes ({cortes_recientes/len(df)*100:.1f}%)")
    print(f"   • 2-7 días: {cortes_1_7} cortes ({cortes_1_7/len(df)*100:.1f}%)")
    print(f"   • > 7 días: {cortes_antiguos} cortes ({cortes_antiguos/len(df)*100:.1f}%)")
    
    # 6. Generar gráficos
    print("\n📊 Generando visualizaciones...")
    generar_graficos(df)
    
    print("\n" + "="*50)
    print("✅ Validación completada exitosamente")
    print("="*50)


if __name__ == "__main__":
    main()
