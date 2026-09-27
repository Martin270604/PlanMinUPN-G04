# IMP-001 — M01 Validate & Desurvey

## 1. Identificación

- **Implementation ID:** IMP-001
- **Module:** M01 — Validate & Desurvey
- **Date:** 2026-09-27
- **Group:** G04
- **Participants:** JorgeSanchez (pendiente de reemplazar por los nombres del equipo)
- **Status:** IN_PROGRESS

---

## 2. Problema minero

Preparar las tablas de sondajes del release para su validación y posterior
desurvey. Esta etapa implementa únicamente la lectura de datos y la validación
de contratos documentados; todavía no calcula trayectorias.

## 3. Objetivo

Cargar collar, survey, assay, lithology y density en memoria sin modificar los
archivos fuente y reportar incumplimientos del diccionario de datos, del
manifest y de las relaciones por `hole_id`.

## 4. Inputs

| Variable | Significado | Unidad | Origen | Obligatorio | Validación |
|---|---|---|---|---|---|
| Collar | Ubicación, orientación inicial e identificación del pozo | Según `data_dictionary.csv`; identificadores: UNKNOWN | `data/raw/collar.csv` | Sí | Esquema, tipos, nulos, conteo del manifest e identificador de pozo |
| Survey | Orientaciones medidas a profundidad | m y degree según diccionario | `data/raw/survey.csv` | Sí | Esquema, tipos, nulos, conteo del manifest y referencia a collar |
| Assay | Intervalos geoquímicos observados | m, percent y g/t según diccionario | `data/raw/assay.csv` | Sí | Esquema, tipos, nulos, conteo del manifest, identificador de muestra y referencia a collar |
| Lithology | Intervalos litológicos observados | m según diccionario | `data/raw/lithology.csv` | Sí | Esquema, tipos, nulos, conteo del manifest y referencia a collar |
| Density | Muestras de densidad observadas | m y t/m3 según diccionario | `data/raw/density.csv` | Sí | Esquema, tipos, nulos, conteo del manifest, identificador de muestra y referencia a collar |
| Alteration | Intervalos de alteración cuando estén disponibles | m según diccionario | `data/raw/alteration.csv` | Sí | Esquema y conteo del manifest; 0 registros se reportan como no disponibles |
| Diccionario | Definiciones de campos, unidades y tipos | No aplica | `data/raw/data_dictionary.csv` | Sí | Columnas requeridas y definiciones aplicables a cada tabla |
| Manifest | Identidad del release, archivos y conteos publicados | No aplica | `data/raw/release_manifest.json` | Sí | Archivos, conteos e identidad del dataset/proyecto |

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| `M01Inputs.tables` | Encabezados y filas CSV cargadas como texto, por archivo | Según campos originales | Memoria |
| `M01Inputs.data_dictionary` | Diccionario leído | No aplica | Memoria |
| `M01Inputs.manifest` | Manifest leído como objeto JSON | No aplica | Memoria |
| `ValidationReport.findings` | Hallazgos con regla, severidad, tabla, fila, sondaje, campo, valor y condición esperada | No aplica | Memoria |
| Findings M01 | Hallazgos individuales de validación | No aplica | `outputs/tables/m01_validation_findings.csv` |
| Resumen | Conteos por regla, severidad y tabla; incluye reglas sin findings | No aplica | `outputs/tables/m01_validation_summary.csv` |

## 6. Supuestos

Los valores CSV se conservan como texto al cargar y el validador interpreta los
tipos declarados por el diccionario.

| ID | Supuesto | Justificación | Impacto |
|---|---|---|---|
| SUP-01 | Tolerancia de redondeo numérico de `1e-9 m` para comparar longitudes, límites de profundidad y continuidad de intervalos. | Las profundidades y longitudes del release se publican con nueve decimales; se evita sensibilidad a redondeo de representación binaria. | Diferencias absolutas menores o iguales a `1e-9 m` se tratan como igualdad en esas comparaciones. No es tolerancia geológica ni operacional. |
| SUP-02 | La cobertura de densidad es la unión de intervalos válidos recortada a `[0, final_depth_m]`; no tiene umbral de aceptación. | El plan define cobertura informativa y no especifica umbral. | El porcentaje es descriptivo; no implica representatividad. |
| SUP-03 | La equivalencia entre `CAMPAIGN_0X` y `C0X` no se confirma automáticamente. | Las tablas y el manifest usan formatos distintos; el equipo indicó que la equivalencia está pendiente. | Se emite WARNING cuando el identificador de tabla no coincide literalmente con el manifest. |

## 7. Lógica minera

Esta etapa valida el contrato documentado y las reglas aprobadas del plan de
validación de ETAPA 3. Cada finding tiene `rule_id`, severidad (`ERROR`,
`WARNING` o `INFO`), tabla, fila, sondaje, campo, valor observado y condición
esperada.

Reglas M01 implementadas:

- **Collar:** `hole_id` único, `final_depth_m > 0` y coordenadas `x/y/z`
  numéricas y finitas; todos `ERROR`.
- **Survey:** referencia a collar, profundidad no negativa, secuencia estricta
  sin duplicados, estación en cero y profundidad dentro del collar; orientación
  numérica y finita; todos `ERROR`.
- **Intervalos:** orden `from_m < to_m`, largo, límites y gaps/overlaps para
  assay, lithology y density. Overlaps son `ERROR` en assay/lithology y
  `WARNING` en density; gaps son `WARNING` en assay/lithology e `INFO` en
  density; las otras reglas son `ERROR`.
- **Assay:** leyes numéricas y no negativas (`ERROR`); ceros (`INFO`) sin
  interpretación como bajo límite de detección.
- **Density:** dato numérico finito y positivo (`ERROR`); cobertura por pozo
  (`INFO`, sin umbral).
- **Alteration:** tabla vacía (`INFO`), no equivale a ausencia geológica.
- **Campañas:** diferencia de nomenclatura frente al manifest (`WARNING`),
  pendiente de confirmación.

Brechas se evalúan también contra los extremos `[0, final_depth_m]`; overlaps y
gaps se detectan por profundidad, independiente del orden de las filas.

No se calculan ni modifican trayectorias. No se realizan interpretación
geológica ni validaciones propias de desurvey.

## 8. Diseño computacional

### Módulos / archivos

- `src/m01/loader.py`: lectura de collar, survey, assay, lithology, density,
  alteration, diccionario y manifest; fuentes abiertas en modo lectura.
- `src/m01/validator.py`: validación contractual y reglas aprobadas de M01.
- `src/m01/validation_report.py`: escritura de findings y resumen por regla.
- `main.py`: orquestación de carga, validación y escritura; no contiene reglas.
- `tests/m01/test_m01_data_contract.py`: pruebas contractuales con el release.
- `tests/m01/test_m01_validation_rules.py`: casos en memoria y salida de reportes.

### Funciones / clases principales

- `load_m01_inputs(raw_dir) -> M01Inputs`
- `validate_m01_inputs(inputs) -> ValidationReport`
- `write_validation_outputs(report, output_dir) -> None`
- `CsvTable`, `M01Inputs`, `ValidationFinding`, `ValidationReport`

### Contratos aún no implementados

| Módulo | Input previsto | Output previsto |
|---|---|---|
| `desurvey.py` | Collar y survey validados | Trayectoria calculada por pozo y profundidad medida |
| `positioning.py` | Trayectoria y tablas intervalares | Intervalos asociados a la trayectoria según el plan M01 |
| `visualizer.py` | Trayectoria y resultados de posicionamiento | Visualización de inspección |
| `exporter.py` | Resultados acordados de M01 | Archivos derivados fuera de `data/raw/` |

Estos contratos no contienen implementación; sus detalles permanecen sujetos a
las convenciones y decisiones aprobadas para M01.

### Dependencias relevantes

- Solo biblioteca estándar de Python (`csv`, `json`, `pathlib`, `dataclasses`).
- No se instalaron dependencias.

## 9. Etapas de implementación

### Etapa 1 — Inventario de datos

- **Fecha:** previa a la implementación; fecha exacta no registrada.
- **Objetivo:** conocer los archivos disponibles y sus campos antes de definir
  el tratamiento computacional.
- **Trabajo realizado:** inventario de archivos, columnas, tipos, unidades
  documentadas, claves, relaciones y dudas del release.
- **Resultado:** identificado EXP03/DS04, incluidos los datos disponibles y
  `alteration.csv` vacío.
- **Pendiente:** utilizar el inventario como base del modelo conceptual.

### Etapa 2 — Modelo conceptual

- **Fecha:** previa a la implementación; fecha exacta no registrada.
- **Objetivo:** definir cómo se organiza el trabajo de M01.
- **Trabajo realizado:** el equipo completó el modelo conceptual antes de
  implementar.
- **Resultado:** separación modular entre carga, validación y etapas posteriores;
  este registro no reinterpreta las decisiones conceptuales del equipo.
- **Pendiente:** usar las definiciones aprobadas al implementar etapas posteriores.

### Etapa 3 — Plan de validación y T1

- **Fecha:** previa a la implementación de esta etapa; fecha exacta no registrada.
- **Objetivo:** acordar reglas y severidades antes de codificarlas.
- **Trabajo realizado:** según el equipo, se aprobó el plan de validación. El
  historial Git confirma que el commit `c40b793` agregó
  `outputs/tables/T1_audit_summary_DS04_EXP03.xlsx`.
- **Resultado:** el plan suministrado para esta implementación se toma como
  contrato de validación; el Excel T1 se conserva sin cambios.
- **Pendiente:** revisar con el equipo los findings producidos por Gate 5.

### Etapa 4 — Arquitectura, loader y contrato inicial

- **Fecha:** 2026-09-27.
- **Objetivo:** definir módulos e implementar la carga y validación del contrato
  de datos.
- **Trabajo realizado:** se acordó avanzar con loader, validator y pruebas;
  desurvey, positioning, visualizer y exporter quedaron sin implementación.
  Se añadieron el loader y las primeras reglas contractuales.
- **Resultado:** nueve pruebas iniciales pasaron con `unittest`.
- **Pendiente:** incorporar las reglas del plan aprobado en ETAPA 3.

### Etapa 5 — Reglas, findings y ejecución

- **Fecha:** 2026-09-27.
- **Objetivo:** implementar las reglas aprobadas, pruebas en memoria, CSV de
  findings/resumen y orquestación.
- **Trabajo realizado:** se añadieron findings estructurados con severidad,
  reglas de collar/survey/intervalos/assay/density/alteration/campañas, escritura
  de reportes y orquestación mínima en `main.py`.
- **Resultado:** 22 pruebas pasaron; `main.py` generó 11,062 findings:
  0 ERROR, 15 WARNING y 11,047 INFO. El resumen por regla suma 11,062.
- **Pendiente:** revisión y aprobación del equipo; no avanzar a desurvey.

## 10. Decisiones

### DECISION-01

**Problema:** cargar CSV sin añadir dependencias ni alterar fuentes.

**Alternativas consideradas:**

- A. Incorporar una librería tabular externa.
- B. Utilizar `csv` de la biblioteca estándar y preservar valores como texto.

**Alternativa seleccionada:** B.

**Justificación:** el alcance actual solo requiere leer filas, encabezados y
metadatos; no se requiere una nueva dependencia.

**Impacto:** la interpretación de los tipos queda centralizada en el validador.

## 11. Archivos creados o modificados

```text
src/m01/__init__.py
src/m01/loader.py
src/m01/validator.py
src/m01/validation_report.py
tests/m01/__init__.py
tests/m01/test_m01_data_contract.py
tests/m01/test_m01_validation_rules.py
main.py
outputs/tables/m01_validation_findings.csv
outputs/tables/m01_validation_summary.csv
docs/implementation/IMP-001_m01_validate_desurvey.md
```

## 12. Pruebas realizadas

### Comandos ejecutados

```text
python -m unittest discover -s tests -v
python main.py
```

Ejecutados desde la raíz `C:\Proyecto_Plan\PlanMinUPN-G04` con el entorno
Python existente. `git diff --check` no reportó errores.

### Resultado real

- **Status:** PASS
- **Tests passed:** 22
- **Tests failed:** 0

### Ejecución de `main.py` sobre el release

- **Findings:** 11,062
- **ERROR:** 0
- **WARNING:** 15 (`CAMPAIGN_ID_EQUIVALENCE`)
- **INFO:** 11,047 (`ASSAY_GRADE_ZERO`: 10,551; `INTERVAL_GAP_DENSITY`: 460;
  `DENSITY_COVERAGE`: 35; `ALTERATION_UNAVAILABLE`: 1)
- **Salidas:** `outputs/tables/m01_validation_findings.csv` y
  `outputs/tables/m01_validation_summary.csv`
- **Datos fuente:** los ocho hashes publicados en el manifest siguen
  coincidiendo; `data/raw/` no se modificó.

## 13. Validación minera

- [ ] Unidades consistentes.
- [ ] Signos económicos correctos cuando corresponda.
- [ ] Magnitudes razonables.
- [ ] Restricciones operacionales respetadas.
- [x] Reglas M01 y casos límite revisados computacionalmente.
- [ ] Caso manual independiente revisado cuando es posible.

### Evidencia / comentario

La ejecución produjo 0 errores, 15 advertencias de nomenclatura de campaña y
11,047 observaciones INFO. Los ceros de assay y los gaps/cobertura de density
requieren lectura del equipo. El resultado no valida trayectorias ni sustituye
la revisión y aprobación del equipo.

## 14. Limitaciones y pendientes

### LIMITATION-01

No se validan convenciones angulares ni geometría del survey. No se calculan
coordenadas de trayectoria.

### FUTURE-01

Implementar `desurvey.py` solo después de la revisión/aprobación del equipo y el
cierre de Gate 5. `positioning.py`, `visualizer.py` y `exporter.py` siguen fuera
de este gate.

## 15. Uso del agente de IA

- [x] Arquitectura.
- [x] Implementación.
- [x] Pruebas.
- [x] Documentación.

Comentario: implementación de la carga de datos, validación contractual,
pruebas automatizadas y registro inicial de trazabilidad.

## 16. Checklist de cierre

- [x] Problema minero documentado.
- [x] Inputs documentados.
- [x] Unidades verificadas en la fuente documental.
- [x] Supuestos identificados.
- [ ] Lógica minera documentada y validada.
- [ ] Implementación terminada para M01.
- [x] Pruebas ejecutadas.
- [x] Validación computacional realizada para el alcance implementado.
- [ ] Validación minera de desurvey realizada.
- [x] Archivos modificados registrados.
- [x] Limitaciones registradas.
- [x] Registro actualizado.

**M01 permanece `IN_PROGRESS`.**
