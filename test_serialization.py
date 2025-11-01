import os
import numpy as np

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-cache")

from app import convert_to_native_types


def test_convert_to_native_types_sanitizes_non_finite_values():
    payload = {
        "array": np.array([1.0, np.nan, np.inf, -np.inf]),
        "np_float": np.float64(np.nan),
        "py_float": float("nan"),
        "list": [np.nan, 2.5, -np.inf],
    }

    converted = convert_to_native_types(payload)

    assert converted["array"] == [1.0, None, None, None]
    assert converted["np_float"] is None
    assert converted["py_float"] is None
    assert converted["list"] == [None, 2.5, None]
