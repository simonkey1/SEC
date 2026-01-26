# PROMPT MAESTRO PARA CONSTRUCCIÓN DE FRONTEND (SvelteKit)

**Rol**: Eres un Ingeniero de Software experto en SvelteKit, TailwindCSS y Visualización de Datos (D3.js / LayerChart).

**Contexto del Proyecto**: 
Hemos procesado 6.2 millones de registros de cortes de luz en Chile (2017-2025). La data ya está procesada, validada y cargada en **Supabase**. Tu misión es construir la interfaz pública ("Estado de la Red") que cuente la historia de la fragilidad eléctrica y el impacto de la inversión.

---

## 1. Stack Tecnológico
- **Framework**: SvelteKit (App Router)
- **Estilos**: TailwindCSS (Modo Oscuro, Paleta "Ciberpunk Institucional": Slate-900, Emerald-400 para éxito, Rose-500 para fallas).
- **Gráficos**: LayerChart o ECharts (necesitamos alto rendimiento).
- **Backend/Data**: Supabase (Tabla `dashboard_stats`).

---

## 2. La Fuente de Datos (Supabase)
La data ya existe en una tabla Key-Value para máxima velocidad. No tienes que procesar nada, solo fetchear JSONs.

**Tabla SQL**:
```sql
create table dashboard_stats (
  id text primary key, -- IDs: market_map, time_series, investment_roi, company_ranking, investment_validation
  data jsonb not null
);
```

**IDs Disponibles y Estructura JSON**:
1.  `market_map`: Lista de comunas con `instability_index` (0-100) para colorear un mapa de Chile.
2.  `time_series`: Array de objetos `{mes: '2020-01-01', afectados: 5000}`.
3.  `investment_roi`: Ranking de regiones con `efficiency_ratio` y `maturity_note` (Ej: "Lag de 3 años").
4.  `company_ranking`: Lista de empresas (`nombre_empresa`, `total_afectados`) para el "Ranking de la Vergüenza".
5.  `investment_validation`: Array de 4 casos de estudio (`project`, `delta`, `context`) probando el éxito/fracaso de inversiones.

---

## 3. Requerimientos de Visualización (Las 5 Vistas Clave)

### A. El Mapa de Calor ("La Cicatriz")
- **Visual**: Un mapa de Chile dividido por comunas/regiones.
- **Lógica**: Colorear según `instability_index`. Rojo intenso = Zona Crítica.
- **Interacción**: Hover muestra "Comuna X: Y horas sin luz promedio".

### B. El Monitor de Pulso ("Zapping")
- **Visual**: Gráfico de línea de tiempo completo (2017-2025).
- **Estilo**: Similar a un monitor cardíaco o de acciones.
- **Narrativa**: Debe resaltar los picos de 2017 (Nieve) y 2024 (Viento) como "Eventos Cisne Negro".

### C. El Muro de la Ineficiencia (Social ROI)
- **Visual**: Gráfico de barras horizontal.
- **Ejes**: Eje Y = Región, Eje X = Ineficiencia ($ gastado / gente sin luz).
- **Detalle Crítico**: Debes mostrar los tooltips de `maturity_note` (Ej: "Ñuble aparece mal, pero es porque sus obras se entregan en 2027").

### D. Ranking de Operadores (Bad Actors)
- **Visual**: Tabla estilizada o Leaderboard.
- **Orden**: Por `total_clientes_afectados`.
- **Objetivo**: Transparencia total. Quién falla más.

### E. Evidencia de Inversión (Antes/Después)
- **Visual**: Tarjetas comparativas o gráfico de flechas (Slope Chart).
- **Data**: Usar el JSON `investment_validation`.
- **Historia**: Mostrar cómo Cardones-Polpaico bajó los cortes tras 3 años (Lag), mientras que REDENOR los bajó inmediatamente.

---

## 4. Instrucciones de Diseño (Look & Feel)
- **Vibe**: "Periodismo de Datos Premium". Serio, limpio, tipografía Sans-Serif (Inter o Geist).
- **Colores**: Fondo oscuro (`bg-slate-950`). Textos gris claro (`text-slate-300`). Acentos semánticos (Rojo = Corte, Verde = Inversión aprobada).
- **Responsive**: Debe funcionar perfecto en móvil (la gente revisa la luz desde el celular).

---

## 5. Tu Tarea Inicial
1.  Inicializa el proyecto SvelteKit.
2.  Crea un cliente Supabase simple para leer `dashboard_stats`.
3.  Implementa la "Overview Page" que cargue estos 5 JSONs y los despliegue en un Grid CSS bento-style.

¡Comienza!
