from pathlib import Path

from dermavision.modules.rules.engine import KB_FILES, RuleEngine

REQUIRED_ACTIVO_FIELDS = {
    "inci",
    "mecanismo",
    "concentracion_minima_eficaz",
    "concentracion_maxima_segura",
    "fotosensibilidad",
    "categoria_embarazo",
    "incompatibilidades",
    "evidencia",
}


def test_kb_files_exist_and_parse(kb_dir: Path) -> None:
    engine = RuleEngine(kb_dir)
    engine.load()
    for name in KB_FILES:
        assert name in engine.kb
        assert isinstance(engine.kb[name], list)
        assert len(engine.kb[name]) > 0


def test_activos_have_required_fields(kb_dir: Path) -> None:
    engine = RuleEngine(kb_dir)
    engine.load()
    for activo in engine.kb["activos"]:
        assert REQUIRED_ACTIVO_FIELDS.issubset(activo.keys())
        assert activo["concentracion_minima_eficaz"] <= activo["concentracion_maxima_segura"]
        assert isinstance(activo["fotosensibilidad"], bool)
        assert isinstance(activo["evidencia"], list)
