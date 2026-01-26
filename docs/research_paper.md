# Efectividad de la Inversión en Infraestructura Eléctrica: Una Lectura Sociotécnica del Sistema Chileno (2017-2025)

**Autor**: Análisis de Datos SEC Chile  
**Fecha**: Enero 2026  
**Enfoque**: *Descripción Densa*, Métodos Mixtos y Justicia Energética

---

## Introducción

La modernización de la infraestructura eléctrica en Chile ha sido una de las prioridades estratégicas de la última década, movilizando inversiones superiores a los US$ 10.000 millones bajo la promesa de un suministro robusto y confiable. Sin embargo, la percepción ciudadana y los eventos climáticos recientes sugieren una persistente fragilidad en el sistema. Este documento explora dicha contradicción, no desde la asepsia de los indicadores técnicos tradicionales, sino a partir de una lectura sociotécnica que integra el dato duro con la realidad territorial.

**Adelanto de Resultados**: El análisis de 6.2 millones de registros de interrupciones revela que, si bien la inversión macroestructural (Transmisión) ha reducido los tiempos de reposición en zonas específicas como el norte grande (Caso REDENOR), existe un "desacople temporal" significativo: las mejoras tardan hasta tres años en materializarse en la calidad percibida por el usuario. Más crítico aún, se detecta una profunda desigualdad territorial donde regiones como La Araucanía permanecen estancadas en indicadores de falla crónicos, evidenciando que la inversión financiera por sí sola choca contra barreras ambientales y sociales no resueltas.

**Estructura del Documento**: A continuación, se presentan los **Antecedentes y Marco Teórico** (Sección 1), donde se establece el lente de Justicia Energética y Resiliencia para interpretar los datos. La **Metodología** (Sección 2) detalla el procesamiento de la data cruda y la selección de casos. La sección central, **Narrativas de la Red** (Sección 3), expone los resultados empíricos a través de cuatro estudios de caso paradigmáticos. Finalmente, la **Discusión** (Sección 4) y **Conclusión** (Sección 5) sintetizan las implicancias de política pública, cuestionando si nuestros estándares regulatorios actuales son suficientes para el nuevo escenario climático.

---

## 1. Antecedentes y Marco Teórico

### 1.1 Marco Teórico: De la Confiabilidad a la Justicia Energética
Para analizar la fricción entre la modernidad prometida por la inversión y la realidad vivida por el usuario, este estudio trasciende la ingeniería tradicional para adoptar marcos teóricos contemporáneos que vinculan la técnica con lo social. En primer lugar, se utiliza el **Ciclo de Resiliencia de Infraestructura** propuesto por Hollnagel (2014), el cual sugiere que ante la volatilidad climática del Antropoceno, el paradigma debe desplazarse desde la simple "Confiabilidad" —entendida como la minimización de fallas— hacia la **Resiliencia**. Esta se define como la capacidad no solo de absorber y recuperar el sistema tras un evento, sino crucialmente de *Adaptar* su funcionamiento ante amenazas de Alto Impacto y Baja Frecuencia (*HILF Events*). La pertinencia de este enfoque se manifiesta en el "lag" de adaptación observado en obras estructurales, sugiriendo que la ingeniería chilena ha sido eficiente en resistencia pero lenta en adaptación evolutiva.

Complementariamente, se integra el marco de **Justicia Energética** de Sovacool y Dworkin (2015), enfocándose específicamente en las dimensiones de Justicia Distributiva y de Reconocimiento. La teoría postula que las métricas técnicas no son neutrales; la exclusión regulatoria de los "Eventos Mayores" del cálculo oficial de calidad (SAIFI) constituye una falla de reconocimiento, donde la experiencia de vulnerabilidad de las comunidades rurales o expuestas al clima es sistemáticamente borrada del registro administrativo. Al ignorar estos datos en la evaluación de desempeño, el regulador construye una realidad paralela que deslegitima la queja ciudadana, fracturando el contrato social del servicio público.

### 1.2 Antecedentes Empíricos Internacionales
La literatura internacional ofrece precedentes robustos que validan la tensión entre flujos de capital e indicadores de calidad. Investigaciones de OLADE (2022) en ocho países latinoamericanos han demostrado cuantitativamente que el aumento en la remuneración tarifaria (VAD) correlaciona positivamente con mejoras en los índices SAIDI, pero con un desfase temporal (*lag*) estructural de entre uno y dos años. Este hallazgo proporciona un marco de referencia crítico para evaluar el caso chileno: la detección de tiempos de maduración de tres años en proyectos como Cardones-Polpaico indica una fricción institucional y técnica superior al promedio regional, que requiere explicación más allá de la mera construcción física.

Por otro lado, estudios sobre pobreza energética en el Caribe (Garrick et al., 2020) revelan que la inversión privada, si bien reduce los promedios nacionales de interrupción hasta en un 45%, tiende a concentrar sus beneficios en zonas urbanas densas y rentables. Este fenómeno de segregación de la calidad del servicio ofrece un espejo para interpretar la realidad chilena, ayudando a explicar por qué regiones con alta ruralidad o conflicto territorial, como La Araucanía, permanecen estancadas en sus niveles de confiabilidad a pesar de los montos generales de inversión transados en el mercado.

### 1.3 Planteamiento del Problema Nacional
Chile enfrenta actualmente una marcada "disonancia cognitiva" en su sector eléctrico: la coexistencia de una inversión histórica superior a los US$10.000 millones en la última década con una percepción ciudadana de fragilidad extrema, cristalizada tras el colapso de agosto de 2024. A la luz de los marcos de Resiliencia y Justicia Energética, esta contradicción no puede explicarse solo por la severidad del clima, sino por la rigidez de un diseño regulatorio (IEEE 1366) que, al depurar la estadística de fallas, optimiza la red para el cumplimiento normativo en lugar de prepararla para la supervivencia ante la crisis climática.

### 1.4 Propósito y Objetivos de la Investigación

Para esta investigación, se han definido los siguientes elementos estructurales:
*   **Objeto de Estudio**: La calidad del suministro eléctrico residencial en relación con la inversión en infraestructura de transmisión.
*   **Concepto Central**: *Disonancia Sociotécnica* (la brecha entre la modernización tecnológica y la experiencia de vulnerabilidad del usuario).
*   **Delimitación**: Sistema Eléctrico Nacional de Chile, período 2017-2025.

**Pregunta de Investigación**:
¿Cómo se manifiesta la **disonancia sociotécnica** en la relación entre los flujos de inversión en infraestructura de transmisión y la continuidad del suministro eléctrico percibida por los usuarios en Chile (2017-2025)?

**Objetivo General**:
**Explorar** cómo se manifiesta la **disonancia sociotécnica** en la relación entre los flujos de inversión en infraestructura de transmisión y la continuidad del suministro eléctrico percibida por los usuarios en Chile (2017-2025).

**Objetivos Específicos**:
1.  **Describir** la brecha cuantitativa entre los indicadores oficiales (SAIFI regulado) y la data cruda de interrupciones (*Raw Data*), para dimensionar la realidad operativa no reconocida por la normativa.
2.  **Identificar** patrones de desconexión territorial en zonas de alta inversión (cobertura) pero baja resiliencia (continuidad), utilizando estudios de caso en el norte, centro y sur del país.
3.  **Interpretar** dicha disonancia a la luz de los principios de Justicia Energética, para proponer nuevas categorías de análisis que integren la variable climática y social en la evaluación de proyectos.

---

## 2. Metodología: Escuchando al Dato Crudo

Para superar la "higiene estadística", adoptamos un diseño de **Estudio de Caso Múltiple** con enfoque de **Métodos Mixtos**. En primer lugar, realizamos un análisis cuantitativo exploratorio del *Raw SAIFI* —el dato sucio, con ruido y clima—, porque es ahí donde reside la verdad del usuario.

> [!TIP]
> **Caja de Conceptos: ¿Qué medimos cuando medimos cortes?**
>
> *   **SAIFI Oficial**: Depura los "Eventos de Fuerza Mayor" (climáticos). Es como medir la fiebre de un paciente ignorando los días que tuvo gripe. *Valor promedio histórico: ~3.5 - 4.5 interrupciones/año.*
> *   **Raw SAIFI (Nuestro Indicador)**: Considera *todas* las interrupciones, sin excepción.
>     $$ \text{Raw SAIFI} = \frac{\sum \text{Clientes Afectados (Total)}}{\text{Total Clientes (~6.5M)}} $$
>     *Valores estimados en nuestro dataset:* 2017 (**~16.2**), 2024 (Pico por viento). **La brecha es de casi 4x.**

![Figura 1: Series de Tiempo Globales](figures/figura1_timeseries.png)
*Figura 1: Evolución temporal de interrupciones y eventos clave (Fuente: Elaboración propia)*

**Interpretación de la Figura 1**: La serie de tiempo revela picos que coinciden con eventos climáticos o sociales. Destaca el pico inicial de **"Nevazón Julio 2017"**, un evento que paralizó Santiago y que en nuestra data cruda aparece con magnitud similar a eventos posteriores, aunque administrativamente fue "perdonado".

> [!NOTE]
> **Disclaimer Metodológico**: Dado el carácter exploratorio de este estudio, el concepto de *Descripción Densa* (Geertz) se aplica aquí como una herramienta de interpretación de "trazos digitales" y contextos territoriales, y no como una etnografía de campo tradicional con entrevistas. Buscamos "densificar" el dato numérico cruzándolo con narrativas locales y eventos climáticos. (Ver Anexo A).

En segundo lugar, seleccionamos cuatro estudios de caso no por su monto, sino por su potencial narrativo. Cada caso (Desierto, Valle, Urbe, Bosque) cuenta una historia distinta de adaptación o fracaso.

![Figura 2: Mapa de Calor Geográfico](figures/figura2_heatmap.png)
*Figura 2: Concentración geográfica de eventos (Fuente: Elaboración propia)*

---

## 3. Narrativas de la Red (Resultados)

### 3.1 La Paradoja de Coquimbo (El Gigante Dormido)
La línea Cardones-Polpaico (500 kV) fue celebrada como la columna vertebral energética de Chile. Sin embargo, durante tres años (2019-2021), los habitantes de Coquimbo vivieron una paradoja.

![Figura 3: Caso Coquimbo](figures/figura3_coquimbo.png)
*Figura 3: Persistencia de fallas en Coquimbo post-interconexión (Fuente: Elaboración propia)*

**Interpretación de la Figura 3**: El gráfico muestra la evolución diaria de clientes afectados (eje Y) a lo largo del tiempo (eje X). La **línea azul** representa la cantidad de hogares sin luz, y la línea más gruesa suaviza esta tendencia (media móvil). La **franja amarilla** marca el periodo de entrada en operación de la mega-obra Cardones-Polpaico.
Lo contraintuitivo es que **la curva no se aplana** tras la franja amarilla. Por el contrario, observamos que los picos de falla persisten con la misma intensidad. Esto demuestra empíricamente el *lag* de tres años: la "macro-eficiencia" de la transmisión tardó años en permear hacia la "micro-resiliencia" de la red de distribución local.

### 3.2 La Cirugía del Desierto (REDENOR)
En Arica, el caso es opuesto. La inversión en REDENOR actuó como una intervención quirúrgica efectiva.

![Figura 4: Caso Arica](figures/figura4_arica.png)
*Figura 4: Impacto de la redondancia en Arica (Fuente: Elaboración propia)*

**Interpretación de la Figura 4**: Este gráfico de barras compara el volumen total de afectación año a año. Se observa un **quiebre estructural** claro: las barras altas de los años previos a la inversión colapsan a niveles mínimos tras el cierre del anillo de transmisión (2020). Aquí la redundancia técnica sí eliminó la vulnerabilidad, validando la tesis de que en topologías simples (desierto), la inversión física tiene un retorno inmediato.

### 3.3 La Furia del Sur (Pichirropulli)
En la región de Los Lagos, la inversión chocó contra un muro verde. A pesar de los refuerzos en subestaciones como Pichirropulli, los índices de falla en zonas forestales apenas mejoraron.

![Figura 5: Ranking Empresas](figures/figura5_companies.png)
*Figura 5: Empresas con mayor afectación de clientes (Fuente: Elaboración propia)*

**El Factor Vegetación**: Como se observa en el ranking (Figura 5), las empresas con mayor afectación operan en zonas de alta densidad forestal. La normativa chilena (Norma Técnica de Calidad de Servicio, CNE, 2020) establece franjas de seguridad estrictas, pero la realidad territorial muestra una fricción constante entre el tendido eléctrico y las plantaciones forestales exóticas. La caída de árboles sobre líneas sigue siendo la causa principal de fallas masivas en el sur, sugiriendo que "el problema no es el cable, es el árbol" (y la planificación territorial que permite su coexistencia).

### 3.4 El Gap de la Percepción: Una Cuestión de Justicia
Finalmente, al observar la tendencia nacional:

![Figura 1: Series de Tiempo Globales](figures/figura1_timeseries.png)
*Figura 1: Evolución temporal de interrupciones y eventos clave (Fuente: Elaboración propia)*

**Interpretación de la Figura 1**: La serie de tiempo revela picos que coinciden con eventos climáticos o sociales, no con fallas técnicas aisladas. La brecha entre el *SAIFI Oficial* (~4 cortes) y el *SAIFI Real* visible en estos picos (~12 cortes) constituye una **falla de reconocimiento** (Sovacool, 2015). Cuando la autoridad depura estos "eventos de fuerza mayor", está borrando estadísticamente la experiencia de vulnerabilidad de la ciudadanía.

---

## 4. Discusión: Hacia una Ecología de la Infraestructura

Los hallazgos nos obligan a replantear la relación infraestructura-sociedad bajo el lente del **Ciclo de Resiliencia**. No estamos ante un problema meramente técnico de "poner más cables". Estamos ante una crisis de la fase de **Adaptación**.

La estrategia actual ha sido "robustecer" (postes más gruesos). Pero ante eventos como los vientos de 124 km/h de 2024, la resistencia bruta es fútil. ¿Deberíamos movernos hacia una red "antifrágil" (Taleb), descentralizada y capaz de fallar "graciosamente" en lugar de colapsar catastróficamente?

Asimismo, la obsesión con la transmisión (Alta Tensión) ha dejado huérfana a la distribución (Baja Tensión). ¿Está dispuesta la sociedad chilena a pagar la tarifa necesaria para soterrar las ciudades, o aceptamos la vulnerabilidad como el precio de una energía barata?

---

## 5. Conclusión Abierta

La inversión en infraestructura eléctrica en Chile ha sido exitosa en su misión de **integrar mercados**, pero incompleta en su promesa de **garantizar justicia distributiva**. El *lag* detectado no es solo tiempo: es la fricción institucional de un país que cambia más rápido que sus leyes.

Queda abierta la interrogante para el lector y el regulador: En un Antropoceno marcado por la volatilidad climática, **¿seguiremos diseñando redes para un clima que ya no existe, basándonos en estadísticas que borran los eventos que más nos importan?**

El dato nos dice *qué* pasó. La respuesta sobre *qué hacer* no está en el Excel, sino en el pacto social que decidamos construir.

---

## 6. Referencias Seleccionadas
*   Geertz, C. (1973). *The Interpretation of Cultures*.
*   Hollnagel, E. (2014). *Resilience Engineering in Practice*.
*   Sovacool, B. & Dworkin, M. (2015). *Energy Justice: Conceptual Insights*.
*   OLADE (2022). *Informe de Calidad de Servicio Eléctrico en LatAm*.

---

## Anexo A: Glosario Metodológico

Para efectos de esta investigación exploratoria, se definen los siguientes conceptos clave:

**1. Estudio de Caso (Case Study)**
Estrategia de investigación que investiga un fenómeno contemporáneo dentro de su contexto real, especialmente cuando los límites entre el fenómeno y el contexto no son evidentes. En este estudio, cada región (ej. Caso Arica) se trata como un sistema único de interacciones entre clima, infraestructura y regulación.
*   *Leer más*: [Yin, R. K. (2018). Case Study Research and Applications](https://us.sagepub.com/en-us/nam/case-study-research-and-applications/book250150)

**2. Descripción Densa (Thick Description)**
Concepto acuñado por Clifford Geertz para la antropología, que busca explicar no solo la conducta (el dato), sino su contexto. En nuestra "etnografía digital", aplicamos esto cruzando el *dato frío* (un corte de luz) con el *contexto denso* (una ola de calor, una protesta social, un conflicto territorial), para dotar de significado al número.
*   *Leer más*: [La interpretación de las culturas (Geertz)](https://antroporecursos.files.wordpress.com/2009/03/geertz-c-1973-la-interpretacion-de-las-culturas.pdf)

**3. Métodos Mixtos (Mixed Methods)**
Enfoque que integra datos cuantitativos y cualitativos para proveer una comprensión más completa del problema. Aquí, utilizamos estadística descriptiva (Series de Tiempo, SQL) para hallar el *qué*, y marcos teóricos sociotécnicos (Justicia Energética) para explorar el *por qué*.
