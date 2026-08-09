from pathlib import Path

import yaml

from dermavision.api.schemas.analysis import Recommendation

KB_FILES = ("activos", "reglas_bloqueo", "indicaciones", "reglas_climaticas")


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


class RuleEngine:
    def __init__(self, kb_dir: Path) -> None:
        self._kb_dir = kb_dir
        self._kb: dict[str, list[dict]] = {}

    @property
    def kb(self) -> dict[str, list[dict]]:
        return self._kb

    def load(self) -> None:
        for name in KB_FILES:
            path = self._kb_dir / f"{name}.yaml"
            with path.open(encoding="utf-8") as handle:
                self._kb[name] = yaml.safe_load(handle)[name]

    def evaluate(self, metrics: dict, climate: dict, profile: dict) -> Recommendation:
        raise NotImplementedError("Motor de reglas pendiente de implementación (Fase 4)")
