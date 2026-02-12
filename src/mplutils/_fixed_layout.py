from matplotlib.figure import Figure, SubFigure
from matplotlib.axes import Axes
from matplotlib.gridspec import SubplotSpec
from matplotlib.transforms import Bbox
import numpy as np
from numpy.typing import NDArray, ArrayLike

import logging
from typing import cast, TypedDict, Unpack

from . import core
from . import errors
from .constants import PTS_PER_INCH


logger = logging.getLogger(__name__)


def normalize_margins(arg: ArrayLike) -> core.Quadrants:
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
        rtn = core.Quadrants(arg, arg, arg, arg)
    elif len(arg) == 1:
        rtn = core.Quadrants(arg[0], arg[0], arg[0], arg[0])
    elif len(arg) == 2:
        rtn = core.Quadrants(arg[0], arg[1], arg[0], arg[1])
    elif len(arg) == 3:
        rtn = core.Quadrants(arg[0], arg[1], arg[2], arg[1])
    elif len(arg) == 4:
        rtn = core.Quadrants(*arg)
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


class NormParamsDict(TypedDict, total=True):
    hpads_inch: tuple[float, ...]
    hpads_use_bbox: tuple[bool, ...]
    vpads_inch: tuple[float, ...]
    vpads_use_bbox: tuple[bool, ...]
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


def normalize_layout_params(
    params: ParamsDict, nrows: int, ncols: int
) -> NormParamsDict:
    mpads_inch = normalize_margins(params["margin_pads_pts"]) / PTS_PER_INCH
    mpads_use_bbox = normalize_margins(params["margin_pads_ignore_labels"])
    hpads_inch = normalize_hv_pads(params["col_pads_pts"], ncols) / PTS_PER_INCH
    hpads_use_bbox = normalize_hv_pads(params["col_pads_ignore_labels"], ncols)
    vpads_inch = normalize_hv_pads(params["row_pads_pts"], nrows) / PTS_PER_INCH
    vpads_use_bbox = normalize_hv_pads(params["row_pads_ignore_labels"], nrows)

    nparams: NormParamsDict = {
        "hpads_inch": (mpads_inch.l, *hpads_inch, mpads_inch.r),
        "hpads_use_bbox": (mpads_use_bbox.l, *hpads_use_bbox, mpads_use_bbox.r),
        "vpads_inch": (mpads_inch.t, *vpads_inch, mpads_inch.b),
        "vpads_use_bbox": (mpads_use_bbox.t, *vpads_use_bbox, mpads_use_bbox.b),
        "max_figwidth": float(params["max_figwidth"]),
    }
    return nparams


def validate_figure(fig):
    if isinstance(fig, SubFigure):
        raise errors.InvalidFigureError(
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
            raise errors.InvalidFigureError(msg)
        if gs is None:
            gs = gs_
        elif gs_ != gs:
            msg = "FixedLayoutEngine cannot handle multiple gridspecs in figure"
            raise errors.InvalidFigureError(msg)
    if gs is None:
        raise errors.InvalidFigureError("Axes in figure need to be part of a gridspec")


def get_axes_for_layout(axes: list[Axes]) -> list[Axes]:
    axes_for_layout = []
    for ax in axes:
        ss = ax.get_subplotspec()
        if ss is None:
            continue
        axes_for_layout.append(ax)
    return axes_for_layout


def get_ax_bbox_inch(fig, ax) -> Bbox:
    fw, fh = fig.get_size_inches()
    bbox = ax.get_position()
    return Bbox([[bbox.x0 * fw, bbox.y0 * fh], [bbox.x1 * fw, bbox.y1 * fh]])


def get_ax_tbbox_inch(fig, ax, renderer) -> Bbox:
    dpi = fig.dpi
    tbbox_ax = ax.get_tightbbox(renderer, for_layout_only=False)

    xy_candidates = core.Quadrants(
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


def get_bboxes_inch_grid(fig, axs) -> core.Array[Bbox]:
    bboxes_inch = np.empty_like(axs, dtype=Bbox)
    for i, ax in np.ndenumerate(axs):
        bboxes_inch[i] = get_ax_bbox_inch(fig, ax)
    return bboxes_inch  # type: ignore


def get_tbboxes_inch_grid(fig, axs, renderer) -> core.Array[Bbox]:
    tbboxes_inch = np.empty_like(axs, dtype=Bbox)
    for i, ax in np.ndenumerate(axs):
        tbboxes_inch[i] = get_ax_tbbox_inch(fig, ax, renderer)
    return tbboxes_inch  # type: ignore


def get_axes_grid(axes: list[Axes]) -> core.Array[Axes]:
    subplotspecs: dict[Axes, SubplotSpec] = {}
    first = True
    for ax in axes:
        ss = ax.get_subplotspec()
        ss = cast(SubplotSpec, ss)
        subplotspecs[ax] = ss
        if first:
            first = False
            gridspec = ss.get_gridspec()
            nrows, ncols = gridspec.get_geometry()

    axes_grid = np.empty((nrows, ncols), dtype=Axes)

    for i, _ in np.ndenumerate(axes_grid):
        for ax in axes:
            if subplotspecs[ax] == gridspec[i]:
                axes_grid[i] = ax

    if logger.isEnabledFor(logging.DEBUG):
        for (row, col), ax in np.ndenumerate(axes_grid):
            logger.debug(f"{(row,col)}: {ax.get_label()}")

    return axes_grid  # type: ignore


def select_bboxes(use_bbox: bool, bboxes: NDArray, tbboxes: NDArray):
    return bboxes if use_bbox else tbboxes


def get_hspaces_inch(
    figwidth: float, use_bbox: tuple[bool, ...], bboxes: NDArray, tbboxes: NDArray
):
    nspaces = len(use_bbox)
    hpads_inch = np.empty(nspaces, dtype=float)

    first_bboxes = select_bboxes(use_bbox[0], bboxes, tbboxes)[:, 0]
    hpads_inch[0] = np.amin([t.x0 for t in first_bboxes])

    for i in range(1, nspaces - 1):
        left_bboxes = select_bboxes(use_bbox[i], bboxes, tbboxes)[:, i]
        right_bboxes = select_bboxes(use_bbox[i], bboxes, tbboxes)[:, i - 1]
        left = np.amin([t.x0 for t in left_bboxes])
        right = np.amax([t.x1 for t in right_bboxes])
        hpads_inch[i] = left - right

    last_bboxes = select_bboxes(use_bbox[-1], bboxes, tbboxes)[:, -1]
    hpads_inch[-1] = figwidth - np.amax([t.x1 for t in last_bboxes])

    return hpads_inch


def get_vspaces_inch(
    figheight: float, use_bbox: tuple[bool, ...], bboxes: NDArray, tbboxes: NDArray
):
    nspaces = len(use_bbox)
    vpads_inch = np.empty(nspaces, dtype=float)

    first_bboxes = select_bboxes(use_bbox[0], bboxes, tbboxes)[0]
    vpads_inch[0] = figheight - np.amax([t.y1 for t in first_bboxes])

    for i in range(1, nspaces - 1):
        top_bboxes = select_bboxes(use_bbox[i], bboxes, tbboxes)[i]
        bottom_bboxes = select_bboxes(use_bbox[i], bboxes, tbboxes)[i - 1]
        top = np.amax([t.y1 for t in top_bboxes])
        bottom = np.amin([t.y0 for t in bottom_bboxes])
        vpads_inch[i] = bottom - top

    last_bboxes = select_bboxes(use_bbox[-1], bboxes, tbboxes)[-1]
    vpads_inch[-1] = np.amin([t.y0 for t in last_bboxes])

    return vpads_inch


def set_axes_position_inch(bbox_inch: Bbox, ax: Axes, fig: Figure) -> None:
    fw, fh = fig.get_size_inches()
    bbox = Bbox.from_extents(
        bbox_inch.x0 / fw, bbox_inch.y0 / fh, bbox_inch.x1 / fw, bbox_inch.y1 / fh
    )
    ax.set_position(bbox)


def get_caxes_grid(axes) -> list[list[list[Axes]]]:
    return [[ax._colorbars for ax in axes_] for axes_ in axes]


def get_caxes_bboxes_grid(fig, cbar_axes) -> list[list[list[Bbox]]]:
    return [
        [[get_ax_bbox_inch(fig, ax) for ax in caxes_rc] for caxes_rc in caxes_row]
        for caxes_row in cbar_axes
    ]


def add_vspace_inch(
    fig: Figure,
    idx: int,
    vspace: float,
    axes: core.Array[Axes],
    axes_bboxes_inch: core.Array[Bbox],
    caxs: list[list[list[Axes]]],
    cax_bboxes_inch: list[list[list[Bbox]]],
):
    fw_old, fh_old = fig.get_size_inches()
    fh_new = fh_old + vspace
    fig.set_size_inches(fw_old, fh_new, forward=True)

    for (row, col), ba in np.ndenumerate(axes_bboxes_inch):
        shift = 0.0 if row >= idx else vspace
        bbox_new = Bbox.from_bounds(ba.x0, ba.y0 + shift, ba.width, ba.height)
        set_axes_position_inch(bbox_new, axes[row, col], fig)
        for i, bc in enumerate(cax_bboxes_inch[row][col]):
            bbox_new = Bbox.from_bounds(bc.x0, bc.y0 + shift, bc.width, bc.height)
            set_axes_position_inch(bbox_new, caxs[row][col][i], fig)


def add_hspace_inch(
    fig: Figure,
    idx: int,
    hspace: float,
    axes: core.Array[Axes],
    axes_bboxes_inch: core.Array[Bbox],
    caxs: list[list[list[Axes]]],
    cax_bboxes_inch: list[list[list[Bbox]]],
):
    fw_old, fh_old = fig.get_size_inches()
    fw_new = fw_old + hspace
    fig.set_size_inches(fw_new, fh_old, forward=True)

    for (row, col), ba in np.ndenumerate(axes_bboxes_inch):
        shift = 0.0 if col < idx else hspace
        bbox_new = Bbox.from_bounds(ba.x0 + shift, ba.y0, ba.width, ba.height)
        set_axes_position_inch(bbox_new, axes[row, col], fig)
        for i, bc in enumerate(cax_bboxes_inch[row][col]):
            bbox_new = Bbox.from_bounds(bc.x0 + shift, bc.y0, bc.width, bc.height)
            set_axes_position_inch(bbox_new, caxs[row][col][i], fig)


def do_fixed_layout(fig: Figure, **params: Unpack[ParamsDict]):
    renderer = fig._get_renderer()  # type: ignore
    axes_grid = get_axes_grid(get_axes_for_layout(fig._localaxes))  # type: ignore
    nrows, ncols = axes_grid.shape
    nparams = normalize_layout_params(params, nrows, ncols)

    caxs = get_caxes_grid(axes_grid)
    caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)
    bboxes = get_bboxes_inch_grid(fig, axes_grid)

    for _ in range(2):
        tbboxes = get_tbboxes_inch_grid(fig, axes_grid, renderer)

        fw, fh = fig.get_size_inches()
        hpads_now = get_hspaces_inch(fw, nparams["hpads_use_bbox"], bboxes, tbboxes)
        vpads_now = get_vspaces_inch(fh, nparams["vpads_use_bbox"], bboxes, tbboxes)

        hdeltas = nparams["hpads_inch"] - hpads_now
        for i, hdelta in enumerate(hdeltas):
            add_hspace_inch(fig, i, hdelta, axes_grid, bboxes, caxs, caxs_bboxes)
            bboxes = get_bboxes_inch_grid(fig, axes_grid)
            caxs = get_caxes_grid(axes_grid)
            caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)

        vdeltas = nparams["vpads_inch"] - vpads_now
        for i, vdelta in enumerate(vdeltas):
            add_vspace_inch(fig, i, vdelta, axes_grid, bboxes, caxs, caxs_bboxes)
            bboxes = get_bboxes_inch_grid(fig, axes_grid)
            caxs = get_caxes_grid(axes_grid)
            caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)

    fw = fig.get_size_inches()[0]
    if fw > nparams["max_figwidth"]:
        msg = f"figure size ({fw}in) larger than max_figwidth ({nparams['max_figwidth']}in)"
        raise errors.InvalidFigureError(msg)
