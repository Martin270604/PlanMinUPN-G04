# T2 M01B — Plan conversacional G04

## Estado de sesión

- **Protocolo:** EXAM_T2_M01B v1.0, adoptado para esta sesión.
- **Perfil:** TUTOR-EVALUADOR.
- **Modo:** EVALUATION_PLAN conceptual (P0 solamente), bajo `RECOVERY_BLOCKED`.
- **BASE_VERIFIED:** No; topografía B09 sigue RECOVERY_BLOCKED.
- **Estado de producto:** baseline M01B histórico incompleto; composites M01B generados en B08, sin modelo de bloques.
- **Alcance de este documento:** conservar decisiones de recuperación y preguntas conversadas. No es un plan resuelto ni autorización para implementar código.

## Decisiones y respuestas literales

Las respuestas siguientes se copian literalmente de los mensajes del estudiante en esta conversación.

### Decisión 1 — Prioridad de recuperación

**Alternativa elegida:** A, auditar assay/litología y resolver primero B06–B08.

**Respuesta literal del estudiante:**

> Elijo A. Justificación: es el faltante crítico que sí puedo resolver con los datos actuales. En data/raw/assay.csv, 5245 de 5275 ensayes miden 2 m y los 30 restantes son residuos al final de cada sondaje; además, en lithology.csv hay 82 contactos internos y 57 ensayes de 2 m cruzan un contacto. Antes de compositar necesito auditar eso y definir cómo tratar contactos y residuos (B06–B08). Ventaja: deja composites coherentes con la litología, que son la base del modelo de bloques. Limitación: no resuelve la topografía (B09 sigue BLOCKED porque no hay Topopl.csv en el repo), así que la clasificación aire/roca quedará pendiente.

**Evaluación conversacional registrada:** CORRECTA — H0. La prioridad es defendible con los faltantes del repo y los conteos fueron comprobados después en lectura.

### Decisión 2 — Ensayes que cruzan contactos

**Alternativa elegida:** A, dividir en el contacto y conservar longitud/segmentos.

**Respuesta literal del estudiante:**

> Elijo A. Justificación: el T2 busca un modelo de bloques geológico, por lo que cada composite debe pertenecer a una sola litología. Los 57 ensayes que cruzan contactos son solo el 1,1 % de los 5275 y, según mi revisión, se dividen exactamente en 1 m + 1 m porque los contactos caen a mitad del ensaye; aparecen en los 35 sondajes, así que conviene una regla uniforme. Ventaja: los composites no mezclan litologías (por ejemplo POR y BRX, que tienen leyes muy distintas), lo que da observaciones limpias para asignar litología a bloques. Limitación: el ensaye original mide una sola ley para los 2 m, así que al dividir se supone ley uniforme en ambos subtramos y se generan 114 tramos de 1 m más cortos que el soporte nominal; habrá que definir cómo tratarlos junto con los 30 residuos de fondo.

**Evaluación conversacional registrada:** CORRECTA — H0. Se verificaron posteriormente los 57 cruces y la división geométrica 1 m + 1 m. La ley por mitad sigue siendo una atribución derivada bajo el supuesto señalado por el estudiante.

### Decisión 3 — Tratamiento de tramos cortos

**Alternativa elegida:** A, conservar tramos cortos con longitud real y etiqueta de tipo.

**Respuesta literal del estudiante:**

> Elijo A. Justificación: los tramos cortos son 144 (114 de contacto + 30 residuos), cerca del 2,7 % de los intervalos, y excluirlos haría perder información relevante: según mi revisión, 28 de los 30 residuos están en POR o BRX, tienen Cu medio de 0,44 % y 20 superan 0,3 % de Cu, es decir, están en la zona mineralizada al fondo de los sondajes. Unirlos (B) generaría composites de hasta 3 m y reglas de unión arbitrarias sin agregar información. Ventaja: se conserva la trazabilidad y la litología de cada tramo, registrando su longitud real y un indicador de tipo (contacto o residuo), para que cualquier uso posterior pueda ponderar por longitud. Limitación: el soporte de los composites no es uniforme (hay residuos de hasta 0,05 m y 11 menores de 0,5 m); si en una etapa futura se estiman leyes, habrá que decidir un umbral mínimo de longitud.

**Evaluación conversacional registrada:** CORRECTA — H0. Se comprobó que hay 30 residuos, 28 con litología POR/BRX, promedio Cu aritmético no ponderado de 0,442266 %, 20 con Cu > 0,3 % y 11 residuos < 0,5 m. El promedio ponderado por longitud es distinto (0,393821 %); “zona mineralizada” no queda validado por esos conteos sin criterio económico aprobado.

### Decisión 4 — Trazabilidad de los ensayes partidos

**Alternativa elegida:** A, dos segmentos geométricos con mismo `sample_id`, sin tratarlos como mediciones independientes.

**Respuesta literal del estudiante:**

> Elijo A. Justificación: es coherente con mi decisión de dividir en el contacto. Los 57 ensayes cruzados se dividen exactamente en 1 m + 1 m; registrar ambos segmentos con el mismo sample_id deja claro que son una sola medición analítica partida geométricamente y no dos observaciones independientes. Si después se pondera por longitud, los dos segmentos suman los 2 m originales, por lo que no se duplica el soporte. Según mi revisión, los cruces son principalmente REG→DIO (31), DIO→POR (10) y REG→POR (8), y hay 7 en contactos con BRX (5 POR→BRX y 2 BRX→POR); conservarlos mantiene la información en esos contactos. Ventaja: se respeta la geometría litológica sin perder ni duplicar mediciones. Limitación: la ley asignada a cada segmento es la misma del ensaye original (supuesto de ley uniforme dentro de los 2 m); no se conoce la ley real de cada mitad.

**Feedback emitido en la sesión:** se indicó que faltaba DIO→REG y se evaluó ese recuento como PARCIAL — H0. El conteo posterior verificó que hay seis tipos, incluido DIO→REG:1. La decisión A sobre trazabilidad se dejó como defendible; no se generó ningún segmento.

### Decisión 5 — Presentación del recuento de contactos

**Alternativa elegida:** A, conservar seis transiciones dirigidas.

**Respuesta literal del estudiante:**

> Elijo A. Corrijo mi recuento: son seis transiciones dirigidas que suman 57: REG→DIO 31, DIO→POR 10, REG→POR 8, POR→BRX 5, BRX→POR 2 y DIO→REG 1. Justificación: la dirección según la profundidad es información geológica observada (por ejemplo, POR→BRX indica entrada a la brecha y BRX→POR la salida), así que no conviene agruparla ni omitir casos. Ventaja: el resumen es completo y trazable, sin perder ningún cruce. Limitación: incluye una categoría de un solo caso; el contacto DIO→REG tiene REG por debajo de DIO, lo que es inusual si REG es material superficial, pero el significado de los códigos no está documentado, así que lo registro como observación a revisar y no como error.

**Evaluación conversacional registrada:** la evaluación inicial PARCIAL se corrigió a CORRECTA — H2 después de la respuesta corregida. Los seis conteos fueron verificados contra los intervalos fuente ordenados por profundidad. No se infiere que `REG` signifique material superficial: el estudiante lo expresó condicionalmente y señaló que el diccionario no define los códigos.

### Decisión 6 — Baseline M01B sin registro previo

**Alternativa elegida:** C, no reconstruir un historial no respaldado; documentar la recuperación realizada durante T2.

**Respuesta literal del estudiante:**

> Elijo C. Justificación: no existe un baseline M01B previo que inspeccionar. Según la evidencia del repo, docs/implementation/ solo contiene IMP-001; el historial de la rama termina en b22c297 (validación espacial de M01) y en GitHub solo existen las ramas main y feature/m01-architecture, sin composites ni pruebas de compositing. Reconstruir decisiones que no se tomaron haría la trazabilidad falsa. Ventaja: el registro es honesto y todo lo de M01B quedará documentado como recuperación realizada en el T2. Limitación: el baseline M01B no tendrá historia previa; B05 solo se completará con la evidencia nueva que generemos en las etapas autorizadas.

**Evaluación conversacional registrada:** CORRECTA — H0, con la salvedad de que la lista de ramas remotas se registra como evidencia aportada por el estudiante, no como consulta GitHub ejecutada independientemente por el agente.

## Autorización de documentación

**Autorización literal del estudiante:**

> A. Sí, autorizo exactamente esas rutas y contenido inicial, con estas condiciones:  
> 1) Mis respuestas deben copiarse literalmente, incluida la corrección del recuento de contactos (PARCIAL → CORRECTA con H2). Si no puedes recuperar alguna respuesta con fidelidad, márcala como TRANSCRIPCIÓN A CONFIRMAR y no la reconstruyas.  
> 2) Registra como evidencia mía la salida que ejecuté en la terminal:  
> git fetch origin  
> git branch -r  
>   origin/HEAD -> origin/main  
>   origin/feature/m01-architecture  
>   origin/main  
> Esto confirma que en el remoto solo existen main y feature/m01-architecture, sin ramas de M01B.  
> 3) No modifiques la plantilla protegida, no toques data/raw/ y no hagas commit ni push.  
> Después de crearlos, muéstrame la lista de archivos creados y vuelve a evaluar B05.

Esta autorización permitió crear únicamente el IMP-002 y los dos documentos de examen especificados. No autorizó código, instalación, modificación de fuentes, edición de plantilla protegida, commit ni push.

## Mapa de verificación vigente

| ID | Estado tras diagnóstico | Observación |
|---|---|---|
| B00 | VERIFIED | Rama `feature/t2-m01b-block-model`, HEAD `b22c297`; exam source docs estaban sin seguimiento al diagnóstico |
| B01 | VERIFIED | Fuentes y diccionario presentes; hashes del manifest comprobados |
| B02 | VERIFIED | Loader/validator; suite M01 actual con `.venv`: 40 PASS, exit code 0 |
| B03 | VERIFIED | Trayectoria XYZ y tablas posicionadas presentes |
| B04 | VERIFIED | Visualizador M01 y HTML real presentes; topografía no incluida |
| B05 | PARTIAL | IMP-002 registra el baseline actual, decisiones y evidencia M01B; el baseline histórico previo no existe |
| B06 | VERIFIED | Auditoría de intervalos assay/lithology, contactos, cobertura, longitudes, nulos/duplicados y reglas Cu/Mo/Au contrastadas con reportes; QA/QC/semántica de códigos no afirmadas |
| B07 | VERIFIED | Regla del grupo documentada y aplicada en `src/m01/compositing.py`: bins 2 m desde MD 0, segmentación por contacto, ponderación por longitud y parciales trazables |
| B08 | VERIFIED (computacional) | Implementación, 7 pruebas específicas y salida generada; validación computacional satisfecha. Interpretación minera registrada; no equivale a validación geológica |
| B09 | RECOVERY_BLOCKED | No se encontró fuente topográfica local; aire/roca no puede validarse |
| B10 | VERIFIED | Suite completa `.venv`: 47 PASS (40 M01 + 7 B08), exit code 0; generación y trazabilidad documentadas |

**B05 no se marca completa:** la ausencia de historia previa quedó registrada fielmente; falta evidencia nueva conforme avancen etapas autorizadas.

## Decisión 7 — Auditoría B06 incremental

**Alternativa elegida:** C, verificar un subconjunto concreto de B06 y declarar limitaciones.

**Respuesta literal del estudiante:**

> Elijo C. Justificación: gran parte de B06 ya tiene evidencia (m01_validation_summary.csv registra 0 gaps y 0 overlaps en assay y lithology, y ya verificamos residuos, contactos y cruces), así que conviene cerrar un subconjunto concreto en vez de repetir todo. Propongo verificar en modo lectura: (1) que assay y lithology cubren de 0 m a final_depth_m en los 35 sondajes y que su longitud total coincide con lo perforado; (2) nulos y duplicados por hole_id/from_m; (3) Cu sin negativos y Mo/Au en cero, clasificados como INFO sin interpretarlos. Ventaja: B06 queda cerrado con evidencia y avanzamos a B07 sin retrasar el examen. Limitación: no se audita QA/QC analítico ni el significado de los códigos litológicos, porque esa información no existe en el release; queda como pendiente declarado.

**Evaluación conversacional:** CORRECTA — H0. Las verificaciones en lectura confirmaron cobertura y suma de intervalos para los 35 sondajes, cero gaps/overlaps en esas tablas, cero claves/intervalos vacíos o duplicados en el subconjunto consultado, y las reglas/conteos de valores negativos/cero de Cu/Mo/Au. B06 queda VERIFIED para la auditoría de datos prevista. QA/QC y semántica geológica no se evaluaron ni se infieren; los ceros y las categorías no reciben interpretación geológica/económica.

### Evidencia adicional de prueba en `.venv`

El estudiante declaró haber ejecutado el suite desde su terminal, pero el mensaje no contiene salida literal, sino un marcador de posición. Su afirmación y esa limitación están documentadas en `docs/exam/T2_M01B_EVIDENCE_G04.md`. La ejecución independiente actual con `C:\Proyecto_Plan\.venv\Scripts\python.exe` registró 40 tests PASS, `OK`, exit code 0. La ejecución previa con Python del sistema terminó con exit code 1 por imports faltantes `matplotlib`/`plotly`; no se ejecutó `main.py`.

## Decisión 8 — Soporte nominal de compositing

**Alternativa elegida:** A, longitud objetivo/nominal de 2 m, respetando contactos y conservando tramos cortos con longitud real.

**Respuesta literal del estudiante:**

> Elijo A: longitud objetivo de 2 m, respetando contactos y conservando los tramos cortos con su longitud real (decisiones anteriores). Justificación: 5245 de 5275 ensayes (99,4 %) ya miden 2 m, así que compositar a 2 m no promedia ni suaviza la información medida; solo estandariza el soporte y separa los 57 ensayes que cruzan contactos. No hay en el repositorio una altura de banco ni un diseño minero que justifique otro largo (alternativa B), y el T2 no estima leyes. Ventaja: los composites quedan prácticamente iguales a las observaciones originales, con trazabilidad directa a cada sample_id. Limitación: el soporte no es totalmente uniforme (144 tramos cortos: 114 de contacto y 30 residuos), y que el composite mida 2 m no implica que el bloque deba medir 2 m; el tamaño de bloque se decidirá en P2 según el espaciamiento real entre sondajes.

**Evaluación conversacional:** CORRECTA — H0. La evidencia confirma 5.245/5.275 ensayes de 2 m, 57 cruces que generan geométricamente segmentos de 1 m + 1 m y 30 residuos terminales. Se registra 2 m como soporte nominal/objetivo, no como longitud obligatoria de cada salida. En intervalos divididos se conservaría un único soporte analítico original de 2 m mediante trazabilidad y longitudes de subtramo; la ley por mitad sigue siendo un supuesto, no una medición nueva. El estudiante distingue correctamente el soporte de compositing del tamaño de bloque P2.

### Decisión 9 — Anclaje de bins y contactos

**Alternativa elegida:** B, bins nominales de 2 m anclados en 0 m del collar; no cruzar contactos, ponderar por longitud y conservar tramos parciales.

**Respuesta literal del estudiante:**

> Elijo B: bins nominales de 2 m anclados en el collar (0 m), sin cruzar contactos, ponderando por longitud y conservando los tramos parciales. Justificación: según mi revisión, todos los ensayes de assay.csv empiezan en metros pares (0, 2, 4…), así que la grilla de 2 m desde el collar coincide exactamente con los ensayes y cada composite corresponde a un solo ensaye (resultado equivalente a A, pero como regla general reproducible). De los 82 contactos, 25 caen en metros pares y no requieren división; los 57 en metros impares se dividen 1 m + 1 m. Descarto C porque, al anclar en contactos impares, cada composite mezclaría la mitad de dos ensayes distintos y promediaría leyes medidas por separado. Ventaja: no se altera ninguna ley medida y la regla es aplicable a otros datasets. Limitación: la ponderación por longitud solo tendría efecto si los ensayes no estuvieran alineados a la grilla; aquí los composites son prácticamente los ensayes originales, por lo que el compositado no reduce la variabilidad.

**Evaluación conversacional:** CORRECTA — H0. La verificación de solo lectura confirmó que los 5.275 valores `from_m` son múltiplos de 2, y que entre los 82 contactos internos 25 tienen profundidad par y 57 impar; no hubo profundidades no enteras. Esto respalda que el anclaje al collar coincide con la grilla assay observada y que los contactos pares no cortan un assay, mientras los impares bisecan geométricamente un intervalo de 2 m. La limitación sobre la ponderación es pertinente: para estos datos no cambiaría el resultado en segmentos alineados a la grilla; la generalización a otros datasets requerirá especificar cómo agregar observaciones y manejar bins parciales, sin perder trazabilidad ni convertir segmentos heredados en nuevas mediciones.

### Decisión 10 — Agregación y soporte parcial

**Alternativa elegida:** A, media ponderada por longitud aportada al bin; registrar longitud cubierta y marcar parcial si es menor de 2 m, sin rellenar faltantes con cero.

**Respuesta literal del estudiante:**

> Elijo A: media ponderada por la longitud que cada intervalo aporta al bin, registrando la longitud efectivamente cubierta y marcando como parcial todo composite menor de 2 m, sin rellenar la parte faltante con ley cero. Justificación: los 30 residuos miden entre 0,05 y 1,98 m; con una media simple (B) un residuo de 0,05 m pesaría igual que un ensaye de 2 m, lo que sesga la ley. Además, como todos los from_m son múltiplos de 2 y no se cruzan contactos, en este dataset ningún bin combina dos ensayes distintos de la misma litología: los 57 bins divididos generan dos composites parciales de 1 m cada uno, y los 30 residuos quedan como composites parciales. La regla A se define igual para que el algoritmo sea correcto y reutilizable. Ventaja: respeta el soporte real de cada intervalo y la marca de parcial permite filtrar o ponderar después. Limitación: la ponderación supone ley uniforme dentro de cada intervalo; y los composites parciales (144) tienen soporte menor que el nominal.

**Evaluación conversacional:** CORRECTA — H0. La ponderación por longitud evita dar peso igual a tramos de distinto soporte; registrar cobertura y no imputar ley cero es consistente con la evidencia. La atribución de ley dentro de un intervalo sigue suponiendo homogeneidad del ensayo original. La afirmación de que no hay múltiples assays de una misma litología en un bin fue solicitada para verificación y queda confirmada por el resultado de lectura anotado en EVIDENCE. Los 144 parciales son el resultado esperado por la regla decidida (114 segmentos de contacto y 30 residuos), no una salida ya generada. Con esta decisión, B07 queda conceptualmente especificado y documentado; B08 sigue pendiente de implementación y pruebas.

### Decisión 11 — Identificador y procedencia de composite

**Alternativa elegida:** A, asignar un `composite_id` único y determinista por fila y conservar `sample_id` como procedencia; repetir el `sample_id` para las dos filas derivadas de un ensayo partido.

**Respuesta literal del estudiante:**

> Elijo A: composite_id único por fila y sample_id de origen como columna de procedencia. Justificación: con la regla aprobada, los 57 ensayes que cruzan contactos se dividen en dos segmentos, así que la tabla esperada tendría 5332 filas (5275 + 57) con 57 sample_id repetidos dos veces; sin un ID propio no habría forma única de referirse a cada fila. Descarto B porque una clave de cuatro campos con profundidades decimales es frágil frente a redondeos, y C porque deja filas sin identidad única. Ventaja: cada composite es referenciable de forma única (útil para vincularlo después con bloques) y el sample_id compartido deja claro que ambas mitades provienen de una sola medición. Limitación: el composite_id es un identificador derivado, no un dato del laboratorio; su formato debe ser estable y reproducible (por ejemplo, basado en hole_id y orden por profundidad) para que no cambie entre ejecuciones.

**Evaluación conversacional:** CORRECTA — H0. Un ID propio por fila permite identificar inequívocamente segmentos que comparten `sample_id`, preservando la relación con la medición de laboratorio. El total de 5.332 filas es una expectativa aritmética según la regla (una fila por ensayo, más una fila adicional por cada uno de los 57 ensayos partidos), no un resultado de ejecución: no hay tabla de composites generada. La estabilidad determinista del `composite_id` queda reconocida como requisito; su formato exacto se especificará antes de implementación.

### Decisión 12 — Regla determinista de `composite_id`

**Alternativa elegida:** A, concatenar `hole_id` y un índice secuencial de cuatro dígitos por sondaje, ordenado establemente por `from_m` y `to_m`.

**Respuesta literal del estudiante:**

> Elijo A: composite_id = hole_id + índice secuencial de 4 dígitos por profundidad (por ejemplo CR-C01-001_0001), ordenado de forma estable por from_m y to_m. Justificación: data/raw/ es inmutable (8 hashes del manifiesto verificados) y la regla de compositado es fija, así que con las mismas entradas el orden y los IDs se regeneran idénticos. Ventaja: es legible y permite revisar a mano cada sondaje (35 sondajes, unas 152 filas promedio por sondaje). Limitación: si en el futuro cambiaran los datos fuente o la regla, los índices se recalcularían; por eso el sample_id se conserva como vínculo permanente con el ensaye original.

**Evaluación conversacional:** CORRECTA — H0. La regla produce IDs legibles y deterministas para las mismas entradas/reglas, y `sample_id` conserva la procedencia analítica. La auditoría de lectura registró 35 sondajes con entre 115 y 218 assays por sondaje, por debajo del límite de 9.999 índices representables con cuatro dígitos. La numeración se reinicia por sondaje y se asignará después de ordenar por `from_m`, `to_m`; no se implementó ni generó ningún ID aún.

## Gate B08 — aprobación e implementación

- **Autorización literal del estudiante:** 

> A. Sí, apruebo la etapa B08 con exactamente ese alcance (src/m01/compositing.py, tests/m01/test_compositing.py y data/processed/m01b_composites.csv), con estas condiciones:  
> 1) Ejecuta todo con el intérprete del entorno virtual: C:\Proyecto_Plan\.venv\Scripts\python.exe.  
> 2) Después de las pruebas de compositing, ejecuta también la suite completa (python -m unittest discover -s tests -v) para confirmar que las 40 pruebas de M01 siguen pasando; registra comando, salida y exit code reales.  
> 3) Indica y registra el comando exacto con el que se genera m01b_composites.csv (sin main.py), para que el resultado sea reproducible.  
> 4) Compara los conteos reales contra los esperados (5332 filas, 5188 de 2 m, 144 parciales, 57 sample_id repetidos) y reporta cualquier diferencia sin ajustarla.  
> No modifiques data/raw/, main.py ni la gobernanza; no instales dependencias ni hagas commit o push. Al terminar, muéstrame los resultados y pídeme la interpretación antes de dar la etapa por validada.

- **Archivos implementados/generados:** `src/m01/compositing.py`, `tests/m01/test_compositing.py`, `data/processed/m01b_composites.csv`. `main.py`, `data/raw/` y gobernanza no se modificaron.
- **Función:** `build_composites(assay, lithology, trajectory, target_length_m=2.0) -> CsvTable`; valida las entradas, segmenta por contacto y bin, calcula ponderación por longitud aportada, conserva soporte parcial y usa posicionamiento M01 de FROM/MID/TO sin extrapolación. `source_sample_ids` conserva la procedencia JSON cuando hay varios assays; en este release cada fila tiene un `sample_id` único de origen.
- **Comando exacto de generación**, ejecutado desde `C:\Proyecto_Plan\PlanMinUPN-G04`:

```powershell
C:\Proyecto_Plan\.venv\Scripts\python.exe -m src.m01.compositing
```

Salida real: `composites_written=5332`, ruta `C:\Proyecto_Plan\PlanMinUPN-G04\data\processed\m01b_composites.csv`, exit code 0.

- **Comparación real vs. esperado:** 5.332 filas (igual); 5.188 de 2 m (igual); 144 parciales (igual); 57 `sample_id` aparecen dos veces cada uno (igual). Diferencias: ninguna. Se conservaron 10.518,328249553 m de soporte total, igual a la longitud assay; no hubo discrepancias de longitud por `sample_id` ni cruces de soporte litológico.
- **Pruebas enfocadas:** 7 tests PASS, exit code 0. **Suite completa:** 47 tests PASS, exit code 0, incluidos los 40 tests M01 previos y los 7 nuevos de compositing. Comandos/salida detallados se conservan en EVIDENCE.
- **Estado tras interpretación minera formativa:** las métricas computacionales incluyen cero cruces litológicos, soporte total y por assay conservado, filas parciales/nominales según lo esperado y XYZ en las 5.332 filas. B08 VERIFIED computacionalmente; no equivale a validación geológica. Topografía y clasificación aire/roca siguen fuera de alcance.

### Decisión 13 — Interpretación de resultados y estado B08/B10

**Alternativa elegida:** B, interpretar el resultado como consistente computacionalmente con reglas/datos comprobados, no como validación geológica; revisar los códigos AIR en P1 y mantener topografía como bloqueante para aire/roca.

**Respuesta literal del estudiante:**

> B. El compositado es consistente con las reglas acordadas y con los datos verificados, pero esa consistencia computacional no equivale a una validación geológica.
>
> Resultado observado: se generaron 5332 compósitos (5188 de 2 m y 144 parciales), con 57 sample_id repetidos dos veces. Se conservan la longitud total (10518.328 m, igual a assay.csv) y la ley de Cu ponderada por longitud (0.25249 % antes y después), y cada compósito mantiene el Cu de su ensaye de origen. Verifiqué estos valores de forma independiente sobre m01b_composites.csv.
>
> Ventaja: no se mezclan litologías dentro de un compósito y no se inventan leyes ni se rellena con ceros, por lo que el archivo es una base trazable para asignar dominios.
>
> Limitación: en los 57 ensayes partidos, las dos mitades de 1 m heredan la misma medición, así que no son observaciones independientes. Los 144 parciales tienen soporte menor a 2 m y no deben tratarse como muestras de 2 m. Además, 2 m quedaron con litología AIR (viene así de lithology.csv) y deben revisarse en P1. Sin topografía no se puede validar la clasificación aire/roca.
>
> Propongo dejar B08 como VERIFIED (computacional) y pasar a B10/BASE_VERIFIED, con B09 como RECOVERY_BLOCKED.

**Verificación independiente adicional y evaluación:** CORRECTA — H0. Se verificó Cu ponderado por longitud en assay y composites: `0.252487149710 %` en ambos; cero compósitos difieren del Cu de su assay fuente. Se encontró una fila composite `AIR`, de 2 m, asociada a `lithology.csv`; se documenta el código sin inferir significado ni clasificarlo como aire físico. La longitud total coincide con assay; no hay incongruencias de soporte por muestra ni por contactos litológicos. En consecuencia, B08 queda VERIFIED **en sentido computacional** y B10 VERIFIED por las 47 pruebas PASS y comandos/salida trazables. La interpretación separa correctamente consistencia de validación geológica.

**Límite de estado base:** no se puede aprobar `BASE_VERIFIED`. B09 carece de topografía local y es crítico para la relación bloque–superficie/clasificación aire-roca; queda `RECOVERY_BLOCKED`. B05 sigue PARTIAL porque se documentó el baseline actual pero no existe historia M01B previa. El modo permanece `ALIGNMENT_RECOVERY / RECOVERY_BLOCKED`; solo puede continuarse planificación conceptual hasta resolver/declarar formalmente los bloqueos según el protocolo. `EVALUATION_PLAN` no inicia.

### Decisión 14 — Continuar planificación conceptual bajo el bloqueo B09

**Alternativa elegida:** A, continuar `EVALUATION_PLAN` conceptual en P0 bajo `RECOVERY_BLOCKED`, dejando aire/roca como `TOPO_UNKNOWN` y consultando en paralelo al docente por la fuente oficial.

**Respuesta literal del estudiante:**

> A. Continúo con la planificación conceptual bajo RECOVERY_BLOCKED, dejando la clasificación aire/roca sin resolver (TOPO_UNKNOWN).
>
> Evidencia: en el repositorio no existe Topopl.csv ni otra fuente topográfica oficial (data/raw/ solo contiene los 8 archivos del manifest), y el escenario indica que, sin un requisito crítico, solo se puede continuar con el plan conceptual, dejando pendientes la generación y la validación.
>
> Ventaja: puedo avanzar en las decisiones que no dependen de la topografía (P0 plan, P1 dominios, P2 extensión/origen/tamaño de bloque con datos reales y P4 criterios de asignación y de UNKNOWN), con trazabilidad y sin inventar una superficie.
>
> Limitación: ningún bloque podrá clasificarse como AIR o ROCK. El límite superior del modelo quedará definido solo de forma provisional por los collars, y la validación P3 seguirá pendiente hasta que el docente entregue la topografía oficial y se verifiquen sus coordenadas, elevaciones, unidades y cobertura. En paralelo consultaré al docente.
>
> Pasemos a EVALUATION_PLAN / P0 en modo conceptual.

**Evaluación conversacional:** CORRECTA — H0. El escenario permite continuar únicamente con plan conceptual si un requisito crítico permanece bloqueado. La topografía no está presente en los ocho archivos del manifest, según evidencia ya registrada. Se adopta el modo `EVALUATION_PLAN conceptual (P0 solamente)`, sin cambiar `BASE_VERIFIED=No`, sin autorizar código ni resultados. La clasificación seguirá `TOPO_UNKNOWN`; el uso provisional de collars para un límite superior no es una superficie topográfica y debe permanecer expresamente provisional.

## P0 — Diagnóstico y plan de implementación conceptual (sin código)

**Microteoría:** P0 organiza dependencias, riesgos y etapas; no fija parámetros del modelo ni autoriza su generación. Las etapas que no dependen de topografía pueden planearse conceptualmente. P1 puede revisar códigos y contactos observados; P2 puede estudiar alternativas geométricas con XYZ de sondajes, pero sus límites superiores no serán definitivos sin topografía. P3 requiere fuente y cobertura verificables; P4 no debe clasificar bloques como roca/aire sin el estado topográfico necesario. `TOPO_UNKNOWN` expresa desconocimiento por falta de cobertura/fuente, no una clase física.

**Evidencia/faltantes:** B08 está VERIFIED computacionalmente, B10 VERIFIED; `data/raw/` contiene los ocho archivos del manifest y no incluye `Topopl.csv`; B09=`RECOVERY_BLOCKED`; B05=`PARTIAL`; `BASE_VERIFIED` sigue No. El escenario P0 requiere construir por decisiones el orden, dependencias, riesgos y alcance; aún no hay `PLAN_APPROVED`.

### Decisión P0.1 — Orden de etapas mientras B09 sigue bloqueado

El orden afecta qué puede avanzar sin producir geometrías que luego parezcan definitivas. Planificar P1 antes de topografía permite trabajar con códigos/contactos disponibles; postergar P1 también evita avanzar más antes de recuperar la fuente común. P2 puede ser solo comparativo/provisional con datos XYZ, mientras P3 y cualquier clasificación AIR/ROCK requieren B09 resuelto.

**¿Qué secuencia de trabajo propones mientras se consulta al docente por la topografía?**

- **A.** Avanzar conceptualmente P1; en P2 calcular y comparar alternativas usando trayectorias/composites con límites superiores provisionales y `TOPO_UNKNOWN`; consultar topografía en paralelo; detener la clasificación final hasta verificar B09 en P3.
- **B.** Pausar P1 y P2 hasta recibir/verificar topografía; después construir el plan de dominios y malla con todo el soporte espacial presente.
- **C.** Avanzar P1; diferir todo P2 (incluso comparaciones geométricas) hasta B09; continuar después en secuencia P2→P3→P4.

**Alternativa elegida:** A.

**Respuesta literal del estudiante:**

> A. Planifico P1 primero; en P2 comparo geometrías con los datos reales, marcando el límite superior como provisional y TOPO_UNKNOWN; consulto la topografía al docente en paralelo y detengo la clasificación aire/roca hasta verificarla en P3.
>
> Evidencia del repositorio: P1 y P2 dependen de datos ya verificados y no de la topografía. lithology.csv y m01b_composites.csv tienen los códigos y contactos (REG, DIO, POR, BRX y 1 fila AIR). drillhole_trajectory.csv y los XYZ de composites permiten calcular la extensión real: collars entre z ≈ 3288 y 3524 m, fondos entre z ≈ 3059 y 3097 m, huella en planta de ≈ 553 × 565 m y distancia 3D mínima entre trayectorias vecinas entre 6 y 93 m (mediana 20 m, columna minimum_trajectory_distance_3d_m de outputs/tables/m01_validacion_espacial.csv). Solo P3, y la parte aire/roca de P4, requieren la superficie topográfica, que no existe en data/raw/.
>
> Ventaja: aprovecho el tiempo con las decisiones que ya tienen soporte (dominios, extensión, origen y candidatos de tamaño de bloque con número total de bloques) sin depender de un archivo que aún no existe.
>
> Limitación: el límite superior del grid será provisional (basado en los collars). Si la topografía oficial llega con otra cobertura o con cotas distintas, habrá que revisar la extensión vertical y el número de bloques, y ningún bloque se clasificará como AIR o ROCK hasta P3.

**Verificación y evaluación conversacional:** CORRECTA — H0. La lectura confirmó cinco códigos observados (`AIR`, `BRX`, `DIO`, `POR`, `REG`), 35 trayectorias; Z de collar 3288–3524 m; Z al fondo 3059,530–3097,320 m; huella XY 552,970 × 565,300 m; y distancias mínimas entre trayectorias 5,979–92,736 m, mediana 20,000 m. `data/raw/` no contiene rutas/nombres con “topo”. Se acepta el orden como planificación conceptual: P1 y comparaciones P2 pueden formularse con datos observados, pero no se fija una superficie ni se produce grid; extensión superior, P3 y clasificación AIR/ROCK permanecen provisionales/bloqueadas.

### Pregunta P1.1 — Uso de códigos sin diccionario geológico

**Microteoría:** `lith_code` es una categoría observada en intervalos; no prueba por sí sola una unidad geológica, continuidad, dominio de estimación ni sólido. Mantener códigos distintos conserva la evidencia sin inventar semántica. Agruparlos puede simplificar la representación, pero requiere sustento geológico que aquí no está documentado. Pospone decisiones y reduce el riesgo de sobreinterpretación, pero limita el avance del plan.

**Evidencia y faltantes:** `data/raw/lithology.csv` y `data/processed/m01b_composites.csv` contienen `REG`, `DIO`, `POR`, `BRX` y una fila `AIR`; el diccionario verificado describe el campo `lith_code` como código categórico, sin definiciones geológicas. Hay 82 contactos internos, y se han preservado los segmentos sin cruces. La fila AIR necesita revisión P1; la falta de topografía impide validar aire/roca.

**¿Qué política conceptual propones para representar esos códigos en P1 sin afirmar más de lo que sustentan los datos?**

- **A.** Mantener cada `lith_code` como categoría provisional distinta, sin agrupar ni asignar significado geológico no documentado; señalar `AIR` para revisión y dejar cualquier clasificación aire/roca en `TOPO_UNKNOWN`.
- **B.** Usar un código genérico `UNKNOWN` para todos los intervalos hasta recibir un diccionario geológico; conservar el código original solo como atributo de procedencia.
- **C.** Pausar P1 y no planificar representación de códigos hasta que el docente aporte definiciones y revisión geológica; continuar solo con tareas de geometría conceptual de P2.

Elige A, B o C y justifica con evidencia del repo, una ventaja y una limitación.

### Decisión P1.1 — Representación de códigos sin diccionario

**Alternativa elegida:** A, conservar cada código como categoría provisional distinta, sin atribuirle significado geológico no documentado; marcar `AIR` para revisión y mantener aire/roca como `TOPO_UNKNOWN`.

**Respuesta literal del estudiante:**

> A. Mantengo cada código como categoría provisional distinta (REG, DIO, POR, BRX), sin asignarles significados geológicos no documentados; marco AIR para revisión y dejo la condición aire/roca como TOPO_UNKNOWN.
>
> Evidencia del repositorio: en m01b_composites.csv hay 5 códigos con soporte muy diferente: POR 2751 compósitos (5455.218 m), DIO 2017 (3989.848 m), BRX 412 (809.262 m), REG 151 (262.0 m) y AIR 1 (2.0 m). El único AIR es CR-C02-002_0001 (MD 0–2 m, junto al collar, Cu = 0), seguido de REG desde 2 m, y su código proviene de lithology.csv. No existe en el repositorio un diccionario que defina los códigos ni una agrupación en dominios.
>
> Ventaja: conservo exactamente la observación registrada en los sondajes, sin agrupar ni reinterpretar, y la representación es trazable a lithology.csv. AIR queda separado y marcado, por lo que no se mezcla con roca ni con UNKNOWN.
>
> Limitación: mantener los códigos separados no demuestra que sean dominios geológicos continuos. REG tiene poco soporte (151 compósitos, cerca de superficie) y AIR un único tramo, por lo que su representación volumétrica será incierta. No sé si AIR es aire físico, un tramo sin recuperación o una convención de registro: sin topografía ni definición oficial no puedo confirmarlo.

**Verificación y evaluación conversacional:** CORRECTA — H0. Lectura independiente confirmó los conteos y longitudes aportados (`POR` 2.751 / 5.455,218 m; `DIO` 2.017 / 3.989,848 m; `BRX` 412 / 809,262 m; `REG` 151 / 262,000 m; `AIR` 1 / 2,000 m). El único `AIR` corresponde a `CR-C02-002`, MD 0–2 m, Cu 0, seguido por `REG` desde MD 2 m; la fila fuente existe en `lithology.csv`. El código y Cu=0 no determinan por sí solos si es aire físico, recuperación o convención. No se agrupan códigos ni se les asigna interpretación no sustentada.

### Pregunta P1.2 — Tratamiento conceptual del código `AIR`

**Microteoría:** una categoría litológica `AIR` observada en un intervalo no equivale automáticamente a una clasificación topográfica de celda. Etiquetarlo directamente como aire propagaría una interpretación desde un único tramo de collar a volumen; tratarlo como roca ignoraría la etiqueta fuente. Reservarlo como observación pendiente conserva la evidencia y evita ambas inferencias. La falta de topografía mantiene `TOPO_UNKNOWN` para el estado físico de bloques.

**Evidencia/faltantes:** hay exactamente una fila `AIR`, en MD 0–2 m del collar `CR-C02-002`; la ley de Cu fuente es cero; no hay diccionario que defina AIR ni superficie topográfica local. El próximo paso permitido es definir en el plan cómo preservar este código y cómo evitar usarlo para clasificar volumétricamente antes de aclararlo.

**¿Qué tratamiento propones para `AIR` en el plan conceptual de dominios?**

- **A.** Conservar `AIR` como código observado separado y con bandera `REVIEW/UNKNOWN`; excluirlo de cualquier extensión volumétrica y no traducirlo a `topo_status=AIR` hasta aclarar el significado y verificar topografía.
- **B.** Tratar provisionalmente el intervalo como roca, ya que aparece en la tabla lithology; conservar una bandera de revisión para corregirlo si la topografía contradice.
- **C.** Remapear inmediatamente el código a `TOPO_UNKNOWN` y dejar de preservar `AIR` como categoría observada, simplificando el set de dominios.

Elige A, B o C y justifica con evidencia del repo, una ventaja y una limitación.

**Respuesta del estudiante — A:**

A. Preservo AIR como código observado separado, marcado REVIEW/UNKNOWN; lo excluyo de la extensión volumétrica de dominios y no lo traduzco a topo_status=AIR hasta aclarar su significado y contar con topografía verificada.

Evidencia del repositorio: AIR aparece una sola vez en m01b_composites.csv (CR-C02-002_0001, MD 0–2 m, Cu = 0), proviene de lithology.csv y está inmediatamente sobre REG desde 2 m. En el repositorio no hay un diccionario de códigos ni una superficie topográfica que permitan confirmar si es aire físico.

Ventaja: mantengo la trazabilidad con la fuente sin afirmar que es roca ni que es aire, y evito que un único tramo de 2 m defina por sí solo un volumen o una condición topográfica.

Limitación: ese tramo de 2 m queda sin dominio asignado y la duda sobre su significado (aire físico, tramo sin recuperación o convención de registro) solo se resuelve con la definición oficial del código o con la topografía en P3. Si resultara ser roca, habría que reincorporarlo.

**Evaluación conversacional:** CORRECTA — H0. La decisión conserva el valor fuente y distingue el código litológico de la clasificación física/topográfica; no asigna volumen ni significado sin diccionario o topografía.

### Pregunta P1.3 — uso conceptual de los contactos litológicos

**Microteoría:** un contacto registrado separa intervalos en el sondaje, pero no demuestra por sí solo la geometría tridimensional ni continuidad de una frontera entre sondajes. Tratar cada contacto como límite duro evita mezclar códigos al asignar bloques, aunque presupone que el contacto debe extenderse como frontera. Ignorarlo y propagar solo el código más cercano puede cruzar límites observados. Una política provisional puede conservar códigos y contactos sin afirmar geometrías que los datos no demuestran.

**Evidencia/faltantes:** `lithology.csv` contiene 82 contactos internos y los códigos observados son `REG`, `DIO`, `POR`, `BRX` y `AIR`; no hay diccionario geológico ni interpretación de continuidad entre sondajes. La topografía sigue ausente, por lo que esta pregunta no resuelve el límite aire/roca.

**¿Qué política conceptual propones para usar los contactos al asignar dominios a bloques, si más adelante se autoriza esa etapa?**

- **A.** Considerar cada contacto observado como límite duro local y no permitir que la asignación de una categoría cruce ese contacto dentro del sondaje; la continuidad entre sondajes queda pendiente de interpretación.
- **B.** Usar contactos como evidencia, pero declarar duro solo un límite cuya continuidad y significado geológico hayan sido validados; los demás quedan como incertidumbre explícita.
- **C.** No usar contactos como límites y asignar cada bloque con la categoría del intervalo más cercano, registrando esa regla como aproximación de vecindad.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación.

**Respuesta del estudiante — B:**

B. Uso los contactos como evidencia observada, pero solo trataría como límite duro uno cuya continuidad y significado geológico hayan sido validados; en los demás mantengo explícita la incertidumbre (por ejemplo, con un flag de proximidad a contacto o UNKNOWN en zonas disputadas).

Evidencia del repositorio: lithology.csv registra 82 contactos internos en los 35 sondajes, con transiciones REG→DIO (31), DIO→POR (10), REG→POR (8), POR→BRX (5), BRX→POR (2) y DIO→REG (1). Las distancias 3D mínimas entre trayectorias van de 5.98 a 92.74 m (mediana 20 m, outputs/tables/m01_validacion_espacial.csv). No hay en el repositorio secciones interpretadas, superficies de contacto ni un modelo geológico que demuestre cómo continúan los contactos entre sondajes. Los compósitos ya respetan los contactos dentro de cada sondaje (B07/B08), así que no mezclan códigos.

Ventaja: respeto el contacto donde está observado sin inventar superficies continuas entre sondajes separados hasta 93 m. Las transiciones poco frecuentes (BRX→POR 2, DIO→REG 1) no se convierten en límites regionales.

Limitación: sin límites duros validados, los bloques cercanos a un contacto o entre sondajes con códigos distintos tendrán una asignación más incierta y podrán quedar como UNKNOWN. Reducir esa incertidumbre exige interpretación geológica (secciones, criterio del docente) que no está en el repositorio.

**Evaluación conversacional:** CORRECTA — H0. La decisión distingue contactos observados en 1D de superficies geológicas continuas en 3D; mantiene incertidumbre donde faltan interpretación y validación. La evidencia de espaciamiento limita cuánto puede inferirse entre trayectorias, y la preservación de códigos en compósitos no demuestra continuidad geológica.

### Pregunta P1.4 — tratamiento de zonas sin dominio respaldado

**Microteoría:** una regla de asignación puede producir categorías para todo el volumen incluso donde no hay evidencia suficiente, pero eso oculta la diferencia entre observación e inferencia. Una categoría `UNKNOWN` conserva esa distinción a costa de dejar celdas sin dominio; una propagación por cercanía entrega cobertura completa, pero depende de una regla de vecindad y puede cruzar contactos no interpretados. Es posible también conservar la asignación provisional y una medida/flag de soporte para revisión, sin afirmar que sea una interpretación validada.

**Evidencia/faltantes:** hay 35 trayectorias con distancias mínimas entre vecinas de 5,979–92,736 m y mediana 20,000 m; los contactos observados no tienen superficies interpretadas ni continuidad 3D validada. La decisión P1.3 mantiene los contactos no validados como incertidumbre. Esta política sería solo conceptual y no autoriza clasificar bloques mientras B09 siga bloqueado.

**¿Cómo propones representar en el plan las zonas donde los códigos de sondajes difieren y no existe un límite geológico validado?**

- **A.** Dejar el dominio como `UNKNOWN` cuando no exista evidencia suficiente para resolverlo; aceptar cobertura incompleta y documentar qué evidencia permitiría reclasificarlo.
- **B.** Asignar provisionalmente el código del intervalo/compósito más cercano y guardar un flag de baja confianza o proximidad a contacto; aceptar que la regla puede cruzar límites no validados.
- **C.** Crear una categoría provisional de transición entre los códigos en disputa y asignarla en esas zonas, dejando pendiente definir sus propiedades geológicas.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación.

**Respuesta del estudiante — A:**

A. En zonas donde los sondajes vecinos muestran códigos distintos y no hay un límite geológico validado, dejo el dominio como UNKNOWN con la causa identificada (por ejemplo, CONFLICTING_CODES o INSUFFICIENT_SUPPORT) y documento qué permitiría reclasificarlo.

Evidencia del repositorio: hay 82 contactos internos registrados en lithology.csv pero ninguna superficie de contacto interpretada ni sección geológica en el repositorio. Las distancias 3D mínimas entre trayectorias vecinas llegan a 92.736 m (mediana 20 m, outputs/tables/m01_validacion_espacial.csv), así que entre sondajes alejados no hay observaciones que indiquen dónde está el cambio de código. Los únicos códigos documentados son REG, DIO, POR, BRX y AIR; no existe una categoría de transición en los datos.

Ventaja: el modelo muestra de forma explícita dónde falta evidencia, en vez de rellenar el volumen con un código que podría estar equivocado, y no se crean litologías que no aparecen en los datos.

Limitación: la cobertura del modelo quedará incompleta, y en zonas de contactos frecuentes (por ejemplo REG→DIO, 31 transiciones) puede haber muchos bloques UNKNOWN. Para reclasificarlos haría falta un criterio de soporte definido en P4 (distancia máxima al compósito y concordancia de códigos vecinos), una interpretación geológica validada por el docente o más perforación.

**Evaluación conversacional:** CORRECTA — H0. La opción hace explícita la incertidumbre y evita crear categorías no observadas o extender códigos sin evidencia; los criterios para reclasificar permanecen pendientes de P4 y validación geológica.

### Pregunta P1.5 — registro de procedencia y confianza del dominio

**Microteoría:** la categoría asignada a un bloque y la evidencia que la respalda son aspectos distintos. Guardar procedencia (por ejemplo, compósito o sondaje de soporte), distancia y estado de confianza permite revisar la asignación, pero esos campos no convierten una regla geométrica en una interpretación geológica validada. Una procedencia ausente o contradictoria puede justificar `UNKNOWN` con una causa, mientras que una asignación con soporte identificable sigue siendo provisional hasta su validación.

**Evidencia/faltantes:** los compósitos tienen identificadores únicos y conservan `sample_id`/fuente; las trayectorias vecinas tienen distancias mínimas de 5,979–92,736 m. No existe una regla aprobada de asignación de bloques, umbral de distancia, validación de continuidad ni topografía; la propuesta de causas `CONFLICTING_CODES` e `INSUFFICIENT_SUPPORT` aún no está formalizada.

**¿Qué evidencia mínima debería quedar asociada a cada asignación provisional de dominio, si más adelante se autoriza el modelado?**

- **A.** Registrar dominio, fuente(s) de soporte, distancia al soporte, regla/versión usada y estado/causa de incertidumbre; si falta la evidencia mínima, dejar `UNKNOWN`.
- **B.** Registrar solo el dominio y la regla global, evitando campos por bloque para mantener pequeño el modelo.
- **C.** Registrar dominio y un puntaje de confianza único, sin detallar la fuente ni cómo se calculó, para simplificar la revisión.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación.

**Respuesta del estudiante — A:**

A. Cada asignación provisional debería guardar: dominio (lith_code), fuente(s) de soporte (composite_id y, por trazabilidad, sample_id), distancia al soporte (y, si el método lo usa, número de compósitos de apoyo), regla/versión aplicada y estado o causa de incertidumbre (assignment_status ASSIGNED/UNKNOWN/UNASSIGNED con causa como CONFLICTING_CODES o INSUFFICIENT_SUPPORT). Si falta la evidencia mínima, el bloque queda UNKNOWN.

Evidencia del repositorio: m01b_composites.csv ya trae composite_id único, sample_id/source_sample_ids, lith_code y coordenadas XYZ, así que la procedencia puede rastrearse hasta el ensaye original. Además, el contrato mínimo de la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md incluye assignment_status, support_distance_or_count y uncertainty_or_review_flag por bloque. Las distancias entre trayectorias varían de 5.979 a 92.736 m, por lo que el soporte será muy distinto de un bloque a otro y debe quedar registrado individualmente.

Ventaja: cualquier asignación se puede auditar y reproducir (de qué compósito viene, a qué distancia y con qué regla), y si la regla cambia en P4 se puede identificar qué bloques se ven afectados por la versión.

Limitación: el modelo tendrá más columnas y ocupará más memoria, y estos metadatos documentan cómo se asignó el dominio, pero no lo convierten en una interpretación geológica validada. La distancia por sí sola tampoco garantiza continuidad geológica.

**Evaluación conversacional:** CORRECTA — H0. El escenario efectivamente requiere por bloque `assignment_status`, `support_distance_or_count` si el método lo define y `uncertainty_or_review_flag`; la salida de composites conserva IDs de composite/muestra, fuente, código y coordenadas. Nota de precisión: el enum del escenario también incluye `NOT_APPLICABLE`; `ASSIGNED/UNKNOWN/UNASSIGNED` son los estados que el estudiante propone para su política, no la enumeración completa del contrato. La procedencia y distancia mejoran auditabilidad, no validan por sí solas la geología.

### Pregunta P2.1 — escala candidata de celdas

**Microteoría:** las dimensiones del bloque deben defenderse frente al espaciamiento 3D de los sondajes y al soporte de los composites; no se deducen igualando automáticamente el tamaño de celda a la longitud de composite. Una malla más fina aumenta detalle y cantidad de celdas, pero no añade observaciones ni resuelve continuidad; una más gruesa reduce costo y puede ocultar variación. Como falta topografía, cualquier extensión vertical basada solo en trayectorias es provisional. Los conteos siguientes comparan escalas, no aprueban una malla.

**Evidencia del repositorio:** las 270 estaciones de trayectoria de 35 sondajes abarcan X = 552,970 m, Y = 565,300 m y Z = 464,470 m (Z observado desde 3.059,530 m al fondo hasta 3.524 m en collar). La mediana de distancia mínima 3D entre trayectorias vecinas es 20 m y los composites tienen longitud objetivo nominal de 2 m. No hay topografía: el máximo Z de collar no es una superficie y el intervalo vertical del grid sigue siendo provisional. Sobre el envolvente observado sin padding, usando `ceil(span/dimension)` y un origen provisional en los mínimos, los conteos estimados son:

- **A. 10 × 10 × 5 m:** 56 × 57 × 93 = **296.856 bloques**; malla más fina, con altura de celda de 2,5 veces el soporte nominal de composite.
- **B. 20 × 20 × 10 m:** 28 × 29 × 47 = **38.164 bloques**; dimensión horizontal igual a la mediana de espaciamiento vecino y altura de celda de 5 veces el soporte nominal.
- **C. 40 × 40 × 20 m:** 14 × 15 × 24 = **5.040 bloques**; malla más gruesa, horizontal al doble de la mediana de espaciamiento.

Como referencia de costo de almacenamiento, solo 7 valores `float64` (centro XYZ, dimensiones XYZ y volumen) más 3 índices `int32` serían aproximadamente 68 bytes/bloque antes de IDs, estados, strings, formato CSV y estructuras en memoria: alrededor de 19,3 MiB para A, 2,5 MiB para B y 0,33 MiB para C. Los conteos finales dependen de origen, alineación y padding, aún no decididos. Estas opciones no resuelven extensión oficial, topografía ni asignación geológica.

**¿Qué escala candidata defenderías para continuar conceptualmente en P2, considerando resolución, espaciamiento real, soporte de composite y limitación de topografía?**

Elige A, B o C y justifica con una evidencia del repositorio, una ventaja y una limitación. La elección aún no autoriza construir la malla; el gate `P2_GRID` es independiente.

**Respuesta del estudiante — B:**

B. Defiendo 20 × 20 × 10 m como escala candidata para continuar conceptualmente en P2.

Evidencia del repositorio: la mediana de la distancia 3D mínima entre trayectorias vecinas es 20 m (rango 5.979–92.736 m, outputs/tables/m01_validacion_espacial.csv). Como es la distancia de máximo acercamiento, el espaciamiento típico entre sondajes es igual o mayor, así que celdas horizontales de 10 m (A) implicarían una resolución que los datos no tienen entre sondajes. En vertical, dz = 10 m equivale a 5 compósitos de 2 m (m01b_composites.csv), por lo que cada celda queda atravesada por varios compósitos donde hay sondaje. No es dx = dy = dz = longitud del compósito.

Ventaja: 38,164 bloques es manejable para generar, probar y visualizar en 3D. El tamaño horizontal es coherente con el espaciamiento observado, sin falsa resolución, y dz = 10 m todavía permite representar los cambios de litología en profundidad (82 contactos internos).

Limitación: con 20 m en planta, las zonas donde los sondajes están separados hasta 93 m seguirán sin soporte (quedarán UNKNOWN), y en zonas densas de contactos (REG→DIO) una celda de 10 m de alto puede contener más de un código, lo que exigirá una regla de desempate o un flag en P4. El conteo es provisional: falta definir origen, alineación y padding, y el límite superior depende de la topografía, que sigue bloqueada (B09).

**Evaluación conversacional:** PARCIAL — H1. La opción B es defendible como candidata conceptual y la aritmética de 38.164 celdas, la equivalencia de `dz=10 m` a cinco soportes nominales de 2 m y la limitación topográfica son coherentes. Sin embargo, `minimum_trajectory_distance_3d_m` es el acercamiento mínimo entre cada trayectoria y su vecina más próxima (35 valores; mediana 20,000 m; rango 5,979–92,736 m), no una medida directa del espaciamiento horizontal representativo a todas las profundidades. Por eso no basta para concluir que `dx=10 m` implica falsa resolución horizontal ni que todo el espacio mayor carece de soporte; habría que contrastar separaciones horizontales/verticales y distribución local. También es plausible, no comprobado con celdas aún inexistentes, que una celda de 10 m contenga varios códigos. Mantener B como candidata, sin declararla aprobada.

### Pregunta P2.2 — origen y alineación del grid

**Microteoría:** el tamaño de celda no determina por sí solo la malla: el origen define dónde caen límites y centros. Alinear el origen con mínimos observados puede producir límites reproducibles, pero se ancla a datos y puede desplazar la grilla respecto a convenciones del proyecto. Usar coordenadas redondeadas facilita lectura, aunque puede añadir padding y celdas sin soporte. El escenario requiere origen, orientación, alineación y tratamiento explícitos de bordes; la topografía no disponible impide validar el límite superior.

**Evidencia/faltantes:** la trayectoria observada tiene mínimos X = 242422,633 m, Y = 8196180,480 m y Z = 3059,530 m. La escala candidata P2.1 es 20 × 20 × 10 m, pero todavía no se eligió origen ni padding, y no hay convención de origen oficial ni topografía para fijar Z superior. El conteo de 38.164 asumía origen provisional en mínimos y `ceil(span/dim)`; cambiar origen puede cambiar el número y posición de celdas.

**¿Qué política de origen/alineación defenderías para continuar conceptualmente, manteniendo los límites como provisionales?**

- **A.** Anclar el origen en los mínimos observados de XYZ y alinear ejes con X/Y/Z del dataset; añadir solo el ajuste de borde necesario para cubrir el envolvente observado, sin llamar topografía al máximo Z.
- **B.** Redondear X/Y a múltiplos de 20 m y Z a múltiplos de 10 m respecto al sistema de coordenadas, aceptando padding y bloques adicionales para una grilla más legible.
- **C.** Posponer la selección del origen hasta obtener la convención oficial del proyecto y topografía; por ahora comparar dimensiones, sin fijar índices ni conteo definitivo.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. Esta decisión conceptual no autoriza generar el grid; `P2_GRID` sigue siendo un gate independiente.

**Respuesta del estudiante — B:**

B. Redondeo el origen a múltiplos del tamaño de bloque: X y Y a múltiplos de 20 m y Z a múltiplos de 10 m, alineado a los ejes X/Y/Z del dataset y con Z superior provisional.

Evidencia del repositorio: con los mínimos observados (X = 242422.633, Y = 8196180.480, Z = 3059.530) y la extensión de las 270 estaciones de drillhole_trajectory.csv, el origen redondeado queda en X0 = 242420, Y0 = 8196180, Z0 = 3050, y los máximos (≈ 242975.6 / 8196745.8 / 3524.0) se cubren con 28 × 29 × 48 = 38,976 bloques, frente a 38,164 anclando en los mínimos exactos: solo 812 bloques más (≈ 2.1 %), que corresponden a una capa adicional en Z y a bordes de pocos metros.

Ventaja: el origen y los límites de celda no dependen de los datos de un release concreto. Si se agregan sondajes o cambia el mínimo observado, los índices i, j, k de los bloques existentes se mantienen, y las coordenadas de centros y esquinas son números redondos fáciles de verificar en pruebas (centro = origen + (índice + 0.5) × tamaño).

Limitación: se agregan celdas de padding sin soporte de datos, que quedarán UNKNOWN o fuera de la envolvente. Los múltiplos se refieren a coordenadas sin CRS/EPSG documentado, así que la alineación no está garantizada con un sistema oficial. Además, la cota superior de 3530 m es provisional hasta tener topografía, y nz puede cambiar en P3.

**Evaluación conversacional:** CORRECTA — H0. El cálculo del origen redondeado y 38.976 bloques fue reproducido sobre las 270 estaciones; respecto del origen exacto y las mismas dimensiones, agrega 812 celdas (2,13 %), una capa vertical. La decisión de mantener el límite Z provisional y reconocer que el CRS no está documentado es apropiada. La estabilidad de índices al agregar datos depende de mantener fija la misma base de coordenadas, orientación, origen y dimensiones; no implica alineación oficial ni validez topográfica.

### Pregunta P2.3 — padding adicional y límite provisional

**Microteoría:** cubrir el envolvente de trayectorias con `floor` en los mínimos y `ceil` en los máximos ya genera márgenes parciales por alineación; añadir padding completo crea más celdas sin observaciones directas y aumenta costo/UNKNOWN. No añadir margen extra limita extrapolación, pero podría dejar sin espacio de trabajo zonas periféricas que luego justifique el proyecto. Esperar topografía oficial antes de fijar el límite superior evita presentarlo como definitivo, aunque impide cerrar el conteo de producción.

**Evidencia/faltantes:** con origen redondeado `(242420, 8196180, 3050)` y celdas de 20 × 20 × 10 m, los máximos observados se cubren con 28 × 29 × 48 = 38.976 celdas, hasta `(242980, 8196760, 3530)`. Ese conteo ya cubre el envolvente observado, con bordes de alineación; un bloque adicional en cada cara produciría 30 × 31 × 50 = 46.500 celdas. No hay topografía ni margen espacial minero documentado, y la cota 3530 m no es superficie oficial.

**¿Qué política conceptual propones para el padding y el límite superior provisional?**

- **A.** No añadir padding de bloque completo más allá del necesario para cubrir el envolvente observado; conservar los límites resultantes como provisionales y revisar Z cuando se verifique topografía.
- **B.** Añadir un bloque de padding en cada cara (30 × 31 × 50 = 46.500 celdas), marcar celdas sin soporte como `UNKNOWN` y declarar provisional el límite Z superior hasta P3.
- **C.** No fijar aún el padding ni un conteo candidato; dejar el cierre de límites, especialmente Z, para cuando haya topografía y una extensión de proyecto aprobada.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. Sigue siendo planificación conceptual; no genera el grid ni levanta el bloqueo B09.

**Respuesta del estudiante — A:**

A. No añado padding completo más allá del necesario para cubrir las trayectorias: mantengo 28 × 29 × 48 = 38,976 celdas con origen (242420, 8196180, 3050) y límite (242980, 8196760, 3530), con todos los límites provisionales y Z superior a revisar con la topografía en P3.

Evidencia del repositorio: el redondeo del origen ya agrega bordes parciales para cubrir los extremos de las 270 estaciones de drillhole_trajectory.csv (las 35 trayectorias quedan dentro). Añadir una celda en cada cara daría 30 × 31 × 50 = 46,500 celdas: 7,524 celdas más (+19.3 %), todas fuera del envolvente de los sondajes y sin compósitos que las respalden. En el repositorio no hay una extensión de proyecto aprobada ni un margen minero documentado que justifique ampliar el volumen.

Ventaja: el modelo se limita al volumen donde hay información, evita extrapolar dominios a zonas sin datos y mantiene un tamaño manejable para pruebas y visualización 3D.

Limitación: si más adelante se justifica una zona periférica (por ejemplo, para un pit o para la topografía oficial con mayor cobertura), habrá que ampliar la malla y recalcular el conteo. Los bloques de la periferia actual siguen teniendo poco soporte. La cota superior de 3530 m depende de los collars y no de la superficie real, así que nz puede cambiar en P3.

**Evaluación conversacional:** CORRECTA — H0. La lectura independiente confirmó 270 estaciones de 35 sondajes, sin estaciones fuera de los límites candidatos `(242420,242980) × (8196180,8196760) × (3050,3530)`. El conteo sin padding adicional es 38.976; añadir un bloque por cara da 46.500, una diferencia de 7.524 (19,304 %). Se reconoce correctamente que esos límites son el envolvente de trayectorias y no la extensión de proyecto/topografía; que no haya estaciones dentro de padding adicional no demuestra que el volumen sea innecesario para un proyecto minero, solo que no tiene soporte de sondajes en este release.

### Pregunta P2.4 — convención de ejes y elevación vertical

**Microteoría:** la malla debe usar una convención de coordenadas consistente para que índices, centros y superficies puedan compararse. Mantener los ejes originales evita transformaciones no sustentadas; documentar Z positivo hacia arriba es coherente con elevaciones, pero requiere confirmación al integrar topografía. Una rotación a coordenadas locales puede ser útil si el proyecto tiene orientación preferente, pero no debe inventarse sin evidencia. El CRS/datum no se debe inferir solo por magnitud de coordenadas.

**Evidencia/faltantes:** `drillhole_trajectory.csv` contiene `x`, `y`, `z` en valores numéricos positivos; en los sondajes, Z de collar es mayor que Z de fondo. El contrato del escenario exige orientación y signo vertical explícitos. No hay CRS/EPSG/datum documentado ni topografía oficial para comprobar compatibilidad.

**¿Qué convención de ejes propones para la geometría conceptual del grid?**

- **A.** Conservar X/Y/Z del dataset, sin rotación, con X/Y en sus ejes actuales y Z numérico positivo hacia arriba; declarar CRS/datum desconocidos y confirmar convención antes de integrar topografía.
- **B.** Transformar a coordenadas locales orientadas según la tendencia principal de los sondajes, fijando un azimut local a partir de la trayectoria dominante.
- **C.** Posponer cualquier decisión de signo/ejes hasta que se entregue el CRS y la topografía, sin asumir siquiera Z positivo hacia arriba.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. Es conceptual: no transforma coordenadas ni genera grid; B09 permanece bloqueado.

**Respuesta del estudiante — A:**

A. Conservo X/Y/Z sin rotación, alineando la malla a los ejes del dataset, con Z numérico positivo hacia arriba (elevación); declaro CRS y datum como desconocidos y confirmaré la compatibilidad antes de integrar cualquier topografía.

Evidencia del repositorio: en drillhole_trajectory.csv la Z de los collars (3288–3524 m) es mayor que la de los fondos (3059.530–3097.320 m), lo que confirma que Z crece hacia arriba. Esto es coherente con las convenciones de desurvey definidas en M01 (IMP-001, commit 1e26f5f), que ya produjeron los XYZ de m01b_composites.csv. Las campañas no tienen todas el mismo azimut (en la T1 se usó 145° como dominante solo para C01/C02), así que no hay una única tendencia que justifique una rotación local. Ningún archivo de data/raw/ documenta CRS, EPSG ni datum.

Ventaja: la malla queda en el mismo sistema que trayectorias y compósitos, sin transformaciones que podrían introducir errores. Las pruebas de índices y centros son directas, y el visualizador 3D puede superponer bloques y sondajes sin conversión.

Limitación: si los cuerpos o contactos tienen una orientación oblicua a X/Y, una malla no rotada los representa en escalera. Además, sin CRS ni datum conocidos no puedo garantizar que una topografía futura use el mismo sistema: habrá que comprobar coordenadas, elevaciones y unidades antes de integrarla en P3.

**Evaluación conversacional:** CORRECTA — H0. La lectura confirmó que Z de collar (3.288–3.524 m) supera Z al fondo (3.059,530–3.097,320 m); IMP-001, commit `1e26f5f`, documenta convenciones de desurvey que sustentan los XYZ derivados. La respuesta conserva coordenadas sin transformación e identifica CRS/datum como desconocidos; los datos de Z sustentan la dirección vertical observada, no identifican un datum absoluto. El archivo `data/raw/` no contiene referencias EPSG/CRS/datum. No se concluye que 145° deba ser una rotación; la orientación local no está establecida como requisito.

### Pregunta P2.5 — revisión de escala horizontal según espaciamiento en collar

**Microteoría:** la distancia mínima 3D entre trayectorias resume el acercamiento de cada trayectoria vecina en cualquier punto; no es equivalente al espaciamiento horizontal entre collares. Para juzgar `dx/dy` conviene observar también la distribución de distancias XY entre collares. La distancia al vecino más cercano por collar informa densidad local pero no toda la cobertura ni el espaciamiento a profundidad; por tanto, sirve como evidencia comparativa, no como prueba suficiente de resolución geológica.

**Evidencia del repositorio:** cálculo de solo lectura sobre las estaciones de profundidad 0 de las 35 trayectorias: distancia XY al collar más cercano por sondaje: mínimo **20,000 m**, mediana **60,000 m**, máximo **92,195 m**. Al mantener `dz=10 m`, usar origen horizontal redondeado a múltiplos del tamaño candidato y conservar Z desde 3050 hasta 3530 m, los conteos conceptuales serían:

- **A. 20 × 20 × 10 m:** origen XY `(242420, 8196180)`, `28 × 29 × 48` = **38.976 bloques**.
- **B. 40 × 40 × 10 m:** origen XY `(242400, 8196160)`, `15 × 15 × 48` = **10.800 bloques**.
- **C. 60 × 60 × 10 m:** origen XY `(242400, 8196180)`, `10 × 10 × 48` = **4.800 bloques**.

Estos conteos cubren el envolvente de trayectoria observado con redondeo por candidato; no representan un grid generado, extensión minera aprobada ni límite topográfico. Una escala horizontal menor da más detalle/costo y más celdas sin soporte local; una mayor reduce bloques pero puede ocultar variación. Los espaciamientos cercanos a collar no determinan por sí solos espaciamiento a profundidad ni continuidad de dominios.

**¿Qué tamaño horizontal mantendrías como candidato conceptual para P2, dejando `dz=10 m` provisional?**

Elige A, B o C y justifica con una métrica real del repo, una ventaja y una limitación. Esta respuesta permite revisar la PARCIAL de P2.1; no aprueba ni genera el grid y no cambia `RECOVERY_BLOCKED`.

**Respuesta del estudiante — A:**

A. Mantengo 20 × 20 m en planta con dz = 10 m provisional (38,976 bloques) como candidato conceptual para P2.

Métrica real: la distancia XY al collar más cercano es de 20.000 m mínimo, 60.000 m mediana y 92.195 m máximo, y la distancia 3D mínima entre trayectorias tiene mediana de 20 m porque los sondajes inclinados se acercan en profundidad. Un tamaño horizontal de 20 m equivale a 1/3 de la mediana de espaciamiento en collar, dentro del rango práctico de 1/3 a 1/2 del espaciamiento, y coincide con el espaciamiento mínimo. 40 m sería ≈ 2/3 y 60 m sería igual a la mediana, de modo que la mayoría de los bloques tendría como mucho un sondaje.

Corrección de conteo: con 40 × 40 × 10 m y el origen (242420, 8196180, 3050), nx = 560/40 = 14, ny = ceil(580/40) = 15, nz = 48, por lo que el total es 14 × 15 × 48 = 10,080 bloques, no 10,800.

Ventaja: con una asignación categórica, celdas de 20 m respetan mejor los contactos observados (82 internos) y las zonas de sondajes cercanos, sin llegar a celdas más finas que el espaciamiento mínimo. 38,976 bloques sigue siendo manejable para probar y visualizar.

Limitación: en las zonas donde los collars están a 60–92 m, muchos bloques de 20 m quedarán sin soporte directo (UNKNOWN), y el tamaño puede sugerir más detalle del que hay entre sondajes. Por eso la asignación debe incluir distancia al soporte y causa de UNKNOWN. La escala es provisional y no autoriza generar la malla; B09 sigue bloqueado.

**Evaluación conversacional:** PARCIAL — H1. La mediana de distancia XY al collar más cercano (60 m) y el mínimo (20 m) respaldan la existencia de zonas con densidad variable y hacen de 20 m una candidata razonable para comparar; el conteo de 38.976 corresponde a la envolvente/origen ya declarados. Sin embargo, el rango práctico de 1/3–1/2 se presenta sin fuente o validación específica del ejercicio, y los mínimos al collar no describen espaciamiento a profundidad. Tampoco se ha demostrado que la mayoría de bloques de 40/60 m contenga como mucho un sondaje ni que una celda de 20 m “respete” contactos: son inferencias que requieren distribución espacial por bloque y una política P4. Sobre la corrección aritmética, 10.080 es correcto si se fija el origen previo `(242420, 8196180)` también para el candidato de 40 m; pero ese origen no es múltiplo de 40. Con la regla previamente decidida de redondear origen a múltiplos del tamaño de bloque, el origen de 40 m es `(242400, 8196160)` y el conteo verificado es 10.800. La elección de 20 m queda como candidata, no como tamaño aprobado ni resolución demostrada.

**Microteoría de revisión:** comparar conteos exige declarar el origen de cada candidato: mantener un origen común facilita comparar la misma retícula, mientras redondear cada origen al múltiplo de su tamaño conserva la regla de alineación elegida, pero desplaza la retícula. Los conteos no son comparables como si solo cambiara el tamaño si también cambian los orígenes. Los espaciamientos al collar describen densidad en superficie; no bastan para afirmar cuántos sondajes cruzarán cada bloque ni cómo se resuelven contactos.

**Evidencia verificada:** bajo origen común `(242420, 8196180, 3050)`, 40×40×10 m da `14×15×48 = 10.080`; bajo origen redondeado a múltiplos de 40 `(242400, 8196160, 3050)`, da `15×15×48 = 10.800`. Los conteos se calcularon de los límites observados en `drillhole_trajectory.csv`; no se generó la malla. Los collars tienen distancia XY al vecino más cercano 20,000–92,195 m, mediana 60,000 m; la mediana 3D mínima entre trayectorias es un estadístico distinto y no sustituye la métrica horizontal.

**Revisión de P2.1 pendiente:** con la evidencia disponible, ¿qué postura deseas mantener para continuar conceptualmente?

- **A.** Mantener 20×20×10 m como candidata de trabajo, pero retirar las afirmaciones de resolución demostrada y de que “respeta” contactos; reconocer que la regla 1/3–1/2 es una heurística no validada aquí y dejar verificación espacial para P4.
- **B.** Comparar 20×20×10 m con 40×40×10 m usando el mismo origen explícito para ambos conteos, sin elegir aún una escala por el número de bloques.
- **C.** Suspender la selección de escala horizontal hasta obtener un análisis de espaciamiento a profundidad/cobertura local, manteniendo todas las dimensiones como alternativas no priorizadas.

Elige A, B o C y justifica con evidencia del repo, una ventaja y una limitación. Esta revisión no autoriza generar la malla; B09 sigue `RECOVERY_BLOCKED`.

**Respuesta del estudiante — A:**

A. Mantengo 20 × 20 × 10 m como candidata conceptual, con afirmaciones moderadas: es una escala plausible, no una resolución demostrada, y la verificación espacial del soporte y de los contactos queda para P4.

Evidencia del repositorio: la distancia XY al collar más cercano varía entre 20 y 92.195 m (mediana 60 m) y la distancia 3D mínima entre trayectorias tiene mediana de 20 m, lo que muestra densidad de datos variable. Ya están registradas tres alternativas con sus conteos: 20 × 20 × 10 m = 38,976; 40 × 40 × 10 m = 10,800 (origen alineado a 40 m, 242400 / 8196160 / 3050; corrijo mi conteo de 10,080, que usaba un origen no alineado con la regla de P2.2); 60 × 60 × 10 m = 4,800. La regla de 1/3–1/2 del espaciamiento la uso solo como heurística, no como validación.

Ventaja: puedo avanzar a P3/P4 con una escala candidata definida y trazable. La decisión puede revisarse con evidencia real en P4 (cuántos bloques quedan con soporte, a qué distancia y cuántos con códigos en conflicto), en vez de discutirla solo con distancias en collar.

Limitación: todavía no demuestro que 20 m represente adecuadamente los contactos ni que haya soporte a profundidad en cada bloque. Si en P4 resulta una proporción muy alta de UNKNOWN o celdas con varios códigos, habrá que reconsiderar 40 × 40 × 10 m. La escala sigue siendo provisional y no autoriza generar la malla; B09 sigue bloqueado.

**Reevaluación conversacional:** CORRECTA — H0. La respuesta modera explícitamente las afirmaciones no demostradas, deja la razón 1/3–1/2 como heurística, reconoce que soporte/contactos se verificarán en P4 y corrige el conteo de 40×40×10 m conforme al origen alineado a múltiplos de 40 m. Se mantiene 20×20×10 m como escala candidata de trabajo, no como resolución aprobada; B09 sigue bloqueado.

### Pregunta P2.6 — identificadores e índices reproducibles

**Microteoría:** `block_id` debe identificar una sola celda y sus índices deben permitir reconstruir centro y límites sin ambigüedad. Un orden lexicográfico explícito y una convención de índices (por ejemplo, base cero desde el origen) permiten reproducir resultados y probar esquinas/centros. Un ID secuencial compacto depende del orden de recorrido; un ID construido con índices hace la relación espacial visible, aunque puede ser más largo. El escenario requiere IDs únicos, índices, centros, dimensiones y pruebas de orden/reproducibilidad, pero no impone un formato único.

**Evidencia/faltantes:** el esquema del escenario propone `block_id`, `index_i/index_j/index_k`, `center_x/center_y/center_z`, `dx/dy/dz` y `nominal_volume`, y exige pruebas de IDs únicos, orden/índices, centros/esquinas y reproducibilidad. Aún no hay grid generado ni convención local de índice base, eje de recorrido, orden de serialización o formato de `block_id`.

**¿Qué convención de identificación e índices propones para la malla conceptual?**

- **A.** Índices base cero desde el origen; definir `i` sobre X, `j` sobre Y, `k` sobre Z; construir `block_id` determinista a partir de `(i,j,k)` y fijar explícitamente el orden de recorrido, por ejemplo `k` exterior, luego `j`, `i` interior.
- **B.** Índices base uno y `block_id` secuencial desde 1 en el orden de filas; guardar también `(i,j,k)` para poder reconstruir ubicación, con el orden documentado.
- **C.** Usar coordenadas del centro redondeadas como `block_id` y omitir índices, para que las filas se interpreten visualmente sin una secuencia de indexación.

Elige A, B o C y justifica con una evidencia del escenario o arquitectura, una ventaja y una limitación. Es una decisión conceptual: no genera grid ni aprueba el gate `P2_GRID`; topografía y B09 siguen bloqueados.

**Respuesta del estudiante — A:**

A. Índices base cero con i→X, j→Y, k→Z; block_id determinista calculado desde (i, j, k) como block_id = i + j·nx + k·nx·ny, con recorrido k exterior, después j, e i interior.

Evidencia del escenario y la arquitectura: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md pide block_id, index_i, index_j, index_k, center_x/y/z, dx/dy/dz y nominal_volume, y P2 exige pruebas de IDs únicos, orden e índices, centro/esquinas correctos y reproducibilidad. En B08 ya usamos una convención determinista (composite_id = hole_id + secuencia), así que mantengo el mismo criterio. Con la candidata 20 × 20 × 10 m y origen (242420, 8196180, 3050): nx = 28, ny = 29, nz = 48, los IDs van de 0 a 38,975, y el centro se obtiene como center_x = 242420 + (i + 0.5)·20, center_y = 8196180 + (j + 0.5)·20, center_z = 3050 + (k + 0.5)·10.

Ventaja: el ID y la ubicación se pueden reconstruir uno desde el otro sin depender del orden de las filas en el archivo, lo que permite probar unicidad, índices y centros con casos simples (por ejemplo, block_id 0 → (0, 0, 0) → centro (242430, 8196190, 3055)). Base cero coincide con Python/numpy y evita errores de media celda.

Limitación: el block_id depende de nx y ny, por lo que si cambia la extensión (por ejemplo, con la topografía en P3 o con otro tamaño de bloque) cambian los IDs y no son comparables entre versiones. Por eso hay que guardar también i, j, k y registrar la versión de la geometría. Base cero puede confundir a quien lea la tabla esperando índices desde 1.

**Evaluación conversacional:** CORRECTA — H0. La fórmula corresponde al recorrido `k` exterior, `j` intermedio, `i` interior; para `nx=28`, `ny=29`, `nz=48` produce 38.976 IDs únicos de 0 a 38.975. Los ejemplos `block_id=0 → (0,0,0)` y centro `(242430,8196190,3055)` son correctos. `nominal_volume` de la candidata es 4.000 m³ por celda completa. Se mantiene como especificación conceptual: cambio de geometría puede cambiar IDs y `P2_GRID` no está aprobado.

### Pregunta P2.7 — tratamiento de celdas en bordes del envolvente

**Microteoría:** cuando el tamaño de celda no divide exactamente la extensión observada, se puede extender el límite del grid hasta completar la última celda, crear celdas de borde con dimensiones parciales o recortar el envolvente. Las celdas completas preservan un tamaño nominal uniforme y facilitan índices/volúmenes, pero parte de su volumen puede quedar fuera de la huella observada; una celda parcial representa el borde con más precisión, pero requiere almacenar dimensiones/volumen efectivo distinto del nominal. Recortar puede excluir estaciones periféricas y perder cobertura.

**Evidencia/faltantes:** con la candidata provisional y origen redondeado, las dimensiones son 20 × 20 × 10 m, `nominal_volume=4.000 m³`; el grid cubre X hasta 242980, Y hasta 8196760 y Z hasta 3530, mientras los máximos observados son aproximadamente X 242975,603, Y 8196745,780 y Z 3524. El exceso de borde se debe al `ceil`/alineamiento. No hay topografía ni decisión sobre fracción de roca/volumen efectivo, y no se ha generado la malla.

**¿Qué convención conceptual propones para los bloques que cubren los bordes?**

- **A.** Mantener celdas completas y `nominal_volume=4.000 m³` uniforme; documentar límites del grid y que parte del borde puede quedar fuera de la envolvente de sondajes, sin llamarlo volumen de roca.
- **B.** Permitir dimensiones parciales en las caras exteriores y registrar `dx/dy/dz` y volumen nominal por celda según el tamaño real de borde.
- **C.** Recortar el límite superior de cada eje al máximo observado, aceptando que el borde final no quede cubierto por una celda completa y definiendo aparte cómo se manejarían las estaciones periféricas.

Elige A, B o C y justifica con evidencia del escenario, una ventaja y una limitación. Es conceptual: no genera el grid, no calcula volumen de roca y no levanta el gate `P2_GRID` ni el bloqueo topográfico B09.

**Respuesta del estudiante — A:**

A. Mantengo celdas completas de 20 × 20 × 10 m con volumen nominal uniforme de 4,000 m³ y documento que parte del borde queda fuera de la envolvente de los sondajes, sin llamarlo volumen de roca.

Evidencia del escenario: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md indica que nominal_volume es el volumen de la celda, no el volumen neto de roca, y que este último requiere una regla de ocupación aparte (que aquí no existe, porque falta la topografía). Los márgenes que agrega el redondeo son pequeños frente al tamaño de celda: ≈ 2.6 m (X mín), 0.5 m (Y mín), 9.5 m (Z mín), 4.4 m (X máx), 14.2 m (Y máx) y 6 m (Z máx), es decir, menos de una celda en cada cara.

Ventaja: geometría regular y simple. Todas las celdas tienen el mismo dx/dy/dz y volumen, los centros siguen la fórmula origen + (índice + 0.5)·tamaño y las pruebas de centros, esquinas y volúmenes son directas. Ninguna estación de trayectoria queda fuera de la malla.

Limitación: las celdas de borde incluyen volumen sin perforación, que no debe interpretarse como roca con soporte; esas celdas deberán quedar UNKNOWN o marcadas en P4. El volumen nominal total (38,976 × 4,000 m³) no es volumen de roca: en la parte superior puede incluir aire, y eso solo se resolverá con topografía en P3 (B09 sigue bloqueado).

**Evaluación conversacional:** CORRECTA — H0. Se verificaron los márgenes exactos respecto de los límites candidatos: X 2,633/4,397 m; Y 0,480/14,220 m; Z 9,530/6,000 m. Los seis son menores que una celda en sus respectivos ejes y no hay estaciones de trayectoria fuera del envolvente. El volumen nominal por celda es 4.000 m³ y el total nominal de la retícula sería 155.904.000 m³; no es volumen de roca ni volumen validado por topografía. El estado `UNKNOWN`/flag para bordes sin soporte queda como propuesta para P4, no como atributo generado.

### P4.1 — regla conceptual de asignación categórica bajo incertidumbre

**Microteoría:** una regla por vecino más cercano es reproducible, pero puede propagar un código a través de contactos y a grandes distancias. Una mayoría de vecinos puede reducir sensibilidad a una observación aislada, aunque un empate o códigos mezclados requieren una política explícita. Exigir concordancia entre los soportes antes de asignar conserva `UNKNOWN` donde la evidencia se contradice, a costa de reducir cobertura. Cualquier umbral de distancia, número de vecinos y desempate debe justificarse y probarse; no debe derivarse automáticamente del tamaño de celda.

**Evidencia/faltantes:** los 5.332 composites tienen coordenadas XYZ y `lith_code`, preservan trazabilidad a `sample_id` y no son observaciones independientes en los 57 assays partidos. Se observaron códigos `REG`, `DIO`, `POR`, `BRX` y `AIR`; `AIR` permanece apartado con `REVIEW/UNKNOWN`. Las distancias entre trayectorias y entre collares varían ampliamente. No hay superficies geológicas interpretadas, topografía, regla de vecindad aprobada ni umbral de soporte validado. Por B09, esta etapa es solo conceptual: no se asigna ningún bloque ni se usa `topo_status` inferido.

**¿Qué principio de asignación categórica propones si P4 se autoriza después de resolver sus prerequisitos?**

- **A.** Asignar el código del composite más cercano solo dentro de una distancia máxima aprobada; si excede el umbral, dejar `UNKNOWN`. Cerca de contactos, el más cercano puede dominar aunque haya otro código vecino.
- **B.** Usar los `k` composites más cercanos con una regla de mayoría; exigir distancia máxima y dejar `UNKNOWN` en empate o falta de mayoría. Esto requiere decidir `k`, radio y tratamiento de los segmentos derivados de un mismo `sample_id`.
- **C.** Asignar solo si todos los soportes dentro de un radio aprobado son concordantes; si hay códigos en conflicto, ningún soporte suficiente o el radio no contiene observaciones, dejar `UNKNOWN` con causa. Esto prioriza evitar propagación ambigua, pero reduce cobertura.

Elige A, B o C y justifica con evidencia del repo, una ventaja y una limitación. No fijes números sin soporte validado. Esta decisión no autoriza implementación: B09 sigue `RECOVERY_BLOCKED`, `P2_GRID` no está aprobado y aún no existe topografía verificada.

**Respuesta del estudiante — C:**

C. Asigno un código solo si todos los composites dentro de un radio aprobado concuerdan; si hay conflicto o soporte insuficiente, el bloque queda UNKNOWN con causa (CONFLICTING_CODES o INSUFFICIENT_SUPPORT). El radio no lo fijo todavía porque no hay un umbral validado.

Evidencia del repositorio: es coherente con lo que registré en P1.3 y P1.4 (T2_M01B_PLAN_G04.md). Los 82 contactos internos de lithology.csv son evidencia observada, pero no hay superficies de contacto interpretadas que validen su continuidad, y en zonas con códigos en disputa decidí dejar UNKNOWN en lugar de propagar un código. m01b_composites.csv tiene 5,332 composites con XYZ, lith_code y procedencia, y 57 sample_id repetidos en dos segmentos: con la regla de concordancia esos segmentos no pesan doble en ninguna votación, porque no se cuentan votos.

Ventaja: no se inventa ninguna frontera ni se elige un código por mayoría donde los datos se contradicen. Cada bloque asignado tiene soporte unánime, y cada UNKNOWN tiene una causa auditable, con composite_id de soporte y distancia, como se definió en P1.5.

Limitación: la cobertura será menor que con vecino más cercano o mayoría. Cerca de cada contacto (sobre todo en las 31 transiciones REG→DIO) y en las zonas donde los collars están a 60–92 m, muchos bloques quedarán UNKNOWN. El resultado depende mucho del radio: uno grande aumenta los conflictos y uno pequeño aumenta el soporte insuficiente, por lo que habrá que comparar al menos dos radios cuando se autorice la implementación.

**Evaluación conversacional:** CORRECTA — H0. La regla es coherente con P1.3/P1.4 y no se inventa una frontera ni se fijan umbrales sin validación; se preserva `UNKNOWN` con causa. La lectura confirmó 5.332 composites con coordenadas XYZ y código litológico, 57 `sample_id` que aparecen exactamente dos veces, y un solo composite `AIR` que se mantiene excluido/review según P1.2. Al no usar votación, los segmentos del mismo ensayo no aportan votos duplicados; al implementar deberá precisarse cómo se agrupan para métricas de soporte, manteniendo la geometría/litología segmentada y distinguiendo recuento de filas de número de mediciones originales. Comparar al menos dos radios y reportar cobertura/conflictos es un requisito futuro, no prueba ya realizada. No hay asignación de bloques ni gate P4 aprobado.

### P4.2 — tratamiento de ensayes partidos en la métrica de soporte

**Microteoría:** los dos segmentos de 1 m de un assay partido son ubicaciones geométricas distintas, pero comparten una única medición analítica y la misma ley original. Por ello se pueden conservar ambos para ubicar contactos, pero contarlos como dos observaciones independientes inflaría el soporte. Si los segmentos de un mismo `sample_id` caen cerca de un bloque con códigos distintos, se debe diferenciar la discordancia espacial de dos ensayes independientes.

**Evidencia/faltantes:** hay 57 `sample_id` repetidos exactamente dos veces entre 5.332 composites; ambos segmentos derivan de un assay original y pueden tener litologías distintas a lados opuestos de un contacto. P4.1 eligió concordancia unánime sin votación, pero no fijó cómo calcular `support_count` ni cómo declarar conflictos cuando una misma fuente aparece en segmentos distintos. No hay radio aprobado ni asignación ejecutada.

**¿Cómo propones tratar esos segmentos al calcular la métrica de soporte de una futura asignación?**

- **A.** Mantener cada segmento como soporte espacial y litológico, pero contar `support_count` por `sample_id` único; si una fuente aparece con códigos distintos dentro del soporte relevante, marcar conflicto/`UNKNOWN`.
- **B.** Para cada `sample_id`, conservar solo el segmento más cercano al centro del bloque como soporte y código; resolver empates con una regla determinista, aceptando que el otro lado del contacto no influya.
- **C.** Excluir de la métrica de soporte cualquier ensayo partido, conservando los segmentos en la tabla para geometría, y aceptar que disminuya el soporte cerca de contactos.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. Es una decisión conceptual; no calcula asignaciones, no fija radio y no autoriza código.

**Respuesta del estudiante — A:**

A. Conservo ambos segmentos como soporte espacial y litológico, cuento support_count por sample_id único (no por segmento) y marco CONFLICTING_CODES/UNKNOWN si una misma fuente aparece con códigos distintos dentro del soporte relevante.

Evidencia del repositorio: en m01b_composites.csv hay 57 sample_id repetidos exactamente dos veces; todos son ensayes de 2 m partidos 1 m + 1 m por un contacto de lithology.csv (1.081 % de los 5,275 ensayes, en 35 sondajes). El lith_code de cada segmento proviene del registro litológico y no del ensaye, así que cada mitad es una observación litológica válida en su posición. Lo que comparten es la misma medición analítica (cu_pct heredado), que en T2 no se usa para estimar ley a bloques.

Ventaja: se conserva la evidencia espacial a ambos lados del contacto, que es justo donde la asignación es más delicada, sin inflar el número de fuentes analíticas independientes. Es coherente con P4.1: un sample_id partido dentro del radio de un bloque implica códigos distintos, y por lo tanto el bloque queda UNKNOWN por CONFLICTING_CODES en lugar de tomar un lado arbitrariamente.

Limitación: hay que guardar y probar dos métricas distintas (segmentos y sample_id únicos), lo que añade complejidad. Además, cerca de esos 57 contactos aumentarán los bloques UNKNOWN. Contar por sample_id tampoco resuelve que los composites de un mismo sondaje estén correlacionados entre sí: el soporte sigue concentrado a lo largo de cada trayectoria.

**Evaluación conversacional:** CORRECTA — H0. La lectura confirmó 57 `sample_id` repetidos exactamente dos veces; ambos segmentos miden 1 m, comparten `cu_pct`, tienen distinto `lith_code`, y los 57 casos aparecen en 35 sondajes. El porcentaje 57/5.275 = 1,081 % es correcto. Contar fuentes analíticas únicas y conservar ambos segmentos para localización litológica evita inflar el soporte por fuente sin borrar la evidencia del contacto. Se registra también la limitación de correlación entre composites del mismo sondaje. No se ha calculado soporte de bloques ni fijado radio.

### P4.3 — selección conceptual de radios para análisis de sensibilidad

**Microteoría:** un radio pequeño restringe asignaciones a soporte cercano y suele aumentar `UNKNOWN`; uno grande puede reducir `UNKNOWN`, pero incluir más códigos en conflicto y extrapolar a distancias mayores. Comparar radios requiere medir el resultado bajo la misma geometría y regla, sin elegir el radio que solo maximice cobertura. Los radios se deben justificar con espaciamiento y soporte reales y reportar sensibilidad de asignaciones, conflictos y no asignaciones. Sin grid, estos son criterios de diseño, no resultados.

**Evidencia/faltantes:** hay 5.332 segmentos de composite, 5.275 `sample_id` originales representados, 57 assays partidos en dos segmentos de 1 m y distancias XY a collar vecino de 20–92,195 m (mediana 60 m). La candidata conceptual de celda es 20×20×10 m, pero `P2_GRID` no está aprobado y no hay asignación, topografía ni radio validado. Los segmentos de un assay partido se conservarán en geometría, con soporte por fuente única según P4.2.

**¿Qué criterio propones para comparar radios cuando el análisis P4 pueda ejecutarse?**

- **A.** Seleccionar al menos dos radios de prueba a partir de la distribución observada de distancias entre datos y reportar para cada uno proporción de bloques `ASSIGNED/UNKNOWN`, distancia de soporte y conflictos; justificar el radio preferido por el balance de cobertura y ambigüedad, no solo por maximizar asignaciones.
- **B.** Usar radios derivados de dimensiones de celda (por ejemplo, medio diagonal y diagonal completa) como escenarios geométricos, comparando soporte/conflictos y explicitando que no son umbrales geológicos validados.
- **C.** No definir todavía el método de selección ni los escenarios de radio; esperar a disponer del grid y de topografía verificados y después formular P4 con cobertura real.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. No propongas valores como validados ni ejecutes asignaciones; `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

**Respuesta del estudiante — A:**

A. Compararía al menos dos radios motivados por la distribución de distancias observada y, para cada uno, reportaría bloques ASSIGNED/UNKNOWN (separando CONFLICTING_CODES de INSUFFICIENT_SUPPORT), distancia al soporte y número de sample_id únicos. Elegiría por el balance entre cobertura y ambigüedad, no por maximizar asignaciones.

Evidencia del repositorio: la distancia XY al collar más cercano va de 20 a 92.195 m (mediana 60 m) y la distancia 3D mínima entre trayectorias tiene mediana de 20 m (outputs/tables/m01_validacion_espacial.csv). Con esa distribución, como escenarios de prueba (no umbrales validados) compararía un radio cercano a 20 m, que solo alcanza sondajes próximos, y otro cercano a 30 m (la mitad de la mediana en collar), que alcanza el sondaje vecino en zonas típicas. Como referencia geométrica, la media diagonal de una celda de 20 × 20 × 10 m es 15 m, así que un radio menor que eso dejaría sin soporte incluso parte de la propia celda atravesada. El conteo usaría las 5,275 fuentes únicas, no los 5,332 segmentos (P4.2).

Ventaja: los radios no son arbitrarios: se relacionan con el espaciamiento real de los sondajes. Las métricas permiten ver con números cuánto se gana en cobertura y cuánto aumentan los conflictos al ampliar el radio, en vez de elegir el que "llena" más el modelo.

Limitación: la comparación muestra el comportamiento de la regla, pero no valida geológicamente ningún radio. Las distancias en collar no representan el espaciamiento a profundidad, y el resultado dependerá de la malla y de la topografía, que siguen pendientes (P2_GRID y B09). Los valores de 20 y 30 m son candidatos de prueba, no parámetros aprobados.

**Evaluación conversacional:** CORRECTA — H0. Se propone análisis de sensibilidad con métricas separadas y se declaran 20/30 m como radios candidatos, no umbrales validados. La evidencia de espaciamiento XY a collares (20–92,195 m; mediana 60 m) y mediana de distancia 3D mínima (20 m) está registrada, pero son estadísticas distintas y ninguna valida por sí sola el radio a profundidad. La media diagonal de la celda es `sqrt(20²+20²+10²)/2 = 15 m`; es una referencia geométrica, no garantía de soporte para todos los puntos de una celda ni criterio geológico. El recuento por `sample_id` único sigue P4.2. No se ejecutó asignación ni se aprobó radio.

### P4.4 — concentración del soporte a lo largo de sondajes

**Microteoría:** contar `sample_id` únicos evita duplicar los ensayes partidos, pero varias muestras del mismo sondaje siguen siendo espacialmente correlacionadas y concentradas en una línea. Contar fuentes y contar sondajes responden preguntas diferentes: número de mediciones originales cercanas versus diversidad de trayectorias independientes que respaldan una categoría. Una regla puede reportar ambas métricas sin convertir automáticamente un conteo mínimo en validación geológica.

**Evidencia/faltantes:** hay 5.275 `sample_id` únicos en 35 sondajes; los composites están distribuidos a lo largo de esas trayectorias y 57 muestras se segmentaron en dos ubicaciones litológicas. No hay radio validado, grid generado, análisis de cobertura por bloque ni asignación ejecutada. P4.3 propone comparar radios de prueba y reportar soporte, conflictos y cobertura.

**¿Cómo propones reportar la concentración del soporte por sondaje en el análisis futuro?**

- **A.** Reportar por bloque tanto `n_sample_ids` únicos como `n_holes` distintos; conservar ambas métricas y evaluar si el soporte procede de una o varias trayectorias, sin fijar ahora un mínimo de asignación.
- **B.** Contar únicamente `n_holes` distintos para la decisión de asignar y usar `n_sample_ids` solo como dato de auditoría, priorizando independencia espacial sobre cantidad de mediciones.
- **C.** Mantener únicamente `n_sample_ids` únicos como soporte, reportar `hole_id` solo en procedencia y dejar el efecto de agrupamiento por sondaje para discusión de resultados.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. No fijes un mínimo no validado ni ejecutes asignación; `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

**Respuesta del estudiante — A:**

A. Reporto por bloque tanto n_sample_ids únicos como n_holes distintos, sin fijar ahora un mínimo de asignación; ambos quedan como evidencia de soporte junto con la distancia (P1.5).

Evidencia del repositorio: los 5,275 sample_id únicos están distribuidos en solo 35 sondajes, con 115 a 218 ensayes por sondaje, así que el soporte está muy concentrado a lo largo de cada trayectoria. Con celdas de 20 × 20 × 10 m y collars separados al menos 20 m (mediana 60 m), lo esperable es que muchas celdas sean atravesadas por un solo sondaje: un bloque podría tener unos 5 compósitos de 2 m (dz = 10 m) y aun así n_holes = 1.

Ventaja: se distinguen dos tipos de soporte, cuánta información hay y de cuántos lugares independientes proviene. Esto permite reconocer en P5 si un bloque asignado por concordancia descansa en un único sondaje, que no aporta evidencia de continuidad lateral, o en varios. Además, las métricas quedan disponibles para fijar un mínimo justificado después de comparar radios (P4.3).

Limitación: son dos columnas más que hay que calcular y probar, y ninguna mide continuidad geológica. n_holes no tiene en cuenta que dos sondajes pueden ser casi paralelos o converger (el par más cercano está a 5.979 m), por lo que dos sondajes no siempre son dos observaciones independientes. El mínimo de asignación sigue sin fijarse.

**Evaluación conversacional:** CORRECTA — H0. La lectura confirmó 5.275 `sample_id` únicos distribuidos en 35 sondajes, con 115–218 assays por sondaje; los composites contienen 5.332 filas y 5.275 fuentes únicas. Reportar fuentes y sondajes distintos separadamente distingue cantidad de muestras de diversidad de trayectorias. `n_holes` no prueba independencia geológica y el mínimo de soporte queda pendiente. Los conteos por bloque son una propuesta, no se han calculado porque no hay malla/asignación.

### P4.5 — política para composites con código `AIR`

**Microteoría:** `AIR` aparece en la tabla de litología/composites, pero su semántica no está documentada y P1.2 decidió conservarlo como código observado separado, `REVIEW/UNKNOWN`, fuera de la extensión volumétrica y sin traducirlo a `topo_status=AIR`. Si se incluye en la regla de concordancia litológica, puede contaminar soportes de roca; si se elimina sin registro, se pierde procedencia. Puede excluirse de la asignación de dominios rocosos conservando el registro y una causa explícita para revisión, hasta tener diccionario/topografía.

**Evidencia/faltantes:** una fila composite AIR (`CR-C02-002_0001`, MD 0–2 m) proviene de `lithology.csv`, inmediatamente sobre REG desde 2 m. No existe diccionario que defina AIR ni topografía oficial; P1.2 la mantiene separada y sin inferencia de aire físico. No hay asignación ejecutada ni regla de elegibilidad de soportes implementada.

**¿Cómo propones tratar el composite `AIR` si una futura asignación de dominios rocosos llega a autorizarse?**

- **A.** Excluirlo como soporte de dominios rocosos; conservarlo en la tabla con `REVIEW/UNKNOWN` y registrar que no participó, sin inferir `topo_status=AIR`.
- **B.** Incluir su código literal `AIR` como una categoría candidata de asignación, pero mantenerlo distinta de los estados topográficos y revisar toda asignación que lo use.
- **C.** Omitirlo de la asignación y de sus registros, para evitar que afecte el soporte, aceptando perder su trazabilidad en la salida de asignación.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. Esta decisión es conceptual; no cambia composites ni asigna bloques. `P2_GRID`, `P4_GEO_ASSIGN` y B09 continúan pendientes.

**Respuesta del estudiante — A:**

A. Excluyo el composite AIR como soporte de dominios rocosos, lo conservo con REVIEW/UNKNOWN en la tabla y registro explícitamente que no participó en la asignación; no infiero topo_status = AIR.

Evidencia del repositorio: es un único composite, CR-C02-002_0001 (MD 0–2 m, junto al collar, Cu = 0), seguido de REG desde 2 m. Su código proviene de lithology.csv, pero no existe en el repositorio un diccionario que lo defina ni una topografía verificada (B09 bloqueado). Es coherente con P1.2, donde decidí preservarlo separado y excluirlo de la extensión volumétrica de dominios, y con P1.5, donde exigí registrar la procedencia de cada asignación.

Ventaja: se evita que un código de significado incierto actúe como dominio rocoso o genere conflictos artificiales con REG en los bloques cercanos al collar de CR-C02-002, y la exclusión queda trazable (se sabe qué composite se dejó fuera y por qué).

Limitación: si AIR resultara ser roca (por ejemplo, un tramo sin recuperación), se pierde 2 m de soporte en la parte superior de ese sondaje, y los bloques cercanos podrían quedar con menos soporte o UNKNOWN. El significado real del código solo se resolverá con una definición oficial o con la topografía en P3.

**Evaluación conversacional:** CORRECTA — H0. La lectura confirmó un único composite `AIR` (`CR-C02-002_0001`, MD 0–2 m, Cu 0), con la fila fuente correspondiente en `lithology.csv` y `REG` a continuación desde 2 m. La política es coherente con P1.2: preservar procedencia, excluir del soporte de dominios rocosos y no inferir `topo_status=AIR`. La posible pérdida de soporte si el código significa roca queda como limitación. No se modificó el composite ni se ejecutó asignación.

### P4.6 — unidad espacial para evaluar soporte y conflicto

**Microteoría:** una regla por distancia necesita definir desde qué punto se mide la distancia al composite y cómo se relaciona con el volumen de la celda. Usar el centro es sencillo y reproducible, pero un composite puede atravesar una cara sin que su punto representativo quede dentro del radio; usar el segmento geométrico completo capta intersección, aunque requiere una distancia punto-segmento y reglas para unidades de soporte. Considerar todo el volumen de la celda como una unidad de vecindad puede incorporar soportes de esquinas alejadas; si hay varios códigos, P4.1 exige `UNKNOWN` con causa en lugar de desempatar. Esto es un criterio metodológico conceptual, no prueba geológica.

**Evidencia/faltantes:** composites tienen posicionamiento FROM/MID/TO XYZ y longitud real; el escenario requiere coordenadas del centro de bloque. P4.1–P4.5 definen concordancia, fuentes únicas, distinción por sondaje y exclusión de `AIR`, pero no han fijado qué geometría del composite entra en el radio ni cómo resolver muestras parciales/segmentos de 1 m. No hay grid ni radio aprobado.

**¿Qué geometría del composite propones usar para determinar soporte a un bloque en P4?**

- **A.** Medir distancia 3D entre el centro del bloque y `mid_x/mid_y/mid_z` del composite; mantener radio máximo aprobado y exigir concordancia de códigos entre fuentes elegibles.
- **B.** Medir la distancia mínima 3D desde el centro del bloque al segmento FROM–TO del composite, conservando `sample_id` único y tratando códigos en conflicto como `UNKNOWN`; requiere implementar y probar distancia punto-segmento.
- **C.** Considerar soporte si cualquier parte del segmento composite intersecta el volumen de la celda, sin radio; reportar conflictos por código y dejar fuera de cobertura lo no intersectado.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. No implica fijar un radio ni codificar; `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

**Respuesta del estudiante — A:**

A. Mido la distancia 3D entre el centro del bloque y el punto medio del composite (mid_x, mid_y, mid_z), aplicando un radio máximo aprobado y la regla de concordancia de códigos (P4.1), contando soporte por sample_id único (P4.2).

Evidencia del repositorio: en m01b_composites.csv los composites miden como máximo 2 m (5,188 de 2 m y 144 parciales más cortos), así que cualquier punto del segmento está a 1 m o menos de su punto medio. Por desigualdad triangular, la diferencia entre la distancia al punto medio y la distancia mínima al segmento es como máximo 1 m, frente a radios de prueba cercanos a 20 y 30 m (P4.3), es decir, ≤ 5 %. Todas las filas tienen mid_x/mid_y/mid_z calculados con el positioning de M01.

Ventaja: el cálculo es simple, rápido y fácil de probar con casos controlados (distancia punto-punto), y es coherente con los radios definidos en P4.3. Cada composite aporta un único punto, sin decisiones adicionales sobre segmentos parciales.

Limitación: un composite que pasa justo por el borde del radio puede quedar dentro o fuera por menos de 1 m de diferencia, y los parciales cortos se representan igual que uno de 2 m. Tampoco considera directamente si el segmento atraviesa la celda: un bloque cruzado por un sondaje quedaría siempre dentro del radio, pero la regla no lo distingue de uno cercano. Si en P5 aparecen casos límite, se podría comparar con la distancia al segmento (opción B).

**Evaluación conversacional:** CORRECTA — H0. La lectura confirmó 5.332 composites: 5.188 de 2 m y 144 parciales; todos contienen `mid_x/mid_y/mid_z`. Para segmentos de longitud ≤2 m, cualquier punto está a ≤1 m de su punto medio; por desigualdad triangular, la diferencia absoluta entre distancia al punto medio y distancia mínima al segmento es ≤1 m. Esto equivale como máximo al 5 % de un escenario de radio de 20 m o al 3,33 % de 30 m, no una garantía de equivalencia de clasificación cerca del umbral. Matiz: un segmento que atraviesa una celda está a no más de media diagonal (15 m) del centro en algún punto; su punto medio puede quedar hasta 1 m más lejos. Por ello, el punto medio quedaría dentro de radios de 20/30 m en ese caso, pero no se puede afirmar “siempre” para cualquier radio aprobado menor de 16 m. La elección es simple y trazable; la limitación de bordes y de no medir intersección con celda queda explícita. Los radios son escenarios aún no aprobados y no se calculó ninguna asignación.

### P4.7 — casos límite del umbral de distancia

**Microteoría:** con el centro del bloque–punto medio como métrica, la aproximación al segmento tiene una discrepancia geométrica acotada por la semilongitud (≤1 m en este release). Cerca del radio máximo, una pequeña diferencia puede cambiar qué fuentes entran al conjunto y, por tanto, cambiar de `ASSIGNED` a `UNKNOWN`/conflicto. Una política de margen puede marcar esos casos como revisión, o calcular la distancia exacta al segmento solo en una banda limítrofe; mantener solo el punto medio es más simple, pero acepta sensibilidad al umbral. El margen no es incertidumbre analítica ni una tolerancia geológica validada.

**Evidencia/faltantes:** 5.188 composites miden 2 m y 144 son parciales; la semilongitud máxima es 1 m. P4.3 propone comparar radios cercanos a 20 y 30 m, aún no aprobados. No hay evaluación de asignación, ni conteo de puntos que caen a ≤1 m de esos umbrales; tampoco existe validación geológica del margen.

**¿Qué harías con bloques cuyo soporte queda a una distancia de punto medio cercana al radio máximo?**

- **A.** Mantener la decisión estricta `distance <= radio`; registrar la distancia y comparar estabilidad en P5, reconociendo que el caso puede cambiar al variar el radio.
- **B.** Marcar para `REVIEW/UNKNOWN` los casos dentro de una banda limítrofe de hasta 1 m del radio, sin asignar solo por el punto medio; la banda es un control geométrico provisional, no tolerancia validada.
- **C.** Para candidatos a ≤1 m del radio, calcular distancia exacta centro–segmento FROM–TO como prueba secundaria; mantener la regla principal por punto medio y reportar cuándo el método secundario cambia la elegibilidad.

Elige A, B o C y justifica con evidencia del repositorio, una ventaja y una limitación. No definas aún radios aprobados ni ejecutes asignaciones; P2_GRID, P4_GEO_ASSIGN y B09 siguen bloqueados.

**Respuesta del estudiante — P4.7:**

Acepto la precisión de P4.6: lo que afirmé sobre los bloques atravesados por un sondaje solo vale para radios de 16 m o más, condición que cumplen los escenarios de prueba de 20 y 30 m.

A. Aplico estrictamente distance <= radio, guardo la distancia de cada fuente en la salida y reviso la estabilidad de la asignación al comparar radios en P5.

Evidencia del repositorio: la diferencia máxima entre la distancia al punto medio y la distancia al segmento es 1 m, porque ningún composite supera 2 m (5,188 de 2 m y 144 parciales en m01b_composites.csv). Los dos radios de prueba de P4.3 (≈ 20 y ≈ 30 m) difieren en 10 m, así que la comparación entre ellos ya captura una sensibilidad mucho mayor que el error geométrico de 1 m. Además, en P1.5 decidí guardar la distancia al soporte por bloque, por lo que los casos cercanos al umbral se pueden identificar después sin otra regla.

Ventaja: la regla es simple, determinista y fácil de probar (un caso justo en el umbral, uno a 0.5 m dentro y uno a 0.5 m fuera). No introduce una tolerancia arbitraria que no está validada, y la distancia guardada permite auditar cualquier caso límite.

Limitación: una fuente a menos de 1 m del umbral puede entrar o quedar fuera según se mida al punto medio o al segmento, y eso puede cambiar un bloque de ASSIGNED a UNKNOWN (o al revés). Si en P5 la proporción de casos límite resulta importante, habría que aplicar la prueba centro–segmento (opción C) en esos casos.

**Evaluación conversacional:** CORRECTA — H0. Se acepta la precisión para radios de 20/30 m, ambos mayores que 16 m. La desigualdad garantiza diferencia geométrica ≤1 m, no que una comparación de radios separados 10 m capture todos los cambios de clasificación; la respuesta conserva esta sensibilidad como limitación y plantea revisar estabilidad en P5. Guardar distancia por fuente y probar exactamente dentro/en el borde/fuera es reproducible. No se fijaron radios, no se ejecutaron asignaciones ni se implementó la prueba punto-segmento.

### P4.8 — precedencia del estado topográfico frente a la litología

**Microteoría:** el estado topográfico y la categoría litológica son atributos distintos. Si una celda se confirma como `AIR`, no debe recibir una litología de roca por proximidad; si está fuera de cobertura topográfica o su estado es desconocido, tampoco se puede asumir roca. Mantener precedencia explícita evita que una regla de vecindad geológica sobrescriba una condición física desconocida. La regla exacta depende de topografía oficial, que aún falta.

**Evidencia/faltantes:** el escenario exige `topo_status` con estados como `ROCK`, `AIR`, `PARTIAL`, `OUTSIDE_TOPO_COVERAGE` y `TOPO_UNKNOWN`, y señala que `AIR` no equivale a roca `UNKNOWN`. No hay Topopl.csv ni topografía oficial en el repositorio; P1.2 mantiene el código litológico AIR separado y B09 sigue `RECOVERY_BLOCKED`. Esta decisión no permite clasificar celdas hoy.

**¿Qué precedencia conceptual propones para una futura asignación litológica cuando se disponga de topografía?**

- **A.** Aplicar litología solo a bloques confirmados como `ROCK`; `AIR` queda sin dominio de roca y `OUTSIDE_TOPO_COVERAGE`/`TOPO_UNKNOWN` quedan sin asignación con causa, conservando separadas ambas columnas.
- **B.** Asignar litología por soporte a todos los bloques y almacenar `topo_status` como atributo independiente, incluso en `AIR`, dejando al consumidor combinar los campos.
- **C.** Asignar litología a `ROCK` y `PARTIAL`; conservar `AIR` sin litología, pero tratar fuera de cobertura/topografía desconocida como elegibles provisionalmente si hay soporte de sondaje.

Elige A, B o C y justifica con evidencia del escenario, una ventaja y una limitación. Es conceptual: no hay topografía verificada, no se asignan estados ni códigos, y `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

**Respuesta del estudiante — P4.8:**

A. Asigno litología solo a bloques con topo_status = ROCK confirmado; los bloques AIR, OUTSIDE_TOPO_COVERAGE y TOPO_UNKNOWN quedan sin dominio, con su causa registrada (assignment_status NOT_APPLICABLE para AIR y UNASSIGNED con causa topográfica para los otros dos).

Evidencia del escenario: en la etapa P4 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md se pide la "prioridad de AIR, OUTSIDE_TOPO_COVERAGE, TOPO_UNKNOWN sobre una asignación geológica automática", y la sección 7 advierte que un bloque AIR no es un bloque de roca UNKNOWN y que no deben confundirse en tabla ni visualización. En el repositorio no hay topografía (B09 RECOVERY_BLOCKED), y la cota superior provisional de 3530 m está por encima de varios collars (rango 3288–3524 m), por lo que parte del grid candidato podría ser aire.

Ventaja: se evita asignar litología a celdas que podrían estar sobre la superficie o fuera de la cobertura, y se separan claramente las causas: no es roca, no se sabe si es roca, o es roca sin soporte suficiente. Es coherente con P1.2 y P4.5, donde no inferí topo_status a partir del código AIR.

Limitación: mientras B09 siga bloqueado, todos los bloques serían TOPO_UNKNOWN, así que con esta regla no se asignaría litología a ningún bloque. Los bloques PARTIAL (cortados por la superficie) también quedarían sin dominio, aunque tengan una parte de roca con soporte; para incluirlos haría falta una regla de fracción de ocupación que no está definida. Por eso, la implementación de P4 depende de que el docente entregue la topografía o autorice explícitamente otro tratamiento.

**Evaluación conversacional:** CORRECTA — H0. La precedencia de estados topográficos sobre asignación automática es explícita en el escenario; distinguir `NOT_APPLICABLE` para `AIR` de `UNASSIGNED` por topografía desconocida/fuera de cobertura evita confundir ausencia de roca con falta de evidencia. La ausencia de topografía confirma que hoy no se pueden calcular ni confirmar esos estados; que el grid candidato contenga bloques `TOPO_UNKNOWN` es una consecuencia esperada, no una clasificación ejecutada. La limitación de `PARTIAL` está bien identificada y requiere una decisión de ocupación aparte. No se asignó litología ni se aprobó el gate `P4_GEO_ASSIGN`.

### P4.9 — tratamiento de bloques PARTIAL

**Microteoría:** un bloque `PARTIAL` intersecta la superficie y contiene fracciones de roca y aire. Un código litológico sin fracción de ocupación puede ocultar que el volumen nominal completo no es roca; excluirlo pierde soporte potencial, mientras que asignarlo exige una regla explícita sobre ocupación y sobre qué volumen representa el dominio. Esa regla no se puede validar sin topografía compatible y sin contrastarla con el propósito del modelo.

**Evidencia/faltantes:** el escenario enumera `PARTIAL` como estado topográfico y distingue el volumen nominal de la celda del volumen neto de roca, que necesita regla de ocupación. B09 sigue bloqueado porque no hay topografía oficial ni CRS/datum confirmados; no hay fracciones roca/aire calculadas para bloques candidatos. La decisión de P4.8 deja `PARTIAL` sin dominio hasta definir un tratamiento.

**¿Cómo tratarías conceptualmente bloques `PARTIAL` en una futura asignación geológica?**

- **A.** Dejarlos sin dominio (`UNASSIGNED` con causa `PARTIAL_TOPO`) hasta definir y validar una regla de ocupación; no perder su `topo_status`.
- **B.** Asignar litología con soporte como en `ROCK`, pero guardar el dominio como preliminar y no interpretarlo como volumen neto de roca; posponer el cálculo de fracción.
- **C.** Asignarlos solo si la fracción de roca supera un umbral aprobado, registrar la fracción y validar sensibilidad a ese umbral; no fijar el valor ahora.

Elige A, B o C y justifica con evidencia del escenario/repositorio, una ventaja y una limitación. No fijes un umbral ni ejecutes cálculos: topografía, compatibilidad espacial y `P4_GEO_ASSIGN` siguen pendientes.

**Respuesta del estudiante — P4.9:**

A. Dejo los bloques PARTIAL sin dominio (assignment_status UNASSIGNED, causa PARTIAL_TOPO) hasta definir y validar una regla de ocupación; como camino futuro, esa regla podría ser la de la opción C (fracción de roca registrada y umbral aprobado con análisis de sensibilidad).

Evidencia del escenario y del repositorio: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md indica que nominal_volume es volumen de la celda y no volumen neto de roca, y que para determinar este último se requiere una regla o fracción de ocupación aparte, que si no se implementó debe declararse. En el repositorio no hay topografía (B09 RECOVERY_BLOCKED) ni fracciones calculadas, así que no hay forma de saber qué parte de cada celda es roca. Es coherente con lo que registré en P4.8, donde señalé que PARTIAL quedaría sin dominio por esa misma falta de regla.

Ventaja: no se asigna litología a volumen que podría ser aire, no se confunde el volumen nominal de 4,000 m³ con volumen de roca, y la causa PARTIAL_TOPO distingue estos bloques de los UNKNOWN por falta de soporte geológico.

Limitación: justo bajo la superficie, donde los sondajes empiezan y suele haber soporte (por ejemplo, REG cerca de los collars), muchos bloques quedarían sin dominio, y el modelo tendría una "capa vacía" en el contacto con la topografía. Para recuperar esos bloques hace falta la topografía oficial, calcular la fracción de roca por celda y aprobar un umbral con evidencia.

**Evaluación conversacional:** CORRECTA — H0. La sección 7 distingue `nominal_volume` del volumen neto de roca y exige declarar una regla de ocupación si se calcula este último. Sin topografía ni fracciones disponibles, dejar `PARTIAL` como `UNASSIGNED` con causa `PARTIAL_TOPO` evita atribuir litología o volumen de roca sin evidencia. La propuesta futura de fracción con umbral y sensibilidad está planteada como trabajo posterior, no como umbral ya definido. La limitación de perder bloques con soporte cerca de la superficie es pertinente. No se calculó ocupación ni se implementó asignación.

### P4.10 — dependencias y orden de evaluación

**Microteoría:** una regla conceptual de asignación no se puede implementar de forma coherente si la geometría de la malla, la superficie topográfica y los parámetros de soporte no están aprobados. El orden importa: sin CRS/compatibilidad y extensión confiable, un resultado de aire/roca o distancia puede ser sistemáticamente incorrecto; sin pruebas y validación, una tabla generada no demuestra validez geológica.

**Evidencia/faltantes:** `P2_GRID` y `P4_GEO_ASSIGN` siguen sin aprobación; B09 está `RECOVERY_BLOCKED` por falta de topografía oficial y CRS/datum no documentados. Los escenarios de radio 20/30 m no están aprobados. `PARTIAL` no tiene regla de ocupación y los estados topográficos no se han calculado. Los composites B08 y la evidencia de sondajes existen, pero no habilitan por sí solos la malla ni la asignación.

**¿Qué orden de dependencias propones antes de cualquier implementación de P4?**

- **A.** Resolver B09 primero (obtener topografía, verificar CRS/unidades y compatibilidad); luego cerrar `P2_GRID`, aprobar reglas/parámetros y pruebas de P4, y finalmente pasar el gate de implementación.
- **B.** Aprobar primero la malla candidata y las reglas abstractas de P4; implementar la asignación topográfica después cuando llegue la superficie, con una revisión posterior de geometría.
- **C.** Implementar ya solo una asignación geológica sin `topo_status`, dejando todos los bloques como provisionales y agregando topografía en una etapa posterior.

Elige A, B o C y justifica con evidencia del estado actual, una ventaja y una limitación. No es autorización de implementación; `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

**Respuesta del estudiante — P4.10:**

A. Primero resuelvo B09: obtener la topografía oficial y verificar coordenadas, CRS/datum (si constan), unidades, elevaciones y cobertura frente a los collars. Luego cierro P2_GRID (ajustando la cota superior y nz con la superficie real), apruebo las reglas, parámetros (radios de prueba 20/30 m) y pruebas de P4, y finalmente paso su gate de implementación.

Evidencia del estado actual: B09 está en RECOVERY_BLOCKED porque no hay topografía en el repositorio (8 archivos del manifest, ninguno topográfico); la cota superior de 3530 m y nz = 48 son provisionales, basados en los collars (3288–3524 m). En P4.8 y P4.9 definí que solo los bloques ROCK reciben litología y que PARTIAL queda UNASSIGNED, así que sin topo_status no hay ningún bloque elegible. Los radios de 20 y 30 m son escenarios de prueba, no parámetros aprobados.

Ventaja: cada etapa se implementa sobre una base verificada. La malla no tendrá que rehacerse cuando llegue la superficie, y las distancias y estados de P4 no se calcularán sobre celdas que podrían ser aire. El orden respeta las dependencias reales: topografía → grid → reglas → asignación.

Limitación: mientras no llegue la topografía, ninguna etapa con código (P2_GRID, P3, P4, P6) puede avanzar, y el examen queda en plan conceptual. Por eso, he consultado al docente: si no puede entregar la topografía y autoriza explícitamente otro tratamiento (por ejemplo, generar la malla con todos los bloques en TOPO_UNKNOWN), presentaré esa autorización para revisar este orden.

**Evaluación conversacional:** CORRECTA — H0. El orden B09 → `P2_GRID` → reglas/parámetros/pruebas → gate P4 respeta las dependencias del escenario y evita calcular estados topográficos o soporte sobre geometría no verificada. La evidencia del repo mantiene cota 3530 m y `nz=48` como provisionales, y los radios 20/30 m como escenarios, no parámetros aprobados. La consulta al docente no equivale a una autorización recibida: solo una respuesta explícita permitiría reconsiderar el tratamiento. Matiz: la limitación se refiere a las etapas de implementación dependientes de topografía; no invalida continuar decisiones conceptuales ni significa que toda actividad con código sea imposible. No se avanzó a implementación y siguen bloqueados `P2_GRID`, P3, `P4_GEO_ASSIGN` y B09.

### P5.1 — separar validación computacional de validación minera

**Microteoría:** una prueba computacional puede demostrar invariantes de la tabla y reproducibilidad de reglas bajo entradas controladas; no demuestra que la escala de bloques, la superficie, los contactos, la continuidad ni la extrapolación sean geológicamente razonables. La validación minera requiere interpretar soporte, geometría y comportamiento espacial y declarar incertidumbres. Un resultado de pruebas verde no reemplaza esa interpretación.

**Evidencia/faltantes:** la sección P5 del escenario separa expresamente comprobaciones computacionales de validación minera y requiere que el estudiante interprete qué demuestra y qué no demuestra cada test. La sección recomienda diagnosticar cobertura, estados topográficos, asignaciones/UNKNOWN, distancias y casos cerca de contactos. En el repo no hay malla ni asignación; B09 sigue bloqueado y las decisiones de P2/P4 son conceptuales, por lo que no existen resultados P5 que evaluar.

**Si más adelante se implementa el modelo con inputs aprobados, ¿cómo distinguirías las dos clases de evidencia y qué condición pondrías para aceptar el resultado?**

- **A.** Exigir invariantes computacionales y reproducibilidad como pruebas técnicas, además de una revisión minera independiente de cobertura, contactos, extrapolación, UNKNOWN y topografía; no declarar aceptación por suite verde solamente.
- **B.** Usar una suite automatizada completa de geometría y reglas como criterio suficiente de aceptación; documentar las limitaciones mineras en el informe, sin gate separado.
- **C.** Priorizar secciones y revisión visual minera; permitir errores estructurales menores si la distribución parece geológicamente razonable, dejando la corrección para después.

Elige A, B o C y justifica con la sección P5 del escenario, una ventaja y una limitación. Esto sigue siendo conceptual: no hay resultados P5, no se ejecuta validación y no se autoriza código.

**Respuesta del estudiante — P5.1:**

A. Exijo dos evidencias separadas, cada una con su propia condición de aceptación.

Computacional: invariantes y reproducibilidad, por ejemplo 38,976 block_id únicos de 0 a 38,975; índices i, j, k coherentes con block_id = i + j·nx + k·nx·ny; centros según origen + (índice + 0.5)·tamaño; volumen nominal de 4,000 m³ en todas las celdas; las 270 estaciones dentro del envolvente; reglas de asignación probadas con casos controlados (concordancia, conflicto, sin soporte, umbral del radio, AIR excluido, TOPO_UNKNOWN sin dominio), y reejecución con los mismos inputs y parámetros que da el mismo resultado (mismo hash).

Minera: una revisión independiente de cobertura y bloques sin soporte, contactos y extrapolación, proporción y ubicación de UNKNOWN por causa, comparación de radios de 20/30 m, y relación aire/roca frente a la topografía.

Condición: acepto el resultado como READY_FOR_REVIEW solo si todas las invariantes computacionales pasan (o una falla se corrige o se aprueba explícitamente un alcance parcial), y la revisión minera queda registrada con hallazgos ERROR/WARNING/INFO y sus limitaciones. Aun así no declaro MINING_VALIDATED.

Evidencia del escenario: la etapa P5 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md obliga a distinguir comprobación computacional (estructura, IDs, centros, volúmenes, reglas reproducibles, reejecución) de validación minera (soporte real, tamaño de bloque, aire/roca real, contactos, extrapolación, incertidumbres). Indica que si falla una invariante importante no se declara READY_FOR_REVIEW, y que el gate P5_VALIDATION no equivale a validación geológica aunque la suite esté verde. Lo mismo pasó en B08: 47 pruebas PASS mostraron consistencia computacional, pero no validación geológica.

Ventaja: cada tipo de evidencia responde a una pregunta distinta (¿el código hace lo que dice la regla? / ¿la regla tiene sentido para estos datos?), y ninguna puede ocultar las fallas de la otra.

Limitación: la validación minera depende de criterio y no tiene un PASS automático. Sin topografía (B09) ni una interpretación geológica de referencia, solo se podrá documentar la coherencia y las incertidumbres, no confirmar que la asignación es geológicamente correcta. Además, todavía no hay malla ni asignación para validar.

**Evaluación conversacional:** CORRECTA — H0. La separación y las dos condiciones de aceptación coinciden con P5; la regla impide que una suite verde sustituya la revisión minera y mantiene `MINING_VALIDATED` como un estado distinto. El ejemplo de 38.976 bloques, IDs 0–38.975 y volumen nominal de 4.000 m³ pertenece a la malla candidata actual, no a una geometría aprobada: la topografía puede cambiar límites y `nz`. Las 270 estaciones dentro del envolvente candidato fueron verificadas anteriormente, pero esa prueba no establece aire/roca. El hash solo es un criterio reproducible si se fijan también serialización y metadatos deterministas. B08 ilustra la distinción: 47 pruebas computacionales PASS no validaron geología. No hay malla ni resultados P5 actuales.

### P5.2 — priorización de diagnósticos y hallazgos

**Microteoría:** los diagnósticos resumen fallas estructurales, cobertura y comportamiento espacial, pero no todos tienen el mismo significado. Un `ERROR` debe impedir aceptación cuando viola una invariante importante; un `WARNING` requiere revisión o limita el alcance; `INFO` registra contexto sin implicar fallo. Los umbrales no se deben inventar: deben derivarse de requisitos aprobados y su interpretación minera.

**Evidencia/faltantes:** el escenario sugiere reportar celdas totales, estados topográficos, clasificadas/`UNKNOWN`, códigos, distancias, áreas sin cobertura, secciones, profundidad y casos próximos a contactos; pide clasificar `ERROR/WARNING/INFO` con criterios documentados e interpretar qué demuestra y qué no cada test. No existe todavía tabla de bloques ni diagnósticos P5. Los umbrales de aceptación y los radios siguen sin aprobarse, y B09 está bloqueado.

**¿Cómo priorizarías los diagnósticos para decidir si el resultado puede pasar a `READY_FOR_REVIEW`?**

- **A.** Definir antes criterios verificables vinculados a requisitos aprobados; tratar invariantes fallidas como `ERROR`, limitaciones o soporte bajo como `WARNING`, y contexto descriptivo como `INFO`; presentar conteos y distribuciones para revisión, sin inventar umbrales mineros.
- **B.** Usar porcentajes fijos de cobertura/UNKNOWN elegidos antes de ver resultados y rechazar cualquier salida que no los alcance, aunque no exista fundamento geológico aprobado.
- **C.** Clasificar los hallazgos después de observar el resultado según si la visualización parece razonable, para no bloquear avances por casos inesperados.

Elige A, B o C y justifica con los diagnósticos y reglas P5 del escenario, una ventaja y una limitación. No propongas todavía umbrales numéricos ni ejecutes diagnósticos; no hay malla ni asignación.

**Respuesta del estudiante — P5.2:**

A. Defino los criterios antes de ver los resultados, ligados a requisitos ya aprobados: ERROR = una invariante computacional fallida (IDs duplicados, índices o centros incorrectos, volumen no positivo, estación fuera del envolvente, regla que no reproduce su caso controlado, reejecución distinta); WARNING = limitación o soporte bajo que restringe el alcance sin ser error (bloques UNKNOWN por INSUFFICIENT_SUPPORT o CONFLICTING_CODES, n_holes = 1, casos a menos de 1 m del radio, PARTIAL_TOPO, AIR en revisión); INFO = contexto descriptivo (conteos por estado topográfico y por código, distribución por profundidad, distancias). No fijo umbrales mineros de cobertura ni de UNKNOWN.

Evidencia del escenario y del repositorio: la etapa P5 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md pide clasificar hallazgos ERROR/WARNING/INFO con criterios documentados, sugiere diagnósticos sin prescribir números (celdas totales, estados topográficos, clasificadas/UNKNOWN, recuentos por código, distancias, áreas sin cobertura, secciones, profundidad y casos cerca de contactos) e indica que si falla una invariante importante no se declara READY_FOR_REVIEW. En M01 ya usamos esa misma convención: el validator de T1 clasificó 0 ERROR, 15 WARNING y 11,047 INFO (outputs/tables/m01_validation_summary.csv).

Ventaja: la clasificación no depende de cómo se vea el resultado, sino de reglas fijadas antes, lo que evita ajustar el criterio para que el modelo "pase". Solo un ERROR bloquea READY_FOR_REVIEW, mientras que los WARNING quedan como límites explícitos del alcance.

Limitación: sin umbrales mineros validados, un modelo con muchos UNKNOWN podría quedar sin ningún ERROR y técnicamente aprobado en lo computacional, aunque sea poco útil. Decidir si esa cobertura es aceptable sigue siendo un juicio minero que debe declararse en la revisión, no un PASS automático.

**Verificación y evaluación conversacional:** CORRECTA — H0. Se releyó y sumó `finding_count` de `outputs/tables/m01_validation_summary.csv`: 91 reglas (77 ERROR, 10 WARNING, 4 INFO), que agregan 0 ERROR, 15 WARNING y 11.047 INFO. La cifra del estudiante coincide con el artefacto. Los criterios son previos y auditables; soporte bajo y `UNKNOWN` son hallazgos para revisión minera, no prueba de fallo computacional. No se han ejecutado diagnósticos P5 ni hay malla/asignación; `READY_FOR_REVIEW` y `MINING_VALIDATED` no se declaran.

### P5.3 — interpretación de cobertura UNKNOWN

**Microteoría:** una proporción alta de `UNKNOWN` puede reflejar una regla conservadora, espaciamiento de datos, conflictos en contactos o estados topográficos sin resolver; por sí sola no demuestra un bug ni un buen modelo. Para juzgar utilidad hay que examinar causa y distribución espacial, y contrastarlas con sondajes, contactos, topografía y objetivo del modelo. Un conteo global puede ocultar zonas vacías o concentraciones de incertidumbre.

**Evidencia/faltantes:** P4 propone `UNKNOWN` con causas como `INSUFFICIENT_SUPPORT` y `CONFLICTING_CODES`, además de prioridad topográfica; `PARTIAL` también queda sin dominio bajo la decisión actual. P5 del escenario recomienda proporciones/ubicación de `UNKNOWN`, distancias, secciones y contactos, y exige interpretación minera independiente. No existe malla ni asignación; por tanto, no hay porcentaje real que interpretar ni umbral de cobertura aprobado.

**Si la futura salida tuviera una proporción alta de bloques `UNKNOWN`, ¿cómo decidirías si refleja cautela apropiada o una limitación que exige revisar el método?**

- **A.** Desglosar por causa y ubicación, cruzarlo con soporte, distancias, contactos y topografía, revisar secciones y radios alternativos; documentar qué revela y qué no el diagnóstico, sin declarar aceptabilidad por un porcentaje global.
- **B.** Considerarlo aceptable mientras todas las invariantes computacionales pasen, ya que `UNKNOWN` evita extrapolar.
- **C.** Reducir el radio o cambiar a vecino más cercano hasta bajar `UNKNOWN`, y decidir luego si la mayor cobertura parece razonable.

Elige A, B o C y justifica con criterios P4/P5, una ventaja y una limitación. No propongas umbrales numéricos ni ejecutes análisis; no hay salida de bloques.

**Respuesta del estudiante — P5.3, primera parte:**

A. Desgloso los UNKNOWN por causa (INSUFFICIENT_SUPPORT, CONFLICTING_CODES, causas topográficas como TOPO_UNKNOWN/PARTIAL_TOPO, y AIR en revisión) y por ubicación (secciones por coordenada, profundidad y periferia de la malla), y los contrasto con soporte (n_sample_ids, n_holes), distancia al soporte, cercanía a contactos, estado topográfico y comparación de radios de 20/30 m. Documento qué indica cada diagnóstico y no acepto ni rechazo el modelo por un porcentaje global.

Criterios P4/P5: en P1.4 y P4.1 definí que UNKNOWN debe llevar una causa identificada, y en P1.5, P4.2 y P4.4 que cada bloque guarde distancia, fuentes y número de sondajes, justamente para poder hacer este desglose. La etapa P5 del escenario sugiere revisar clasificadas/UNKNOWN, distancias, áreas sin cobertura, secciones, distribución por profundidad y casos cerca de contactos.

Criterio de interpretación: un UNKNOWN concentrado en la periferia o entre sondajes a 60–92 m, por INSUFFICIENT_SUPPORT, indica cautela apropiada por falta de datos. Concentrado en contactos frecuentes (REG→DIO) por CONFLICTING_CODES, refleja incertidumbre real del contacto. Pero si aparece UNKNOWN en bloques atravesados por un sondaje con un único código, o si el cambio de 20 a 30 m altera mucho la clasificación, eso exige revisar el método. Reducir el radio no disminuye

**Respuesta del estudiante — P5.3, complemento:**

Completo P5.3 (respuesta A):

Frase completa: reducir el radio no disminuye los UNKNOWN; al contrario, aumenta los de causa INSUFFICIENT_SUPPORT, porque menos composites quedan dentro del radio. Cambiar a vecino más cercano sí los reduce, pero porque deja de exigir concordancia y puede cruzar contactos no validados (P1.3, P4.1), no porque mejore el soporte.

AIR separado de UNKNOWN: el composite AIR (CR-C02-002_0001) no es un UNKNOWN de roca. Según P4.5 queda excluido del soporte con REVIEW/UNKNOWN como marca del código, y un bloque con topo_status = AIR queda assignment_status NOT_APPLICABLE (P4.8). En el desglose lo reporto en una categoría aparte, fuera del porcentaje de UNKNOWN de roca.

Precisión aceptada: un UNKNOWN en un bloque atravesado por un sondaje no demuestra por sí solo un fallo. Solo indicaría revisar el método si el bloque es ROCK elegible, tiene soporte dentro del radio con un único código y no existe otra causa registrada (topográfica, conflicto o AIR).

Ventaja: el desglose distingue falta de datos, conflicto real de códigos, condición topográfica y posible falla de la regla, y muestra dónde actuar (más perforación, interpretación de contactos o ajuste justificado) sin forzar la cobertura.

Limitación: requiere criterio y no da un PASS automático. Mientras B09 siga bloqueado, la causa topográfica dominará todos los bloques y ocultará las demás, y sin una interpretación geológica de referencia no puedo confirmar si un conflicto refleja la geología real o solo la regla.

**Evaluación provisional:** PARCIAL — H1. Se completan ventaja, limitación, separación de `AIR` y la condición para investigar un bloque atravesado por sondaje. La distinción `AIR` como categoría aparte es consistente con P4.5/P4.8. Matiz técnico: al reducir el radio, los casos `INSUFFICIENT_SUPPORT` pueden aumentar, pero también pueden desaparecer conflictos de códigos; por ello el total de `UNKNOWN` no necesariamente aumenta en todos los datos. La alternativa de vecino más cercano puede bajar `UNKNOWN`, pero sacrifica el requisito de concordancia y puede cruzar contactos. Además, la frase “la causa topográfica dominará todos los bloques” depende del tratamiento alternativo que autorice el docente; con B09 ausente y la política actual de no generar bloques, no existe una clasificación ejecutada que permita afirmar la distribución futura. Se requiere reformular la primera afirmación y mantener ese punto como expectativa condicionada, no resultado. No hay malla/asignación ni análisis ejecutado.

**Pendiente:** precisar que reducir el radio tiende a aumentar `UNKNOWN` por soporte insuficiente, pero su efecto neto depende también de los conflictos que desaparezcan; y reformular la afirmación de que la causa topográfica dominará todos los bloques como una consecuencia condicionada a una política futura. No se avanza a otra pregunta hasta cerrar P5.3.

**Respuesta del estudiante — P5.3, ajuste final:**

A. Ajusto los dos puntos:

1. Un radio menor tiende a aumentar los UNKNOWN por INSUFFICIENT_SUPPORT, porque quedan menos fuentes dentro del radio, pero también puede eliminar algunos CONFLICTING_CODES, porque un radio menor incluye menos códigos distintos (por ejemplo, deja fuera el otro lado de un contacto). El efecto neto sobre el total de UNKNOWN depende del resultado y solo se podrá medir comparando los radios de 20 y 30 m en P5 por causa, no por total.

2. Que la causa topográfica domine es una posibilidad condicionada: solo ocurriría si se generara la malla con todos los bloques en TOPO_UNKNOWN, bajo un tratamiento autorizado por el docente. No es una distribución verificada, porque hoy no existe malla ni asignación.

Justificación: mantengo la tendencia esperada porque guía qué diagnósticos preparar (desglose por causa y por radio), pero sin presentarla como conclusión, coherente con P5.2: los criterios se fijan antes y los efectos se confirman con resultados reales.

**Evaluación conversacional:** CORRECTA — H0. El ajuste distingue la tendencia esperada de `INSUFFICIENT_SUPPORT` del efecto neto, que también depende de conflictos que desaparezcan, y especifica comparar radios por causa. La causa topográfica dominante queda como posibilidad condicionada a una malla completamente `TOPO_UNKNOWN` bajo autorización docente; no se presenta como resultado observado. `AIR` se conserva en una categoría distinta de `UNKNOWN` de roca, y la limitación/ventaja ya están registradas. Los radios siguen siendo escenarios, no aprobados; no hay malla ni asignación ni análisis ejecutado.

### P6.1 — objetivo y capas del visualizador 3D

**Microteoría:** el visualizador de P6 debe servir para auditar geometría, cobertura e incertidumbre, no solo para producir una imagen atractiva. La topografía solo puede mostrarse como superficie real donde exista cobertura justificada; sondajes/contactos aportan referencia; clases geológicas preliminares deben distinguirse de `UNKNOWN`/`UNASSIGNED`, `AIR` y celdas `PARTIAL`. Leyendas, filtros, cortes y escala ayudan a evitar ocultamiento y lecturas equivocadas. No se debe colorear por Cu como si fuese una ley estimada.

**Evidencia/faltantes:** P6 del escenario recomienda topografía donde haya cobertura, trayectorias/contactos o composites, bloques clasificados, desconocidos distinguibles, límites de malla, ejes, escala, unidades, leyenda y filtros/cortes. `outputs/figures/m01_exploration_3d.html` es una visualización exploratoria, no de bloques clasificados; no hay topografía, malla ni asignación. El escenario exige valorar herramienta existente/dependencia, pruebas y revisión, con gate `P6_VISUALIZER`. B09 y gates P2/P4/P5 siguen pendientes.

**¿Cuál debería ser el objetivo y conjunto inicial de capas de un futuro visualizador P6, dadas estas limitaciones?**

- **A.** Diseñarlo como herramienta de auditoría: trayectorias y contactos/composites de control, malla solo cuando esté aprobada, códigos litológicos por categoría sin ley Cu, estados `UNKNOWN/UNASSIGNED` separados y topografía únicamente tras verificar cobertura; incluir límites, ejes/unidades, leyenda y cortes/filtros.
- **B.** Priorizar una vista de bloques coloreados por litología y mostrar sondajes; añadir superficie y estados desconocidos si llegan datos, dejando controles secundarios para después.
- **C.** Mantener por ahora la visualización exploratoria de sondajes y dejar explícito que P6 no puede mostrar bloques/topografía hasta que los inputs y gates estén resueltos.

Elige A, B o C y justifica con evidencia/capacidades reales del repo, una ventaja y una limitación. No se implementa ni se decide librería en esta pregunta; P6 sigue conceptual bajo `RECOVERY_BLOCKED`.

**Respuesta del estudiante — P6.1:**

A. Diseño el visualizador como herramienta de auditoría: trayectorias y composites/contactos de control; la malla solo cuando P2_GRID esté aprobado; bloques coloreados por lith_code (REG, DIO, POR, BRX), sin colorear por Cu porque en T2 no se estima ley; estados UNKNOWN/UNASSIGNED (por causa) y NOT_APPLICABLE/AIR con colores o capas separadas y distinguibles de la roca asignada; topografía solo después de verificar su cobertura en P3; e incluyendo límites de la malla, ejes con unidades (m), leyenda y cortes/filtros por coordenada, estado y código.

Evidencia y capacidades del repositorio: src/m01/visualizer.py ya genera con Plotly outputs/figures/m01_exploration_3d.html con collars, trayectorias e intervalos en XYZ, y en la T1 la figura declara que no hay topografía en el release. m01b_composites.csv tiene from/mid/to XYZ y lith_code para las 5,332 filas, así que los composites y contactos de control pueden añadirse sin otro cálculo. La malla candidata tendría 38,976 celdas, demasiadas para verlas todas a la vez sin ocultar el interior, por lo que los cortes y filtros son necesarios, no opcionales.

Ventaja: permite auditar visualmente lo que se decidió en P1–P5: si los bloques asignados están cerca de su soporte, dónde se concentran los UNKNOWN por causa, cómo se comportan cerca de los contactos y, cuando exista, la relación con la superficie. Reutiliza la herramienta y el estilo ya probados en M01.

Limitación: hoy solo se pueden mostrar sondajes y composites, porque no hay topografía, malla ni asignación. Con 38,976 celdas, el HTML puede ser pesado (el de M01 ya ocupa ≈ 5.7 MB) y los colores de los bloques pueden dar una falsa impresión de continuidad geológica, aunque se distingan los UNKNOWN. La visualización ayuda a revisar, pero no reemplaza la validación P5.

**Evaluación conversacional:** CORRECTA — H0. La orientación de auditoría y separación de litologías, estados sin asignar y topografía es coherente con P6; no colorear por Cu evita sugerir estimación de ley. Se verificó que `src/m01/visualizer.py` produce HTML interactivo Plotly, con collars, trayectorias, intervalos litológicos y toggle entre litología y ensayes coloreados por Cu; el archivo existente mide 5.720.873 bytes (≈5,7 MB decimal). El CSV de composites tiene 5.332 filas y campos XYZ FROM/MID/TO con `lith_code`. Es correcto que estos son insumos presentes, no una visualización T2 ya implementada; tampoco se ha verificado aún que filtros por coordenada/estado/código existan. La candidata de 38.976 celdas no está aprobada y no se ha medido el peso que tendría una visualización de bloques. El aviso sobre riesgo de continuidad visual y no sustituir P5 es pertinente. No se ha elegido librería nueva ni se implementó P6.

### P6.2 — filtros, cortes y volumen renderizado

**Microteoría:** una escena 3D con miles de celdas puede ocultar su interior, saturar el navegador y sugerir continuidad donde solo hay categorías asignadas por proximidad. Un render auditable necesita un mecanismo reproducible para inspeccionar el interior y controlar qué se muestra; ocultar u omitir bloques debe poder distinguirse de `UNKNOWN` o de bloques ausentes. Reducir visualmente la carga no debe modificar ni reemplazar la tabla de modelo.

**Evidencia/faltantes:** la candidata conceptual contiene 38.976 celdas, no generadas. El HTML M01 actual pesa 5.720.873 bytes; el código agrupa intervalos por litología y ofrece un dropdown entre litología y assay, pero no se ha verificado soporte de filtros por coordenada, estado o código ni render de bloques. P6 requiere filtros/cortes para evitar ocultamiento y pide justificar el criterio para no saturar memoria. No existe perfil de rendimiento de una escena de bloques ni gate `P6_VISUALIZER` aprobado.

**¿Qué estrategia conceptual usarías para que el visualizador permita inspeccionar interior y categorías sin ocultar incertidumbre ni cargar innecesariamente la escena?**

- **A.** Mantener el dataset completo como fuente, con filtros explícitos por `lith_code`/estado y cortes reproducibles por coordenada; renderizar solo la selección visible, indicar conteos filtrados y nunca tratar lo oculto como ausente o `UNKNOWN`.
- **B.** Crear para la vista general una muestra espacialmente reducida y determinista de bloques, conservar la tabla completa aparte y permitir seleccionar zonas/cortes sin muestreo; informar claramente que la vista general está diezmada.
- **C.** Mostrar todos los bloques en una escena completa con transparencia y confiar en la rotación/zoom, sin filtros para no excluir información.

Elige A, B o C y justifica con la candidata de 38.976 celdas y las capacidades actuales del visualizador, una ventaja y una limitación. No decidas aún librería ni implementación, no transformes el dataset y no declares `P6_VISUALIZER` aprobado.

**Respuesta del estudiante — P6.2:**

A. Conservo la tabla completa de bloques como fuente y en el visualizador filtro por lith_code y por estado (ASSIGNED, UNKNOWN por causa, UNASSIGNED, NOT_APPLICABLE), además de cortes por coordenada (nivel k, sección i o j). Solo renderizo la selección e indico en pantalla cuántos bloques se muestran y cuántos quedan ocultos por el filtro.

Justificación con la malla candidata y las capacidades actuales: con 28 × 29 × 48 = 38,976 celdas, un corte en planta tiene 28 × 29 = 812 bloques, una sección por X 29 × 48 = 1,392 y una sección por Y 28 × 48 = 1,344, es decir, entre el 2 % y el 3.6 % de la malla. Es una carga pequeña comparada con lo que ya muestra visualizer.py, que con Plotly renderiza collars, trayectorias e intervalos litológicos y alterna capas con un menú (HTML actual de 5,720,873 bytes). Los filtros por bloque todavía no existen y habría que implementarlos y probarlos.

Ventaja: la inspección es exacta y reproducible. Cada bloque mostrado es el bloque real de la tabla, sin muestreo ni reducción, y el conteo de ocultos deja claro que no se está omitiendo información del modelo, solo de la vista. Las secciones por i/j/k coinciden con los índices de P2.6, así que un bloque de la tabla se puede ubicar directamente en la vista.

Limitación: si se selecciona un filtro grande (por ejemplo, todos los bloques de POR o todos los UNKNOWN), el render puede volver a ser pesado y tapar el interior. Además, ver por cortes exige recorrer varias secciones para entender la continuidad 3D. El rendimiento real no se ha medido porque la malla no está generada.

**Evaluación conversacional:** CORRECTA — H0. Los conteos de secciones son aritméticamente consistentes con la malla candidata: nivel `k` = 28×29 = 812 (2,08 %); plano `i` = 29×48 = 1.392 (3,57 %); plano `j` = 28×48 = 1.344 (3,45 %). El enfoque conserva la tabla completa y hace explícita la selección visual, evitando muestreo silencioso; la limitación de filtros grandes y revisión de continuidad 3D es pertinente. El tamaño del HTML existente no demuestra rendimiento del render de bloques. La selección es conceptual; no hay malla ni filtros implementados, perfil de rendimiento ni gate `P6_VISUALIZER` aprobado.

**Cierre conceptual P6:** P6.1 y P6.2 completan la propuesta de auditoría, capas, filtros y cortes. Se reutilizará como candidata la herramienta Plotly de M01, sin dependencia nueva por ahora; el P6 gate exige implementar/pruebas/revisión más adelante. No se afirma que el visualizador de bloques exista.

## Estado de planificación

**P0–P6: síntesis del plan conceptual**

- **P0 — orden y recuperación:** secuencia defendida: resolver B09/topografía y compatibilidad espacial, después cerrar la malla, aprobar reglas/pruebas de asignación, validar y visualizar. `RECOVERY_BLOCKED` se conserva; `BASE_VERIFIED` no se declara. No es autorización de código.
- **P1 — dominios:** preservar códigos observados y contactos como evidencia, sin inventar sólidos; AIR no se infiere como estado físico; UNKNOWN lleva causa y procedencia/distancia/soporte trazables. Las decisiones conversacionales quedaron CORRECTA — H0.
- **P2 — grid:** candidata conceptual 20×20×10 m, origen `(242420, 8196180, 3050)`, 28×29×48 = 38.976 celdas; ejes sin rotación, Z positivo, índices base cero e ID determinista. La extensión superior depende de topografía, CRS/datum son desconocidos; `P2_GRID` no aprobado.
- **P3 — topografía:** no existe fuente oficial en repo; B09 sigue `RECOVERY_BLOCKED`. No hay estados aire/roca/parcial, cobertura ni fracciones de roca verificadas. Sin P3 no se puede validar ni cerrar la geometría topográfica.
- **P4 — asignación:** concordancia de códigos, UNKNOWN ante conflicto/soporte insuficiente, soporte único por `sample_id`, reporte de `n_holes`, distancia centro–midpoint con `distance <= radio`; 20/30 m solo escenarios. AIR excluido del soporte y `NOT_APPLICABLE` en bloques AIR; PARTIAL `UNASSIGNED/PARTIAL_TOPO`; fuera de cobertura y topografía desconocida sin dominio. `P4_GEO_ASSIGN` no aprobado.
- **P5 — validación:** distinguir pruebas computacionales/reproducibilidad de revisión minera independiente; criterios previos ERROR/WARNING/INFO y análisis UNKNOWN por causa/ubicación. No existe malla/asignación ni resultado P5; `P5_VALIDATION` pendiente y no se declara `MINING_VALIDATED`.
- **P6 — visualizador:** herramienta de auditoría, códigos por litología (no por Cu), estados UNKNOWN/UNASSIGNED y AIR diferenciados, topografía solo verificada, cortes/filtros reproducibles por coordenada/estado/código con conteos visibles/ocultos. Usar la tabla completa como fuente y renderizar solo la selección. Se identificó Plotly existente como vía a reutilizar, sujeto a gate; filtros de bloques y rendimiento no probados. `P6_VISUALIZER` no aprobado.

**Estado de gates:** El plan cumple conceptualmente el criterio `PLAN_APPROVED` del escenario (plan defendido con decisiones, orden, dependencias y bloqueos explícitos), por lo que se registra **`PLAN_APPROVED` — conceptual, bajo `RECOVERY_BLOCKED`**. Esto no equivale a `BASE_VERIFIED`, no autoriza implementación y no levanta los gates `P2_GRID`, P3, `P4_GEO_ASSIGN`, `P5_VALIDATION` o `P6_VISUALIZER`. Sin resolución/autorización de B09, el alcance ejecutable sigue bloqueado. No se generaron datos ni resultados en P2–P6.
