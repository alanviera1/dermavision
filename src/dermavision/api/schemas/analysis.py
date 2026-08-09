from pydantic import BaseModel, Field


class SkinMetrics(BaseModel):
    hyperpigmentation_pct: float = Field(ge=0.0, le=100.0)
    erythema_pct: float = Field(ge=0.0, le=100.0)
    open_comedones: int = Field(ge=0)
    closed_comedones: int = Field(ge=0)
    papules: int = Field(ge=0)
    pustules: int = Field(ge=0)
    ita_angle: float
    fitzpatrick_type: int = Field(ge=1, le=6)
    confidence: float = Field(ge=0.0, le=1.0)


class ClimateContext(BaseModel):
    temperature_c: float
    relative_humidity_pct: float = Field(ge=0.0, le=100.0)
    uv_index_now: float = Field(ge=0.0)
    uv_index_max_today: float = Field(ge=0.0)
    source: str = "open-meteo"


class ActiveIngredient(BaseModel):
    inci: str
    concentration: float
    frequency: str
    moment: str
    phase: str
    evidence_refs: list[str]


class Recommendation(BaseModel):
    ingredients: list[ActiveIngredient]
    blocked: list[str]
    reasons: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
