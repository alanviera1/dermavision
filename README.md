# Dermavision

Sistema Experto de Análisis Dermocosmético Cuantitativo.

Analiza fotografías faciales con métricas cuantitativas (hiperpigmentación, acné, eritema), las cruza con el contexto climático en tiempo real (temperatura, humedad, índice UV) y prescribe activos químicos puros con concentración mediante un motor de reglas determinista, bloqueando combinaciones peligrosas. 100% capas gratuitas y open-source.

Documentación completa: [docs/PLAN.md](docs/PLAN.md).

## Stack

- Backend: Python 3.11 + FastAPI + SQLAlchemy/Alembic
- Visión: OpenCV, scikit-image, PyTorch, YOLOv8n, U-Net, MediaPipe (extra opcional `vision`)
- Clima: Open-Meteo (gratis, sin API key)
- BD: Supabase (dev local: PostgreSQL vía Docker Compose)
- Frontend (Fase 5): PWA React + Vite

## Inicio rápido

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d             # PostgreSQL local de desarrollo
uvicorn dermavision.main:app --reload
```

## Verificación

```bash
ruff check .
ruff format --check .
pytest
```

## Estructura

```
src/dermavision/
├── api/          # rutas FastAPI + contratos Pydantic
├── modules/
│   ├── vision/   # Módulo A: estandarización de imagen y métricas
│   ├── climate/  # Módulo B: contexto ambiental (Open-Meteo)
│   ├── rules/    # Módulo C: base de conocimiento y motor de reglas
│   └── tracking/ # Módulo D: perfiles, snapshots y comparación temporal
├── presentation/ # capa LLM opcional validada
└── db/           # modelos SQLAlchemy + migraciones Alembic
```

Los extras `vision`, `data` y `presentation` se instalan solo si se necesitan:
`pip install -e ".[dev,vision]"`.
