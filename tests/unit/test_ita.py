import pytest

from dermavision.modules.vision.ita import fitzpatrick_type, ita


def test_ita_light_skin_is_positive_and_large() -> None:
    assert ita(l_star=70.0, b_star=10.0) > 55.0


def test_ita_math() -> None:
    assert ita(l_star=60.0, b_star=10.0) == pytest.approx(45.0)
    assert ita(l_star=60.0, b_star=0.0) == pytest.approx(90.0)


def test_fitzpatrick_ranges() -> None:
    assert fitzpatrick_type(60.0) == 1
    assert fitzpatrick_type(50.0) == 2
    assert fitzpatrick_type(35.0) == 3
    assert fitzpatrick_type(20.0) == 4
    assert fitzpatrick_type(0.0) == 5
    assert fitzpatrick_type(-40.0) == 6


def test_fitzpatrick_boundaries() -> None:
    assert fitzpatrick_type(55.0) == 2
    assert fitzpatrick_type(41.0) == 3
    assert fitzpatrick_type(-30.0) == 6
