import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backend_bases import RendererBase
from matplotlib.axes import Axes
from matplotlib.transforms import Bbox
from matplotlib.gridspec import SubplotSpec
import numpy as np
from numpy.typing import NDArray, ArrayLike

from typing import TypedDict, Unpack, Final
import logging

from . import utils

# from .fixed_layout_engine import FixedAxesLayoutEngine


PTS_PER_INCH: Final = 72.0

logger = logging.getLogger(__name__)


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
    hpads: np.ndarray[tuple[int], np.dtype[np.float64]]
    hpads_use_bbox: np.ndarray[tuple[int], np.dtype[np.bool]]
    vpads: np.ndarray[tuple[int], np.dtype[np.float64]]
    vpads_use_bbox: np.ndarray[tuple[int], np.dtype[np.bool]]
    max_figwidth: float


class ParamsDict(TypedDict, total=True):
    margin_pads_pts: (
        float
        | tuple[float, float]
        | tuple[float, float, float]
        | tuple[float, float, float, float]
    )
    margin_pads_ignore_labels: (
        bool
        | tuple[bool, bool]
        | tuple[bool, bool, bool]
        | tuple[bool, bool, bool, bool]
    )
    col_pads_pts: float | tuple[float, ...]
    col_pads_ignore_labels: bool | tuple[bool, ...]
    row_pads_pts: float | tuple[float, ...]
    row_pads_ignore_labels: bool | tuple[bool, ...]
    max_figwidth: float


class Layouter:
    def __init__(self, fig: Figure, **params: Unpack[ParamsDict]) -> None:
        self._fig = self._validate_figure(fig)

        # fig.canvas.draw()
        self._renderer = fig._get_renderer()
        self._params = params
        self._axes_grid = self._get_axes_grid(self._get_axes_for_layout())
        self._caxes_grid = self._get_caxes_grid()
        self._nparams = self._normalize_layout_params()

    def execute(self) -> None:
        bboxes = self._get_bboxes_grid()
        caxes_bboxes = self._get_caxes_bboxes_grid()

        for _ in range(2):
            tbboxes = self._get_tbboxes_grid()

            hpads_now = self._get_hspaces(bboxes, tbboxes)
            vpads_now = self._get_vspaces(bboxes, tbboxes)

            hdeltas = self._nparams["hpads"] - hpads_now
            for i, hdelta in enumerate(hdeltas):
                self._add_hspace(i, hdelta, bboxes, caxes_bboxes)
                bboxes = self._get_bboxes_grid()
                caxes_bboxes = self._get_caxes_bboxes_grid()

            vdeltas = self._nparams["vpads"] - vpads_now
            for i, vdelta in enumerate(vdeltas):
                self._add_vspace(i, vdelta, bboxes, caxes_bboxes)
                bboxes = self._get_bboxes_grid()
                caxes_bboxes = self._get_caxes_bboxes_grid()

        fw = self._fig.get_size_inches()[0]
        if fw > self._nparams["max_figwidth"]:
            msg = f"figure size ({fw}in) larger than max_figwidth ({self._nparams['max_figwidth']}in)"
            raise utils.InvalidFigureError(msg)

    @property
    def nrows(self) -> int:
        return self._axes_grid.shape[0]

    @property
    def ncols(self) -> int:
        return self._axes_grid.shape[1]

    def _validate_figure(self, fig) -> Figure:
        if not isinstance(fig, Figure):
            raise utils.InvalidFigureError("figure must be matplotlib.figure.Figure")
        gs = None
        for ax in self._get_axes_in_figure(fig):
            ss = ax.get_subplotspec()
            if ss is None:
                continue
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
        return fig

    def _get_axes_in_figure(self, fig) -> list[Axes]:
        try:
            axes = getattr(fig, "_localaxes")
        finally:
            axes = fig.axes
        return axes

    def _norm_margins(self, arg: ArrayLike) -> utils.Quadrants:
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

    def _norm_hv_space(self, vals: ArrayLike, n: int) -> NDArray:
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

    def _normalize_layout_params(self) -> NormParamsDict:
        mpads_inch = self._norm_margins(self._params["margin_pads_pts"]) / PTS_PER_INCH
        mpads_use_bbox = self._norm_margins(self._params["margin_pads_ignore_labels"])
        hpads_inch = (
            self._norm_hv_space(self._params["col_pads_pts"], self.ncols) / PTS_PER_INCH
        )
        hpads_use_bbox = self._norm_hv_space(
            self._params["col_pads_ignore_labels"], self.ncols
        )
        vpads_inch = (
            self._norm_hv_space(self._params["row_pads_pts"], self.nrows) / PTS_PER_INCH
        )
        vpads_use_bbox = self._norm_hv_space(
            self._params["row_pads_ignore_labels"], self.nrows
        )

        nparams: NormParamsDict = {
            "hpads": np.array((mpads_inch.l, *hpads_inch, mpads_inch.r)),
            "hpads_use_bbox": np.array(
                (mpads_use_bbox.l, *hpads_use_bbox, mpads_use_bbox.r)
            ),
            "vpads": np.array((mpads_inch.t, *vpads_inch, mpads_inch.b)),
            "vpads_use_bbox": np.array(
                (mpads_use_bbox.t, *vpads_use_bbox, mpads_use_bbox.b)
            ),
            "max_figwidth": float(self._params["max_figwidth"]),
        }
        return nparams

    def _get_axes_for_layout(self) -> list[Axes]:
        axes_for_layout = []
        for ax in self._get_axes_in_figure(self._fig):
            ss = ax.get_subplotspec()
            if ss is None:
                continue
            axes_for_layout.append(ax)
        return axes_for_layout

    def _get_axes_grid(self, axes_in_layout: list[Axes]) -> utils.Array[Axes]:
        subplotspecs: dict[Axes, SubplotSpec] = {}
        first = True
        for ax in axes_in_layout:
            ss = ax.get_subplotspec()
            subplotspecs[ax] = ss
            if first:
                first = False
                gridspec = ss.get_gridspec()
                nrows, ncols = gridspec.get_geometry()

        axes_grid = np.empty((nrows, ncols), dtype=Axes)

        for i, _ in np.ndenumerate(axes_grid):
            for ax in axes_in_layout:
                if subplotspecs[ax] == gridspec[i]:
                    axes_grid[i] = ax

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"got a grid {axes_grid.shape}")
            for (row, col), ax in np.ndenumerate(axes_grid):
                logger.debug(f"{(row,col)}: {ax.get_label()}")

        return axes_grid  # type: ignore

    def _get_bbox(self, ax: Axes) -> Bbox:
        fw, fh = self._fig.get_size_inches()
        pos = ax.get_position()
        return Bbox.from_extents(pos.x0 * fw, pos.y0 * fh, pos.x1 * fw, pos.y1 * fh)

    def _get_bboxes_grid(self) -> utils.Array[Bbox]:
        bboxes = np.empty_like(self._axes_grid, dtype=object)
        for i, ax in np.ndenumerate(self._axes_grid):
            bboxes[i] = self._get_bbox(ax)
        return bboxes

    def _get_tbboxes(self, ax) -> Bbox:
        dpi = self._fig.dpi
        tbbox_ax = ax.get_tightbbox(self._renderer, for_layout_only=False)

        xy_candidates = utils.Quadrants(
            [tbbox_ax.y1], [tbbox_ax.x1], [tbbox_ax.y0], [tbbox_ax.x0]
        )

        for cax in ax._colorbars:
            tbbox_cb = cax.get_tightbbox(self._renderer)
            location = cax._colorbar_info["location"]
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

    def _get_tbboxes_grid(self) -> utils.Array[Bbox]:
        tbboxes = np.empty_like(self._axes_grid, dtype=object)
        for i, ax in np.ndenumerate(self._axes_grid):
            tbboxes[i] = self._get_tbboxes(ax)
        return tbboxes

    def _get_caxes_grid(self) -> list[list[list[Axes]]]:
        caxes = []
        for axs_in_row in self._axes_grid:
            caxes.append([])
            for ax in axs_in_row:
                cax = ax._colorbars
                if cax and cax in caxes:
                    msg = "Cannot handle colorbars that are attached to multiple axes"
                    raise utils.InvalidFigureError(msg)
                caxes[-1].append(cax)
        return caxes

    def _get_caxes_bboxes_grid(self) -> list[list[list[Bbox]]]:
        return [
            [[self._get_bbox(ax) for ax in caxes] for caxes in caxes_row]
            for caxes_row in self._caxes_grid
        ]

    def _select_box(self, use_bbox: bool, bboxes: NDArray, tbboes: NDArray) -> NDArray:
        return bboxes if use_bbox else tbboes

    def _get_hspaces(
        self, bboxes: utils.Array[Bbox], tbboxes: utils.Array[Bbox]
    ) -> NDArray[np.float64]:
        use_bbox = self._nparams["hpads_use_bbox"]
        nspaces = len(use_bbox)
        hpads = np.empty(nspaces, dtype=float)

        first_bboxes = self._select_box(use_bbox[0], bboxes, tbboxes)[:, 0]
        hpads[0] = np.amin([t.x0 for t in first_bboxes])

        for i in range(1, nspaces - 1):
            left_bboxes = self._select_box(use_bbox[i], bboxes, tbboxes)[:, i]
            right_bboxes = self._select_box(use_bbox[i], bboxes, tbboxes)[:, i - 1]
            left = np.amin([t.x0 for t in left_bboxes])
            right = np.amax([t.x1 for t in right_bboxes])
            hpads[i] = left - right

        last_bboxes = self._select_box(use_bbox[-1], bboxes, tbboxes)[:, -1]
        fw = self._fig.get_size_inches()[0]
        hpads[-1] = fw - np.amax([t.x1 for t in last_bboxes])

        return hpads

    def _get_vspaces(
        self, bboxes: utils.Array[Bbox], tbboxes: utils.Array[Bbox]
    ) -> NDArray[np.float64]:
        use_bbox = self._nparams["vpads_use_bbox"]
        nspaces = len(use_bbox)
        vpads_inch = np.empty(nspaces, dtype=float)

        first_bboxes = self._select_box(use_bbox[0], bboxes, tbboxes)[0]
        fh = self._fig.get_size_inches()[1]
        vpads_inch[0] = fh - np.amax([t.y1 for t in first_bboxes])

        for i in range(1, nspaces - 1):
            top_bboxes = self._select_box(use_bbox[i], bboxes, tbboxes)[i]
            bottom_bboxes = self._select_box(use_bbox[i], bboxes, tbboxes)[i - 1]
            top = np.amax([t.y1 for t in top_bboxes])
            bottom = np.amin([t.y0 for t in bottom_bboxes])
            vpads_inch[i] = bottom - top

        last_bboxes = self._select_box(use_bbox[-1], bboxes, tbboxes)[-1]
        vpads_inch[-1] = np.amin([t.y0 for t in last_bboxes])

        return vpads_inch

    def _add_vspace(self, idx, space, axes_bboxes, caxes_bboxes):
        fw_old, fh_old = self._fig.get_size_inches()
        fh_new = fh_old + space
        self._fig.set_size_inches(fw_old, fh_new, forward=True)

        for (row, col), ba in np.ndenumerate(axes_bboxes):
            shift = 0.0 if row >= idx else space
            bbox_new = Bbox.from_bounds(ba.x0, ba.y0 + shift, ba.width, ba.height)
            self._set_axes_position(bbox_new, self._axes_grid[row, col])
            for i, bc in enumerate(caxes_bboxes[row][col]):
                bbox_new = Bbox.from_bounds(bc.x0, bc.y0 + shift, bc.width, bc.height)
                self._set_axes_position(bbox_new, self._caxes_grid[row][col][i])

    def _add_hspace(self, idx, space, axes_bboxes, caxes_bboxes):
        fw_old, fh_old = self._fig.get_size_inches()
        fw_new = fw_old + space
        self._fig.set_size_inches(fw_new, fh_old, forward=True)

        for (row, col), ba in np.ndenumerate(axes_bboxes):
            shift = 0.0 if col < idx else space
            bbox_new = Bbox.from_bounds(ba.x0 + shift, ba.y0, ba.width, ba.height)
            self._set_axes_position(bbox_new, self._axes_grid[row, col])
            for i, bc in enumerate(caxes_bboxes[row][col]):
                bbox_new = Bbox.from_bounds(bc.x0 + shift, bc.y0, bc.width, bc.height)
                self._set_axes_position(bbox_new, self._caxes_grid[row][col][i])

    def _set_axes_position(self, bbox: Bbox, ax: Axes):
        fw, fh = self._fig.get_size_inches()
        bbox_figcoords = Bbox.from_extents(
            bbox.x0 / fw, bbox.y0 / fh, bbox.x1 / fw, bbox.y1 / fh
        )
        ax.set_position(bbox_figcoords)
