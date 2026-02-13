import typing as tp

import numpy as np

DType = tp.TypeVar("DType")

FontsizeLike = tp.Union[
    float,
    tp.Literal[
        "xx-small",
        "x-small",
        "small",
        "medium",
        "large",
        "x-large",
        "xx-large",
        "larger",
        "smaller",
    ],
    None,
]

FONT_SCALINGS: tp.Final = {
    "xx-small": 0.579,
    "x-small": 0.694,
    "small": 0.833,
    "medium": 1.0,
    "large": 1.200,
    "x-large": 1.440,
    "xx-large": 1.728,
    "larger": 1.2,
    "smaller": 0.833,
}


class Array(np.ndarray, tp.Generic[DType]):
    def __getitem__(self, key) -> DType:
        return super().__getitem__(key)  # type: ignore


class Quadrants(tp.NamedTuple):
    """
    Tuple representing the top/right/bottom/left quadrants of a figure.

    Parameters
    ----------
    top, right, bottom, left :
        The value(s) representing the top, right, bottom, left quadrants.

    Attributes
    ----------
    t, r, b, l :
        Alias for top/right/bottom/left.
    """

    top: tp.Any
    right: tp.Any
    bottom: tp.Any
    left: tp.Any

    @property
    def t(self) -> tp.Any:
        """
        Alias for top.
        """
        return self.top

    @property
    def r(self) -> tp.Any:
        """
        Alias for right.
        """
        return self.right

    @property
    def b(self) -> tp.Any:
        """
        Alias for bottom.
        """
        return self.bottom

    @property
    def l(self) -> tp.Any:
        """
        Alias for left.
        """
        return self.left

    def __neg__(self) -> "Quadrants":
        return Quadrants(*[-el for el in self])

    def __add__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] + val[i] for i in range(4)])
        return Quadrants(*[el + val for el in self])

    def __radd__(self, val) -> "Quadrants":
        return self + val

    def __sub__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] - val[i] for i in range(4)])
        return Quadrants(*[el - val for el in self])

    def __rsub__(self, val) -> "Quadrants":
        return self - val

    def __mul__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] * val[i] for i in range(4)])
        return Quadrants(*[el * val for el in self])

    def __rmul__(self, val) -> "Quadrants":
        return self * val

    def __truediv__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] / val[i] for i in range(4)])
        return Quadrants(*[el / val for el in self])

    def __rtruediv__(self, val) -> "Quadrants":
        return self / val

    def __floordiv__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] // val[i] for i in range(4)])
        return Quadrants(*[el // val for el in self])

    def __rfloordiv__(self, val) -> "Quadrants":
        return self // val

    def astype(self, t: tp.Type) -> "Quadrants":
        """
        Convert elements to type `t`

        Examples
        --------
        ::

            >>> quadrants = mplu.Quadrants(1.0, 1.0, 1.0, 1.0)
            >>> quadrants
            Quadrants(top=1.0, right=1.0, bottom=1.0, left=1.0)
            >>> quadrants.astype(int)
            Quadrants(top=1, right=1, bottom=1, left=1)
        """
        return Quadrants(*[t(el) for el in self])


def convert_to_inches(val: float, unit: tp.Literal["inch", "pts", "mm"]) -> float:
    if unit == "inch":
        return val
    if unit == "pts":
        return val / 72.0
    if unit == "mm":
        return val / 25.4
    valid_units = "inch", "pts", "mm"
    raise ValueError(f"{unit=}, but it must be one of {valid_units}")
