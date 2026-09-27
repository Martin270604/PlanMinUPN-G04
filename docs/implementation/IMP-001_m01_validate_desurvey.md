# IMP-001 — M01 Validate & Desurvey

## 1. Identificación

- **Implementation ID:** IMP-001
- **Module:** M01 — Validate & Desurvey
- **Date:** 2026-09-27
- **Group:** Not provided
- **Participants:** Not provided
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
| Diccionario | Definiciones de campos, unidades y tipos | No aplica | `data/raw/data_dictionary.csv` | Sí | Columnas requeridas y definiciones aplicables a cada tabla |
| Manifest | Identidad del release, archivos y conteos publicados | No aplica | `data/raw/release_manifest.json` | Sí | Archivos, conteos e identidad del dataset/proyecto |

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| `M01Inputs.tables` | Encabezados y filas CSV cargadas como texto, por archivo | Según campos originales | Memoria |
| `M01Inputs.data_dictionary` | Diccionario leído | No aplica | Memoria |
| `M01Inputs.manifest` | Manifest leído como objeto JSON | No aplica | Memoria |
| `ValidationReport` | Lista de hallazgos del contrato de entrada | No aplica | Memoria |

## 6. Supuestos

No se incorporan supuestos mineros. Los valores CSV se conservan como texto al
cargar y el validador interpreta únicamente los tipos declarados por el
diccionario.

## 7. Lógica minera

Esta etapa no realiza cálculos mineros ni geométricos. Comprueba los contratos
documentados: estructura de columnas, compatibilidad con tipos declarados,
campos no anulables, conteos e identidad declarados en el manifest, unicidad de
los identificadores estables de collar/assay/density y referencias de `hole_id`
contra collar. No valida geometría, continuidad de intervalos ni reglas de
desurvey.

## 8. Diseño computacional

### Módulos / archivos

- `src/m01/loader.py`: lectura de los cinco CSV fuente, `data_dictionary.csv` y
  `release_manifest.json`; apertura de fuentes en modo lectura.
- `src/m01/validator.py`: validación del contrato documentado y creación de un
  informe estructurado.
- `tests/m01/test_m01_data_contract.py`: pruebas unitarias y prueba con el
  release disponible.

### Funciones / clases principales

- `load_m01_inputs(raw_dir) -> M01Inputs`
- `validate_m01_inputs(inputs) -> ValidationReport`
- `CsvTable`, `M01Inputs`, `ValidationIssue`, `ValidationReport`

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

### Etapa 1 — 2026-09-27

- **Objetivo:** delimitar la arquitectura modular para comenzar M01.
- **Trabajo realizado:** se acordó avanzar con loader, validator y tests, dejando
  los módulos de desurvey, posicionamiento, visualización y exportación sin
  implementar.
- **Resultado:** alcance acotado a carga y validación de contratos documentados.
- **Pendiente:** implementar y validar desurvey conforme a las convenciones
  aprobadas por el equipo.

### Etapa 2 — 2026-09-27

- **Objetivo:** implementar la carga y validación del contrato de datos.
- **Trabajo realizado:** se añadieron loader, validator y pruebas con el release
  y modificaciones en memoria para casos inválidos.
- **Resultado:** 9 pruebas pasaron con `unittest`.
- **Pendiente:** incorporar el plan de validación del equipo en lo que exceda el
  contrato de metadatos, y validar etapas posteriores de M01.

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
tests/m01/__init__.py
tests/m01/test_m01_data_contract.py
docs/implementation/IMP-001_m01_validate_desurvey.md
```

## 12. Pruebas realizadas

### Comandos ejecutados

```text
python -m unittest discover -s tests -v
```

Ejecutado desde la raíz del repositorio usando el Python disponible en el
entorno existente.

### Resultado real

- **Status:** PASS
- **Tests passed:** 9
- **Tests failed:** 0

## 13. Validación minera

- [ ] Unidades consistentes.
- [ ] Signos económicos correctos cuando corresponda.
- [ ] Magnitudes razonables.
- [ ] Restricciones operacionales respetadas.
- [x] Casos de contrato inválido revisados.
- [ ] Caso manual independiente revisado cuando es posible.

### Evidencia / comentario

La prueba contra el release confirma concordancia con el esquema, tipos,
conteos e identificadores definidos en sus metadatos. Esto no constituye
validación minera de la trayectoria ni reemplaza las pruebas de desurvey.

## 14. Limitaciones y pendientes

### LIMITATION-01

No se validan convenciones angulares, geometría del survey, cálculo de
coordenadas, continuidad de intervalos ni cobertura de densidad.

### FUTURE-01

Implementar `desurvey.py`, `positioning.py`, `visualizer.py` y `exporter.py`
únicamente cuando sus contratos y decisiones de M01 estén aprobados.

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
