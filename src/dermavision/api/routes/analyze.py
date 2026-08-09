from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["analyze"])


@router.post("/analyze")
def analyze() -> None:
    raise HTTPException(
        status_code=501,
        detail="Análisis pendiente de implementación (Fases 1-4)",
    )
