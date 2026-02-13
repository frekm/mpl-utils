import typing as tp

import numpy as np
from matplotlib.transforms import Bbox

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


def get_ax_bbox_inch(fig, ax) -> Bbox:
    fw, fh = fig.get_size_inches()
    bbox = ax.get_position()
    return Bbox([[bbox.x0 * fw, bbox.y0 * fh], [bbox.x1 * fw, bbox.y1 * fh]])


def get_ax_tbbox_inch(fig, ax, renderer) -> Bbox:
    dpi = fig.dpi
    tbbox_ax = ax.get_tightbbox(renderer, for_layout_only=False)

    xy_candidates = Quadrants(
        [tbbox_ax.y1], [tbbox_ax.x1], [tbbox_ax.y0], [tbbox_ax.x0]
    )

    for cb in ax._colorbars:
        tbbox_cb = cb.get_tightbbox(renderer)
        location = cb._colorbar_info["location"]
        if location == "left":
            xy_candidates.left.append(tbbox_cb.x0)
            xy_candidates.top.append(tbbox_cb.y1)
            xy_candidates.bottom.append(tbbox_cb.y0)
        if location == "right":
            xy_candidates.right.append(tbbox_cb.x1)
            xy_candidates.top.append(tbbox_cb.y1)
            xy_candidates.bottom.append(tbbox_cb.y0)
        if location == "top":
            xy_candidates.top.append(tbbox_cb.y1)
            xy_candidates.left.append(tbbox_cb.x0)
            xy_candidates.right.append(tbbox_cb.x1)
        if location == "bottom":
            xy_candidates.bottom.append(tbbox_cb.y0)
            xy_candidates.left.append(tbbox_cb.x0)
            xy_candidates.right.append(tbbox_cb.x1)

    relevant_xy = (
        np.min([x0 / dpi for x0 in xy_candidates.left]),
        np.min([y0 / dpi for y0 in xy_candidates.bottom]),
        np.max([x1 / dpi for x1 in xy_candidates.right]),
        np.max([y1 / dpi for y1 in xy_candidates.top]),
    )

    rtn = Bbox.from_extents(*relevant_xy)
    return rtn
