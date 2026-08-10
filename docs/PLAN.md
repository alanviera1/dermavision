# Plan de Desarrollo Técnico — Sistema Experto de Análisis Dermocosmético Cuantitativo

**v1.0 (aprobado) · Última revisión: 2026-08-09**

---

## 1. Resumen ejecutivo

La adquisición de productos dermocosméticos es ineficiente: los usuarios compran guiados por marketing, generando gastos innecesarios y posibles daños a la barrera cutánea. Las IAs generativas actuales ofrecen diagnósticos cualitativos genéricos que pueden incurrir en alucinaciones peligrosas (ej. recomendar ácidos fotosensibles en zonas con alta radiación UV).

Este proyecto construye un **Sistema Experto de Análisis Dermocosmético Cuantitativo** con dos ventajas injustas:

1. **Análisis matemático**: métricas cuantitativas extraídas de imágenes ( % de área con hiperpigmentación, conteo de comedones, % de eritema), cruzadas con el contexto climático del usuario (temperatura, humedad, índice UV) para prescribir **activos químicos puros con concentración**, no marcas comerciales.
2. **Agnóstico al hardware**: un pipeline de estandarización de imagen garantiza precisión clínica reproducible independientemente de la calidad de la cámara y de las condiciones de iluminación.

El núcleo del sistema es **100% determinista** (motor de reglas con base de conocimiento clínica versionada y citada). El uso de LLM queda relegado a una **capa de presentación opcional** que nunca participa en la decisión clínica.

**Restricción global del proyecto**: 100% gratuito y viable — free tiers y open-source sostenibles exclusivamente.

---

## 2. Decisiones arquitectónicas clave

| Decisión | Elección | Justificación |
|---|---|---|
| Arquitectura | **Monolito modular** (FastAPI) con 4 dominios internos (A: visión, B: clima, C: reglas, D: trazabilidad) | A la escala del producto, microservicios añaden complejidad sin beneficio. Fronteras de dominio claras dentro de un solo servicio |
| Núcleo de inferencia | **Determinista** (CV de transfer learning + motor de reglas) | Exigencia clínica: mismo input → mismo output. Reproducibilidad y auditabilidad totales |
| LLM | Solo capa de presentación **opcional**, con validación estricta de salida | El reto clínico prohíbe LLM en la ruta crítica |
| Plataforma | **PWA web** (React + Vite + `getUserMedia`) | Máxima simplicidad, $0, instalable en móvil; captura de cámara nativa del navegador |
| Clima | **Open-Meteo** (gratis, sin API key, incluye `uv_index`, temperatura, humedad) | Verificado: gratis, sin registro, sin límites razonables |
| BD + Auth + Storage | **Supabase** (PostgreSQL + Auth + Storage) | Free tier: 500 MB BD, 1 GB storage; PostgreSQL estándar (SQLAlchemy + Alembic) |
| MVP de métricas | Acné + hiperpigmentación + eritema | Datasets públicos sólidos. Poros/arrugas quedan como extensión documentada |

---

## 3. Stack tecnológico (100% gratuito / open-source)

### Backend y datos

| Capa | Tecnología | Licencia / Free tier |
|---|---|---|
| Lenguaje | Python ≥ 3.11 | Open source |
| API | FastAPI + Uvicorn | MIT |
| Cola (opcional) | Celery + Redis (free tier) | BSD / AGPL-compatible uso |
| BD + Auth + Storage | Supabase (PostgreSQL 15+) | Free tier |
| Migraciones | Alembic | MIT |
| Configuración | pydantic-settings | MIT |
| Tests | pytest + pytest-cov + hypothesis | MIT |
| Lint/format | ruff (+ pre-commit) | MIT |
| Versionado de datos/modelos | DVC + MLflow | Apache-2.0 |
| CI | GitHub Actions (ubuntu-latest, free) | $0 |
| Dev DB local | Docker Compose (postgres:16-alpine) | Apache-2.0 / $0 |

### Visión por computadora (Módulo A)

| Componente | Tecnología | Licencia |
|---|---|---|
| Detección facial + landmarks | MediaPipe Face Mesh / BlazeFace | Apache-2.0 |
| Segmentación de región facial | BiSeNet face parsing (pre-entrenado) | MIT |
| Detección de lesiones de acné | Ultralytics YOLOv8n (fine-tune) | AGPL-3.0 (válido para uso no comercial; alternativa Apache-2.0 documentada: RT-DETR) |
| Segmentación de pigmentación/eritema | U-Net / DeepLabV3+ (ResNet50, timm) | MIT / Apache-2.0 |
| Preprocesamiento | OpenCV, scikit-image, CLAHE, Retinex, filtros bilaterales | BSD |
| Up-scaling opcional | Real-ESRGAN (solo si QA lo permite) | BSD-3 |
| Aumentación | Albumentations | MIT |
| Entrenamiento | Google Colab free (T4) / Kaggle (GPU gratis) | $0 |
| Anotación asistida | Label Studio (self-hosted) | Apache-2.0 |

### Frontend, contexto y presentación

| Componente | Tecnología | Nota |
|---|---|---|
| Frontend | React + Vite + Tailwind, PWA con `getUserMedia` | Deploy Vercel free tier (Fase 5) |
| Geolocalización | `navigator.geolocation` + validación manual (viajes, permisos denegados) | — |
| Clima/UV | Open-Meteo `api.open-meteo.com` (actual + pronóstico) | Gratis, sin API key; caché 30 min |
| LLM (opcional) | Gemini Flash free tier **o** local vía Ollama (Qwen/Llama 7-8B) | Rate-limited o $0; nunca en ruta crítica |

---

## 4. Arquitectura del sistema y flujo de datos

```
[PWA] Foto frontal (getUserMedia, guía de encuadre/iluminación)
  │  POST /api/v1/analyze  (JWT, Supabase Auth)
  ▼
[A] QA de imagen ──(rechazo: imagen borrosa/mal expuesta → NO se recomienda,
│   solo guía de recaptura: "abstención activa")
│   Estandarización: balance de blancos (Gray World) → corrección de
│   iluminación no uniforme (Retinex) → CLAHE (LAB) → denoise NLM leve
│   → alineación affine a template facial 1024px (landmarks MediaPipe)
│   → enmascarado de cabello/ojos/fondo (BiSeNet) → cálculo de ITA
│   (tipo de piel Fitzpatrick, matemático y reproducible)
│   → Modelos: YOLOv8n (lesiones) + U-Net (pigmentación/eritema)
│   → MÉTRICAS JSON: {pigmentacion_pct_por_zona, comedones_abiertos,
│     papulas_pustulas, eritema_pct, ita, fitzpatrick, confianza}
  ▼
[B] Contexto: {lat, lon} validado por el usuario → Open-Meteo →
│   {temp_C, humedad_rel, uv_index_actual, uv_max_hoy}
  ▼
[C] Motor de reglas (KB versión vX.Y):
│   1) Filtro de seguridad (bloqueos duros)
│   2) Reglas de indicación (métricas × clima × perfil)
│   3) Ranking y emisión (activos + concentración + frecuencia + momento)
│   → [LLM presentación opcional: texto amigable VALIDADO contra el JSON]
  ▼
[D] Snapshot inmutable en Supabase (imagen + métricas + clima + rec +
│   versiones de modelo/KB + reglas disparadas) → respuesta al cliente
│
│  GET /api/v1/progress ── alinea con snapshot anterior → delta% por
└── métrica → tasa de mejora + gráfica de evolución
```

---

## 5. Módulo A — Motor de visión (agnosticismo de hardware)

**Principio**: toda fotografía se lleva a un espacio canónico (mismo encuadre, misma escala, misma iluminación aparente) antes de medir. Una foto de gama baja en una habitación oscura produce métricas comparables a una de cámara tope.

### 5.1 Pipeline de estandarización (en orden)

1. **QA de entrada**: nitidez (varianza del Laplaciano), sobreexposición/subexposición, resolución mínima, presencia de rostro detectable. Si falla → **abstención activa** (guía de recaptura). Mejor no responder que responder mal.
2. **Balance de blancos** (Gray World + Shades of Gray) y **corrección de iluminación no uniforme** (shading correction / Retinex) → elimina dominantes de color de bombillas cálidas/frías y sombras.
3. **CLAHE** en el canal L de LAB → contraste local sin amplificar ruido.
4. **Denoise** Non-Local Means *leve* (preservar textura de piel; ruido fuerte se descarta en QA).
5. **Alineación facial** (MediaPipe landmarks → transformación affine a template 1024×1024): estandariza escala, rotación, distancia focal y gesto. Habilita la resta de métricas entre fotos (Módulo D).
6. **Enmascarado de región**: BiSeNet excluye cabello, ojos, cejas, fondo → métricas solo sobre piel, por zonas (frente, mejillas, mentón).
7. **Calibración de color por parche de referencia** (piel sana de la misma imagen) → comparabilidad temporal robusta.
8. **Estimación de Fitzpatrick por ITA** (fórmula del color, no red neuronal): `ITA = arctan((L* − 50)/b*) × 180/π`. Matemático, reproducible y auditable.

### 5.2 Modelos y métricas (fine-tuning sobre datasets públicos)

- **YOLOv8n** (lesiones de acné): conteo de comedones abiertos/cerrados, pápulas, pústulas.
  - Datasets: Roboflow Universe (`Skin-Analysis-v3`, CC-BY-4.0: acne, dark circles, freckles, redness, whiteheads, wrinkles), ACNE04; anotación propia asistida (Label Studio) de 200–500 imágenes si se requiere.
- **U-Net / DeepLabV3+** (segmentación): % de área con hiperpigmentación y % con eritema, por zona facial.
  - Datasets: FITZPATRICK17k (16.5k imágenes clínicas, CC-BY-NC-SA — uso no comercial), ISIC Archive.
- **Heurísticas validadas** (extensión): porosidad (filtros Gabor + estadística de textura), líneas finas.
- Toda métrica emite **confianza** (0–1) derivada del QA + variabilidad del modelo.

### 5.3 Criterios de éxito del módulo

- IoU ≥ 0.70 en segmentación de pigmentación.
- mAP@0.5 ≥ 0.70 en detección de lesiones.
- **Varianza temporal < 5%**: misma persona, misma sesión, fotos simuladas con perturbaciones de iluminación/ruido.

---

## 6. Módulo B — Motor de contexto ambiental

1. `navigator.geolocation` → lat/lon → **el usuario confirma o corrige** (campo de texto + búsqueda) para contemplar viajes, cambios de residencia o permisos denegados.
2. `GET api.open-meteo.com/v1/forecast?latitude&longitude&current=temperature_2m,relative_humidity_2m,uv_index&daily=uv_index_max` — gratis, sin API key.
3. Caché en memoria de 30 min por coordenada (evita abuso y latencia).
4. Fallback: sin GPS ni corrección manual → **suposiciones conservadoras** (UV del peor caso) anunciadas al usuario.

---

## 7. Módulo C — Motor de reglas y abordaje del reto clínico

### 7.1 Estrategia sin profesionales médicos en el equipo

El sistema **no necesita "saber medicina"**: necesita que su base de conocimiento esté restringida a lo que la evidencia pública establece con certeza, y ser **fail-safe ante la duda**. No inventa: **abstiene**.

### 7.2 Estructura de la base de conocimiento (versionada, citada, migrable)

Tablas SQL (Alembic) + reglas YAML versionadas en el repo (`src/dermavision/modules/rules/kb/`):

| Tabla/archivo | Contenido |
|---|---|
| `activos` | Nombre INCI, mecanismo, pH óptimo, concentración mínima eficaz, concentración máxima segura, fotosensibilidad, categoría en embarazo, incompatibilidades, forma cosmética |
| `indicaciones` | (métrica, severidad, tipo de piel) → activos rankeados con nivel de evidencia |
| `reglas_bloqueo` | Combinaciones prohibidas + condiciones (UV alto, embarazo, piel dañada, etc.) |
| `reglas_climaticas` | Ajustes por T/humedad/UV (fase, textura, momento del día) |
| `citas_evidencia` | Fuente de cada regla: DOI de PubMed, informe CIR, guía EADV/AAD, URL |

**Fuentes públicas y gratuitas (verificadas)**:

- **CIR — Cosmetic Ingredient Review** (cir-safety.org): informes públicos de seguridad e ingestión de cada activo cosmético (incluye rangos de concentración). Fuente primaria más rigurosa y accesible.
- **Guías de consenso**: EADV (acné, rosácea, hiperpigmentación), AAD.
- **PubMed**: revisiones sistemáticas y metaanálisis de eficacia de concentraciones (retinoides, AHA/BHA, niacinamida, ácido azelaico).
- **PubChem / INCI UE**: propiedades fisicoquímicas.

Cada regla lleva `evidence_refs[]` + `confidence` + `version`. **Sin cita → la regla no entra.**

### 7.3 El motor (determinista, 3 etapas)

1. **Filtro de seguridad (bloqueos duros, no negociables)**:
   - UV actual o máximo del día > 5 y activo fotosensible (AHA, BHA, retinoide, hidroquinona) → bloqueo de uso diurno; prescripción nocturna condicionada a SPF; si no se puede garantizar → abstención de ese activo.
   - Embarazo/lactancia declarado → bloqueo de retinol/retinoides, hidroquinona, ácido salicílico > 1%.
   - Retinol + AHA/BHA en la misma aplicación → bloqueo (permitir alternancia día/noche).
   - BPO + retinoide en la misma capa → bloqueo.
   - Concentración solicitada > máximo seguro → cap al máximo.
   - Barrera comprometida (eritema + sequedad severos) → modo reparación (ceramidas, niacinamida baja), sin ácidos.
2. **Reglas de indicación** (métricas × clima × perfil): severidad de acné → primera línea (ej. niacinamida 4–5% + BHA 1% alternado); hiperpigmentación en Fitzpatrick IV–VI → azelaico 10–15% nocturno (evitar hidroquinona por riesgo de hiperpigmentación postinflamatoria); humedad < 30% → humectación reforzada (ceramidas, glicerina); T alta → texturas gel.
3. **Ranking y emisión**: score de (evidencia × match × seguridad) → JSON con activos, concentración, frecuencia, momento, duración, fase y razones plantilladas.

### 7.4 Salvaguardas éticas y técnicas

1. **Abstención activa**: QA pobre, lesiones fuera del alcance de métricas estéticas, o regla no resoluble → "no puedo recomendar con seguridad" + guía. Métrica: tasa de abstención ≥ 5%.
2. **Nunca diagnostica enfermedad**: solo métricas estéticas. Heurística conservadora de alerta ABCD (asimetría, borde irregular, color no uniforme, diámetro > 6 mm) → redirige a dermatólogo. Sin diagnóstico ni recomendación.
3. **Property tests** (`hypothesis`): genera todas las combinaciones (perfil × clima × severidad) y verifica que **ninguna combinación peligrosa salga al usuario** (cobertura 100% de `reglas_bloqueo`). Artefacto de validación del producto.
4. **Validación externa de la KB**: revisión de pares de la KB v1 por un farmacéutico o dermatólogo externo (una sesión, costo ~0 si es contacto universitario), dictamen documentado en la documentación técnica del producto. El diseño fail-safe no depende de esto.
5. **Trazabilidad completa**: cada recomendación persiste versión de KB, modelo, reglas disparadas y clima → auditable y reproducible.
6. **Privacidad**: imágenes = datos biométricos → GDPR/LOPD: consentimiento informado, cifrado, Supabase RLS, derecho al borrado, metadatos mínimos.
7. **Disclaimer legal** en cada salida: no sustituye atención médica.

### 7.5 Activos del MVP (v1, ~20–30 nucleares)

Niacinamida, ácido azelaico, retinol, adapaleno OTC, BPO, AHA (glicólico, láctico), BHA (salicílico), vitamina C (L-ascórbico 10–15%), ceramidas, glicerina, ácido hialurónico, escualano, filtros solares (ZnO, avobenzona), pantenol, cafeína — cada uno con su fila de evidencia CIR/guias.

---

## 8. Módulo D — Perfiles, trazabilidad y evolución

- **Perfil**: edad, Fitzpatrick autoevaluado, fototipo declarado, embarazo/lactancia, alergias/medicación, rutina actual, alergias a activos.
- **Snapshot inmutable por análisis**: imagen original + normalizada + métricas + contexto climático + recomendación + versiones (modelo, KB) + timestamp. Nunca se modifica → integridad de comparación.
- **Comparación temporal**: la misma alineación facial del pipeline permite superponer snapshots del mismo usuario (registro de imágenes: landmarks compartidos + correlación de fase). **Delta por métrica**: `Δ% = (métrica_t2 − métrica_t1)/métrica_t1` → tasa de mejora y tablero de evolución por zona facial; valida empíricamente la eficacia de la rutina (cierre del bucle C → D).
- Umbral mínimo de similitud de pose entre snapshots; si difieren demasiado → se notifica que la comparación no es válida (evita falsos deltas).

---

## 9. Decisión sobre LLMs

- **No** en el núcleo: el motor de reglas es 100% determinista (exigencia clínica y de reproducibilidad del producto).
- **Sí, opcional, solo presentación**: Gemini Flash free tier (o Qwen local vía Ollama) recibe el JSON estructurado y genera explicación en lenguaje natural amigable. **Validación estricta de salida** (no puede alterar activos/concentraciones; fallback automático a plantillas). Descartable sin afectar al sistema — se documenta como decisión arquitectónica.

---

## 10. Estructura del repositorio (scaffold aprobado)

```
dermavision/
├── docs/PLAN.md
├── src/dermavision/
│   ├── main.py                    # FastAPI app + /health
│   ├── config.py                  # pydantic-settings (env DERMA_*)
│   ├── api/
│   │   ├── routes/                # analyze.py, progress.py
│   │   └── schemas/               # contratos Pydantic (métricas, clima, rec)
│   ├── modules/
│   │   ├── vision/                # Módulo A: qa, standardization, face, ita, detectors, segmenters
│   │   ├── climate/               # Módulo B: geolocation, openmeteo_client, cache
│   │   ├── rules/                 # Módulo C: engine, kb/*.yaml
│   │   └── tracking/              # Módulo D: profiles, snapshots, comparison
│   ├── presentation/              # Capa LLM opcional validada
│   └── db/                        # SQLAlchemy Base + migraciones Alembic
├── tests/                         # unit/, property/, integration/
├── models/                        # artefactos de modelos (DVC, gitignored)
├── data/{raw,processed}/          # datasets (DVC, gitignored)
├── notebooks/                     # experimentos de entrenamiento (Colab)
├── scripts/                       # download_datasets.py, train_*.py
├── .github/workflows/ci.yml       # ruff + pytest + coverage
├── pyproject.toml
├── docker-compose.yml             # postgres local de desarrollo
└── .env.example
```

**Convenciones**: identificadores de código en inglés; documentación en español; BOM de licencias de datasets en Fase 0; sin comentarios de código salvo necesidad explícita.

---

## 11. Roadmap por fases (12–16 semanas)

| Fase | Semanas | Entregables | Verificación |
|---|---|---|---|
| **F0 — Fundación** | 1–2 | Repo operativo, CI verde, Docker, schema Supabase (Alembic), recopilación de datasets con **BOM de licencias** documentada | `pytest` verde; datos descargables y licenciados |
| **F1 — Estandarización** | 3–4 | QA, balance de blancos, Retinex, CLAHE, denoise, alineación facial, enmascarado BiSeNet, ITA | Varianza temporal < 5%; rate de rechazo en imágenes degradadas |
| **F2 — Métricas** | 5–7 | Fine-tune YOLOv8n + U-Net (Colab), pipeline de métricas por zona, anotación asistida si se requiere | IoU ≥ 0.70, mAP ≥ 0.70, fairness por Fitzpatrick con FITZPATRICK17k |
| **F3 — Clima** | 8 | Servicio Open-Meteo + geolocalización + validación manual + caché | Tests de integración; fallbacks probados |
| **F4 — KB + Reglas** | 9–11 | KB v1 (20–30 activos citados), motor de reglas, property tests de bloqueos, revisión externa de pares | **0 combinaciones peligrosas emitidas**; suite hypothesis completa |
| **F5 — Producto** | 11–13 | API + PWA (cámara, perfil, resultados), snapshots, comparación temporal | E2E: analizar → recomendar → comparar |
| **F6 — Validación** | 13–16 | Pruebas con usuarios piloto, métricas finales, fairness, documentación técnica del producto | Hipótesis del producto validadas con datos |

---

## 12. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Datos clínicos anotados insuficientes (comedones) | Múltiples datasets públicos + anotación propia (Label Studio) + aumentación |
| Sesgo en pieles oscuras | FITZPATRICK17k para balanceo; métricas separadas por subgrupo |
| Responsabilidad legal | Abstención, nunca diagnóstico, disclaimers, alerta ABCD → dermatólogo |
| Límites de free tiers (Vercel/Supabase) | Diseño para la escala del producto; procesamiento pesado en Colab/batch |
| Sobre-extensión de alcance | MVP = acné + hiperpigmentación + eritema + humectación; poros/arrugas como extensión |
| Licencias (AGPL de YOLO) | Válido para uso no comercial; alternativa Apache-2.0 (RT-DETR) documentada |
| Ocio del calendario (picos de exámenes) | Fases de 1–2 semanas con entregables independientes; CI como verificación continua |

---

## 13. Hipótesis medibles del producto

1. El pipeline de estandarización permite métricas reproducibles entre dispositivos de distinta calidad (varianza < 5%).
2. El motor determinista emite **0 combinaciones peligrosas** en el espacio completo de estados (property tests).
3. La comparación temporal cuantifica mejora/regresión de la rutina con deltas matemáticos auditables.
4. La tasa de abstención en imágenes de baja calidad evita recomendaciones inseguras (≥ 5%).

---

## 14. Alcance fuera del MVP (extensión documentada)

- Porosidad y arrugas (heurísticas Gabor / textura).
- Comparación de productos reales (marcas → mapeo INCI).
- Aplicación móvil nativa (React Native/Flutter) si el PWA queda corto.
- Integración de retail / e-commerce (fuera del alcance ético del MVP).
