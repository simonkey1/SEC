# 📈 Legacy: Visualización y Análisis en PowerBI

Esta documentación conserva las instrucciones originales para utilizar los datos generados por este proyecto en **PowerBI Desktop**. Aunque el enfoque actual del proyecto es el desarrollo de un Dashboard Web, este flujo sigue siendo funcional para análisis rápidos.

---

## 🛠️ Configuración Inicial

Para poder manipular los datos en PowerBI, sigue estos pasos:

1.  **Importar Datos**:
    *   Abrir PowerBI Desktop.
    *   Ir a `Obtener datos` -> `Texto/CSV`.
    *   Seleccionar `outputs/clientes_afectados_tiempo_real.csv`.
2.  **Transformación (Power Query)**:
    *   Es necesario normalizar los nombres de las regiones para que coincidan con los mapas estándar de Chile en PowerBI.

### Código M Sugerido
En el Editor Avanzado de Power Query, puedes pegar este código para automatizar la limpieza:

```m
let
    Source = Csv.Document(File.Contents("C:\Ruta\Al\Proyecto\outputs\clientes_afectados_tiempo_real.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"ID_UNICO", type text}, 
        {"TIMESTAMP", type datetime}, 
        {"CLIENTES_AFECTADOS", Int64.Type},
        {"REGION", type text}
    }),
    #"Added Custom" = Table.AddColumn(#"Changed Type", "REGION_CORREGIDA", each "Región de " & [REGION]),
    
    // Reemplazos para compatibilidad de mapas
    Reemplazos = {
        {"Región de Metropolitana", "Región Metropolitana de Santiago"},
        {"Región de Tarapaca", "Región de Tarapacá"},
        {"Región de Magallanes", "Región de Magallanes y Antártica Chilena"},
        {"Región de Valparaiso", "Región de Valparaíso"}
    },
    Resultado = List.Accumulate(Reemplazos, #"Added Custom", (tabla, par) => Table.ReplaceValue(tabla, par{0}, par{1}, Replacer.ReplaceText, {"REGION_CORREGIDA"}))
in
    Resultado
```

---

## 📊 Métricas DAX Útiles

Para enriquecer tu tablero, puedes crear las siguientes medidas:

### 1. Última Actualización
Muestra la hora exacta del último reporte capturado:
```dax
Última Actualización = MAX('Tabla'[TIMESTAMP])
```

### 2. Variación Nominal
Compara el impacto actual con la medición inmediatamente anterior:
```dax
Variación Afectados = 
VAR Ultimo = MAX('Tabla'[TIMESTAMP])
VAR Anterior = CALCULATE(MAX('Tabla'[TIMESTAMP]), 'Tabla'[TIMESTAMP] < Ultimo)
VAR SumaUltimo = CALCULATE(SUM('Tabla'[CLIENTES_AFECTADOS]), 'Tabla'[TIMESTAMP] = Ultimo)
VAR SumaAnterior = CALCULATE(SUM('Tabla'[CLIENTES_AFECTADOS]), 'Tabla'[TIMESTAMP] = Anterior)
RETURN SumaUltimo - SumaAnterior
```

---

## 🗺️ Mapa de Chile (Shape Map)
Si deseas utilizar el mapa por formas:
1.  Habilita `Shape Map Visual` en `Opciones -> Características de Versión Preliminar`.
2.  Carga el archivo `.topojson` o `.json` que se encuentra en `maps/poligonos_chile/`.
3.  Usa la columna `REGION_CORREGIDA` en el campo **Location**.

---
*Este documento se mantiene por razones históricas y para usuarios que prefieran soluciones No-Code para visualización.*
