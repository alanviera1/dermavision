import math

FITZPATRICK_BOUNDS: tuple[tuple[float, int], ...] = (
    (55.0, 1),
    (41.0, 2),
    (28.0, 3),
    (10.0, 4),
    (-30.0, 5),
)


def ita(l_star: float, b_star: float) -> float:
    return math.degrees(math.atan2(l_star - 50.0, b_star))


def fitzpatrick_type(ita_value: float) -> int:
    for lower_bound, skin_type in FITZPATRICK_BOUNDS:
        if ita_value > lower_bound:
            return skin_type
    return 6
