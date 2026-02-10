from matplotlib.layout_engine import LayoutEngine
import numpy as np

from ._fixed_layout import do_fixed_layout, validate_figure, ParamsDict


class FixedLayoutEngine(LayoutEngine):
    _adjust_compatible = False
    _colorbar_gridspec = False

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

    def get(self) -> ParamsDict:
        return self._params

    def execute(self, fig):
        if self._is_executing:
            return
        self._is_executing = True
        validate_figure(fig)
        do_fixed_layout(fig, **self._params)
        self._is_executing = False
