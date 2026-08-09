from hypothesis import given
from hypothesis import strategies as st

from dermavision.modules.rules.engine import clamp


@given(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1000.0, max_value=1000.0),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1000.0, max_value=1000.0),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1000.0, max_value=1000.0),
)
def test_clamp_stays_within_bounds(value: float, a: float, b: float) -> None:
    low, high = sorted((a, b))
    result = clamp(value, low, high)
    assert low - 1e-9 <= result <= high + 1e-9
