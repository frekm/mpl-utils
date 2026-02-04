from typing import NamedTuple, Any, Type, TypeVar, Generic

import numpy as np

DType = TypeVar("DType")


class Array(np.ndarray, Generic[DType]):
    def __getitem__(self, key) -> DType:
        return super().__getitem__(key)  # type: ignore


class InvalidFigureError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message


class Quadrants(NamedTuple):
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

    top: Any
    right: Any
    bottom: Any
    left: Any

    @property
    def t(self) -> Any:
        """
        Alias for top.
        """
        return self.top

    @property
    def r(self) -> Any:
        """
        Alias for right.
        """
        return self.right

    @property
    def b(self) -> Any:
        """
        Alias for bottom.
        """
        return self.bottom

    @property
    def l(self) -> Any:
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

    def astype(self, t: Type) -> "Quadrants":
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
