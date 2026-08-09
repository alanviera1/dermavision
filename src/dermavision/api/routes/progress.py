from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["progress"])


@router.get("/progress")
def progress() -> None:
    raise HTTPException(
        status_code=501,
        detail="Comparación temporal pendiente de implementación (Fase 5)",
    )
