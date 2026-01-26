# Guía: Obtención de Datos SEIA

## Método Manual (Recomendado)

### Paso 1: Acceder al Buscador
URL: https://seia.sea.gob.cl/busqueda/buscarProyecto.php

### Paso 2: Configurar Filtros

**Configuración Recomendada**:

| Campo | Valor | Notas |
|-------|-------|-------|
| **Región** | -- Seleccionar -- | Dejar TODAS (no filtrar) |
| **Comuna** | -- Seleccionar -- | Dejar TODAS (no filtrar) |
| **Tipo de Presentación** | Ambos | Incluir DIA y EIA |
| **Estado del Proyecto** | Aprobado | Solo proyectos aprobados |
| **Fecha de Presentación** | (vacío) | No filtrar |
| **Fecha de Calificación** | Desde: 01/01/2017<br>Hasta: 31/12/2025 | Período completo |
| **Sector Productivo** | Energía | Ya seleccionado |
| **Razón de Ingreso** | -- Seleccionar -- | No filtrar |
| **Tipo de Proyecto** | Ver códigos abajo ⬇️ | Seleccionar específicos |

**Códigos de Tipo de Proyecto** (seleccionar estos 4):
- ✅ **DS95/DS40-b1**: Líneas de transmisión eléctrica de alto voltaje
- ✅ **DS95/DS40/DS17-b**: Líneas de transmisión eléctrica de alto voltaje y sus subestaciones  
- ✅ **DS95/DS40/DS17-c**: Centrales generadoras de energía mayores a 3 MW
- ✅ **DS95/DS40/DS17-b2**: Subestaciones

### Paso 3: Exportar Datos
- Buscar botón "Exportar a Excel" o "Descargar CSV"
- Guardar como `seia_proyectos_energia_2017_2025.csv`

### Paso 4: Colocar en Carpeta
```
luz/
└── data/
    └── raw/
        └── seia_inversion/
            └── seia_proyectos_energia_2017_2025.csv
```

---

## Variables Importantes

Al descargar, asegúrate de que incluya:
- **Nombre del proyecto**
- **Titular** (empresa responsable)
- **Región**
- **Monto inversión** (USD o CLP)
- **Fecha de aprobación**
- **Tipo de proyecto** (distribución, generación, transmisión)
- **Estado actual**

---

## Método Alternativo: API (Si existe)

Algunas plataformas gubernamentales tienen APIs. Verificar en:
- https://datos.gob.cl/
- Documentación SEIA

---

## Procesamiento Posterior

Una vez descargado, usar script de procesamiento:
```bash
python scripts/process_seia_data.py
```
