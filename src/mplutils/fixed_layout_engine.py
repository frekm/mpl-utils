from matplotlib.layout_engine import LayoutEngine
import numpy as np

from ._fixed_layout import Layouter, ParamsDict


class FixedLayoutEngine(LayoutEngine):
    _colorbar_gridspec = False
    _adjust_compatible = False

    def __init__(
        self,
        margin_pads_pts: (
            float
            | tuple[float, float]
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ) = 3.0,
        margin_pads_ignore_labels: (
            bool
            | tuple[bool, bool]
            | tuple[bool, bool, bool]
            | tuple[bool, bool, bool, bool]
        ) = False,
        col_pads_pts: float | tuple[float, ...] = 10.0,
        col_pads_ignore_labels: bool | tuple[bool, ...] = False,
        row_pads_pts: float | tuple[float, ...] = 10.0,
        row_pads_ignore_labels: bool | tuple[bool, ...] = False,
        max_figwidth: float = np.inf,
    ):
        self.margin_pad_pts = margin_pads_pts
        self.margin_pads_pts = margin_pads_pts
        self.margin_pads_ignore_labels = margin_pads_ignore_labels
        self.col_pads_pts = col_pads_pts
        self.col_pads_ignore_labels = col_pads_ignore_labels
        self.row_pads_pts = row_pads_pts
        self.row_pads_ignore_labels = row_pads_ignore_labels
        self.max_figwidth = max_figwidth

        self._params: ParamsDict = {
            "margin_pads_pts": margin_pads_pts,
            "margin_pads_ignore_labels": margin_pads_ignore_labels,
            "col_pads_pts": col_pads_pts,
            "col_pads_ignore_labels": col_pads_ignore_labels,
            "row_pads_pts": row_pads_pts,
            "row_pads_ignore_labels": row_pads_ignore_labels,
            "max_figwidth": max_figwidth,
        }

        self._is_executing = False

    def get(self) -> ParamsDict:
        return self._params

    def set(
        self,
        margin_pads_pts: (
            float
            | tuple[float, float]
            | tuple[float, float, float]
            | tuple[float, float, float, float]
            | None
        ) = None,
        margin_pads_ignore_labels: (
            bool
            | tuple[bool, bool]
            | tuple[bool, bool, bool]
            | tuple[bool, bool, bool, bool]
            | None
        ) = None,
        col_pads_pts: float | tuple[float, ...] | None = None,
        col_pads_ignore_labels: bool | tuple[bool, ...] | None = None,
        row_pads_pts: float | tuple[float, ...] | None = None,
        row_pads_ignore_labels: bool | tuple[bool, ...] | None = None,
        max_figwidth: float | None = None,
    ):
        for td in self.set.__kwdefaults__:  # type: ignore
            if locals()[td] is not None:
                self._params[td] = locals()[td]

    def execute(self, fig):
        if self._is_executing:
            return

        self._is_executing = True

        layouter = Layouter(fig, **self._params)
        layouter.execute()

        self._is_executing = False
