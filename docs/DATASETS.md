# BOM de Datasets — Fase 0 (Bill of Materials con licencias)

Catálogo oficial de datasets del proyecto. **Regla**: ningún dataset se integra sin fila verificada en este documento. Licencias verificadas el 2026-08-09.

**Uso ético**: los datos contienen imágenes clínicas de pacientes. Uso exclusivo de investigación; sin redistribución, sin re-identificación; declarar origen y licencias en la documentación del producto.

---

## 1. Detección de lesiones de acné (YOLOv8n)

| Dataset | Nº imágenes | Anotaciones | Licencia | Acceso | Estado |
|---|---|---|---|---|---|
| **ACNE04** (Wu et al., ICCV 2019) | 1,457 | Bounding boxes + conteo + severidad | **Restringida a fines de investigación** (contactar autor: Xiaoping Wu, xpwu95@163.com para otros usos) | GitHub `xpwu95/LDL`; espejos sin marca de agua: HuggingFace `ManuelHettich/acne04`, Kaggle `manuelhettich/acne04` | ⏳ Pendiente descarga |
| **ACNE04-v2** (Gazeau et al., MICCAI 2024, AcneAI) | 1,204 | 32,443 anotaciones COCO (centro + radio por lesión) | Investigación (deriva de ACNE04) | GitHub `AIpourlapeau/acne04v2` | ⏳ Pendiente |
| **Roboflow acne04** (Andrei Dore) | 1,419 | Detección 7 clases (blackheads, whiteheads, papule, pustule, nodule, cyst, fire) | CC BY 4.0 | Roboflow Universe `andrei-dore-5lz05/acne04` (API key gratuita) | ⏳ Pendiente |
| **Roboflow Skin-Analysis-v3** (Faceinfo) | 2,623 | Detección: Acne, Dark Circle, freckles, Redness, whiteheads, Wrinkles | CC BY 4.0 | Roboflow Universe `faceinfo/skin-analysis-v3-jwjcp` | ⏳ Pendiente |

## 2. Segmentación de hiperpigmentación / melasma (U-Net)

| Dataset | Nº imágenes | Anotaciones | Licencia | Acceso | Estado |
|---|---|---|---|---|---|
| **MEMI-DS** (Zhai et al., 2025) | **131 imágenes + 131 máscaras** (artículo figshare v1; el paper declara 716 — el zip/artículo publicado contiene este subconjunto) | Máscaras de segmentación de melasma (modo P, 0/255) en espejo exacto de cada imagen (3456×5184) | CC BY 4.0 | figshare, DOI `10.6084/m9.figshare.29209229`; descarga vía API `api.figshare.com/v2/articles/29209229` (el zip directo está tras AWS WAF; descarga por archivo con reintentos) | ✅ Descargado y verificado |
| **Roboflow melasma** (ayezka) | 512 | Segmentación de instancias (melasma, hyperpigmentation, acne, black_head, wrinkles) | CC BY 4.0 | Roboflow Universe `ayezka/melasma-wf8lz` | ⏳ Pendiente |

## 3. Fairness, tipo de piel y lesiones pigmentarias

| Dataset | Nº imágenes | Anotaciones | Licencia | Acceso | Estado |
|---|---|---|---|---|---|
| **Fitzpatrick17k** (Groh et al., 2021) | 16,577 | 114 condiciones + tipo de piel Fitzpatrick I–VI | **CC BY-NC-SA 3.0** (uso no comercial) | CSV público en GitHub `mattgroh/fitzpatrick17k`; **imágenes: formulario a autores** | ✅ CSV descargado; ⏳ imágenes por formulario |
| **ISIC Archive** | >90k (múltiples colecciones) | Diagnósticos, segmentaciones por colección | Por colección (mayoría CC; verificar cada una) | `isic-cli` (pip) / API `isic-archive.com` | ⏳ Pendiente |

## 4. Región facial (infraestructura de Fase 1)

| Modelo/Recurso | Propósito | Licencia | Acceso | Estado |
|---|---|---|---|---|
| **MediaPipe Face Mesh / BlazeFace** | Detección facial + landmarks (alineación) | Apache-2.0 | pip `mediapipe` | ✅ Dependencia declarada |
| **BiSeNet face parsing** (pre-entrenado) | Enmascarado cabello/ojos/fondo | MIT | GitHub `zllrunning/face-parsing.PyTorch` (pesos `79999_iter.pth`) | ⏳ Fase 1 |

## Comandos de descarga

```bash
# Fitzpatrick17k CSV + MEMI-DS (sin autenticación)
.venv\Scripts\python.exe scripts/download_datasets.py --dataset fitzpatrick17k
.venv\Scripts\python.exe scripts/download_datasets.py --dataset memi-ds

# ACNE04 (espejo HuggingFace, requiere pip install "dermavision[data]")
.venv\Scripts\python.exe scripts/download_datasets.py --dataset acne04-hf

# Roboflow (requiere cuenta gratuita + variable RF_API_KEY)
$env:RF_API_KEY = "tu_clave"
.venv\Scripts\python.exe scripts/download_datasets.py --dataset roboflow --workspace faceinfo --project skin-analysis-v3-jwjcp
```

## Pendientes de gestión humana

1. **Fitzpatrick17k imágenes**: solicitar enlace vía formulario del repo `mattgroh/fitzpatrick17k` (los links originales de DermaAmin están rotos).
2. **ACNE04 original**: descargar del espejo HuggingFace/Kaggle (mismo contenido, sin marca de agua).
3. **Cuenta Roboflow gratuita** para generar `RF_API_KEY`.
