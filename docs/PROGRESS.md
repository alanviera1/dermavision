# PROGRESS — Dermavision (Sistema Experto Dermocosmético Cuantitativo)

Bitácora de estado, decisiones y próximos pasos. **Obligatorio actualizar al completar cada tarea o fase** para no perder contexto entre sesiones.

Última actualización: 2026-08-09

---

## Estado actual

| Ítem | Estado |
|---|---|
| Plan aprobado (docs/PLAN.md) | ✅ Completado |
| Scaffolding del repositorio | ✅ Completado |
| Commit inicial + push a GitHub | ✅ Completado |
| Fase 0 — Recopilación de datasets (BOM de licencias) | 🟡 En curso (paso 1 de 3) |
| Fase 1 — Pipeline de estandarización | ⏳ Pendiente |

## Fase 0 — Checklist

- [x] 1. Recopilación y catalogación de datasets con **BOM de licencias** (`docs/DATASETS.md`)
- [x] 2. Descargas automatizadas (Fitzpatrick17k CSV ✅, MEMI-DS ✅) y script `scripts/download_datasets.py`
- [ ] 3. Descargas manuales/requieren clave (ACNE04, Roboflow, ISIC) — ver `docs/DATASETS.md` (pendiente)

## Decisiones técnicas tomadas en el camino

| Fecha | Decisión | Contexto |
|---|---|---|
| 2026-08-09 | Python 3.11 + venv local `.venv` (aprobado por usuario) | Entorno detectado: 3.11.9 |
| 2026-08-09 | Schemas de la KB (campos de `activos.yaml`) congelados como contrato de Fase 4 (aprobado por usuario) | Añadir activos exige cumplir el schema validado en `tests/unit/test_kb.py` |
| 2026-08-09 | Repo en `https://github.com/alanviera1/dermavision`, rama `main`, remoto `origin` | Push inicial OK |
| 2026-08-09 | Convención de commits convencional: `feat:`, `fix:`, `docs:`, `chore:`; commits atómicos por hito | Regla de flujo de trabajo del usuario |
| 2026-08-09 | ACNE04 (licencia de investigación) + ACNE04-v2 (anotaciones COCO) como base de detección de acné | Wu et al. ICCV 2019; Gazeau et al. MICCAI 2024 |
| 2026-08-09 | MEMI-DS (CC BY 4.0, figshare) como dataset de segmentación de melasma | Zhai et al. 2025, 716 imgs con máscaras |
| 2026-08-09 | Roboflow Universe como fuente complementaria (CC BY 4.0) vía API key gratuita | Skin-Analysis-v3 (2,623 imgs), acne04 (1,419), melasma (512) |
| 2026-08-09 | ISIC Archive vía `isic-cli` para lesiones pigmentarias (licencia por colección) | Pendiente de descarga |
| 2026-08-09 | Fitzpatrick17k: CSV público descargado; imágenes requieren formulario a autores | CC BY-NC-SA 3.0 — uso no comercial |
| 2026-08-09 | Datos de pacientes: uso exclusivo de investigación, sin redistribución; reportar en la documentación del producto | Ética |
| 2026-08-09 | Directiva de estilo: documentar todo como producto de software profesional; sin referencias de ámbito educativo en código, documentación o mensajes de commit | Regla obligatoria del usuario |

## Historial de hitos

- **2026-08-09 — hito 1**: `docs/PLAN.md` aprobado; scaffolding completo (src layout, FastAPI, módulos A–D, Alembic, CI, tests); 12 tests en verde, ruff limpio, cobertura 72%.
- **2026-08-09 — hito 2**: commit inicial `910c25d` (`feat: scaffolding inicial`), rama `main`, push a GitHub OK.
- **2026-08-09 — hito 3**: BOM de licencias creado (`docs/DATASETS.md`); `scripts/download_datasets.py` implementado (con reintentos para URLs presignadas S3 de figshare); **Fitzpatrick17k CSV (16,577 filas) y MEMI-DS (131 imágenes + 131 máscaras, 165.5 MB, 0 archivos vacíos) descargados y verificados**. Hallazgo: figshare bloquea el zip directo con AWS WAF; se resuelve vía API por archivo con reintentos ante expiración del presigned URL (10 s).

## Próximos pasos

1. Terminar Fase 0 paso 3: descargar ACNE04 (espejo HuggingFace `ManuelHettich/acne04` o Kaggle) y decidir qué datasets de Roboflow usar (requiere cuenta gratuita + `RF_API_KEY`).
2. Verificar integridad de MEMI-DS (716 imgs + máscaras) y documentar estructura interna real en `docs/DATASETS.md`.
3. Fase 1: pipeline de estandarización (QA, balance de blancos, Retinex, CLAHE, denoise, alineación facial, BiSeNet, ITA) con test de varianza temporal < 5%.
