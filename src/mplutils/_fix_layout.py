import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure, SubFigure
from matplotlib.backend_bases import RendererBase
from matplotlib.axes import Axes
from matplotlib.transforms import Bbox
import numpy as np
from numpy.typing import NDArray, ArrayLike

from typing import TypedDict, Unpack, Final

from . import utils


PTS_PER_INCH: Final = 72.0


def get_renderer(fig) -> RendererBase:
    """
    from https://stackoverflow.com/a/78560455
    """
    if hasattr(fig.canvas, "get_renderer"):
        return fig.canvas.get_renderer()
    elif hasattr(fig, "_get_renderer"):
        return fig._get_renderer()
    backend = matplotlib.get_backend()
    raise AttributeError(f"Could not find a renderer for the '{backend}' backend.")


class NormParamsDict(TypedDict, total=True):
    hpads: tuple[float, ...]
    hpads_use_bbox: tuple[bool, ...]
    vpads: tuple[float, ...]
    vpads_use_bbox: tuple[bool, ...]
    max_figwidth: float
    fix_figwidth: bool
    min_runs: int
    max_runs: int


class ParamsDict(TypedDict, total=False):
    fix_figwidth: bool
    margin_pad_pts: (
        float
        | tuple[float, float]
        | tuple[float, float, float]
        | tuple[float, float, float, float]
    )
    margin_pad_ignore_labels: (
        bool
        | tuple[bool, bool]
        | tuple[bool, bool, bool]
        | tuple[bool, bool, bool, bool]
    )
    col_pad_pts: float | tuple[float, ...]
    col_pad_ignores_labels: bool | tuple[bool, ...]
    row_pad_pts: float | tuple[float, ...]
    row_pad_ignores_labels: bool | tuple[bool, ...]
    max_figwidth: float
    min_runs: int
    max_runs: int


class Layouter:
    def __init__(self, fig: Figure, **params: Unpack[ParamsDict]) -> None:
        self._fig = self.validate_figure(fig)
        fig.canvas.draw()
        self._params = params
        self._renderer = get_renderer(fig)
        self._axes_grid = self.get_axes_grid(self.get_axes_for_layout(fig._localaxes))
        self._nrows, self._ncols = self._axes_grid.shape

    def validate_figure(self, fig) -> Figure:
        if isinstance(fig, SubFigure):
            raise utils.InvalidFigureError(
                "FixedLayoutEngine cannot handle nested figures"
            )
        gs = None
        for ax in fig._localaxes:
            if not ax.get_subplotspec():
                continue
            ss = ax.get_subplotspec()
            gs_ = ss.get_gridspec()
            if ss.num1 != ss.num2:
                msg = "Cannot handle axes spanning multiple cells in a gridspec"
                raise utils.InvalidFigureError(msg)
            if gs is None:
                gs = gs_
            elif gs_ != gs:
                msg = "FixedLayoutEngine cannot handle multiple gridspecs in figure"
                raise utils.InvalidFigureError(msg)
        if gs is None:
            raise utils.InvalidFigureError(
                "Axes in figure need to be part of a gridspec"
            )
        if not isinstance(fig, Figure):
            raise ValueError("No figure")
        return fig

    def normalize_margins(self, arg: ArrayLike) -> utils.Quadrants:
        """
        Processes arguments that represent margins of a figure.

        Parameters
        ----------
        arg : array_like
            1 value:
                (top, right, bottom, left)
            2 values:
                (top, bottom), (right, left)
            3 values:
                top, (right, left), bottom
            4 values:
                top, right, bottom, left
        """
        arg = np.asarray(arg)
        if not arg.ndim > 0:
            rtn = utils.Quadrants(arg, arg, arg, arg)
        elif len(arg) == 1:
            rtn = utils.Quadrants(arg[0], arg[0], arg[0], arg[0])
        elif len(arg) == 2:
            rtn = utils.Quadrants(arg[0], arg[1], arg[0], arg[1])
        elif len(arg) == 3:
            rtn = utils.Quadrants(arg[0], arg[1], arg[2], arg[1])
        elif len(arg) == 4:
            rtn = utils.Quadrants(*arg)
        else:
            raise ValueError(f"{arg=} has invalid length")
        return rtn

    def normalize_hv_pads(vals: ArrayLike, n: int) -> NDArray:
        """
        Process arguments that are 'row/col'-like.

        Parameters
        ----------
        vals : array_like
            Values corresponding to the respective column/row.

            value:
                Global for all rows/cols.

            (value, ...)
                values corresponding to each row/col. Must have length `n`.

        n : int
            Number of rows/columns.

        Returns
        -------
        values : ndarray
            Array of length `n`.
        """
        vals = np.asarray(vals)
        if not vals.ndim > 0:
            vals = np.array([vals] * (n - 1))
        elif len(vals) != n - 1:
            raise ValueError(f"{vals=}, but must be scalar or of length {n-1}")
        return vals

    def normalize_layout_params(
        params: ParamsDict, nrows: int, ncols: int
    ) -> NormParamsDict:

        defaults: ParamsDict = {
            "fix_figwidth": False,
            "margin_pad_pts": 3.0,
            "margin_pad_ignore_labels": False,
            "col_pad_pts": 10.0,
            "col_pad_ignores_labels": False,
            "row_pad_pts": 10.0,
            "row_pad_ignores_labels": False,
            "max_figwidth": np.inf,
            "min_runs": 2,
            "max_runs": 5,
        }

        params_ = {**defaults, **params}

        mpads_inch = normalize_margins(params_["margin_pads_pts"]) / PTS_PER_INCH
        mpads_use_bbox = normalize_margins(params_["margin_pads_ignore_labels"])
        hpads_inch = normalize_hv_pads(params_["col_pads_pts"], ncols) / PTS_PER_INCH
        hpads_use_bbox = normalize_hv_pads(params_["col_pads_ignore_labels"], ncols)
        vpads_inch = normalize_hv_pads(params_["row_pads_pts"], nrows) / PTS_PER_INCH
        vpads_use_bbox = normalize_hv_pads(params_["row_pads_ignore_labels"], nrows)

        nparams: NormParamsDict = {
            "hpads": (mpads_inch.l, *hpads_inch, mpads_inch.r),
            "hpads_use_bbox": (mpads_use_bbox.l, *hpads_use_bbox, mpads_use_bbox.r),
            "vpads": (mpads_inch.t, *vpads_inch, mpads_inch.b),
            "vpads_use_bbox": (mpads_use_bbox.t, *vpads_use_bbox, mpads_use_bbox.b),
            "max_figwidth": float(params_["max_figwidth"]),
            "min_runs": int(params_["min_runs"]),
            "max_runs": int(params_["max_runs"]),
            "fix_figwidth": bool(params_["fix_figwdith"]),
        }

        return nparams

    def get_axes_for_layout(axes_in_figure: list[Axes]) -> list[Axes]: ...

    def get_axes_grid(axes_in_layout: list[Axes]) -> utils.Array[Axes]: ...

    def get_bboxes_grid(
        fig: Figure, axes_grid: utils.Array[Axes]
    ) -> utils.Array[Bbox]: ...

    def get_tbboxes_grid(
        fig: Figure, axes_grid: utils.Array[Axes], renderer: RendererBase
    ) -> utils.Array[Bbox]: ...

    def get_caxes_grid(axes_grid: utils.Array[Axes]) -> list[list[list[Axes]]]: ...

    def get_caxes_bboxes_grid(
        fig: Figure, caxes_grid: list[list[list[Axes]]]
    ) -> list[list[list[Bbox]]]: ...

    def get_hspaces(
        use_bbox: tuple[bool, ...],
        bboxes: utils.Array[Bbox],
        tbboxes: utils.Array[Bbox],
    ) -> NDArray[np.float64]: ...

    def get_vspaces(
        use_bbox: tuple[bool, ...],
        bboxes: utils.Array[Bbox],
        tbboxes: utils.Array[Bbox],
    ) -> NDArray[np.float64]: ...

    def add_hspace(
        fig, idx, space, axes_grid, axes_bboxes, caxes_grid, caxes_bboxes
    ): ...
    def add_vspace(
        fig, idx, space, axes_grid, axes_bboxes, caxes_grid, caxes_bboxes
    ): ...
