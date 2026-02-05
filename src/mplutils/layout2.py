from typing import Unpack

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ._fix_layout import (
    ParamsDict,
    NormParamsDict,
    validate_figure,
    get_axes_grid,
    get_axes_for_layout,
    normalize_layout_params,
    get_caxes_grid,
    get_caxes_bboxes_grid,
    get_bboxes_grid,
    get_tbboxes_grid,
    get_hspaces,
    get_vspaces,
    add_hspace,
    add_vspace,
)

from . import utils


def apply_fixed_axes_layout(
    fig: Figure | None = None, **params: Unpack[ParamsDict]
) -> None:
    # everything is in inches, nothing is in figure coordinates
    fig = fig or plt.gcf()
    fig.canvas.draw()
    validate_figure(fig)
    renderer = fig.canvas.get_renderer()
    axes_grid = get_axes_grid(get_axes_for_layout(fig.get_axes()))
    nrows, ncols = axes_grid.shape
    nparams: NormParamsDict = normalize_layout_params(params, nrows, ncols)

    caxes_grid = get_caxes_grid(axes_grid)

    caxes_bboxes = get_caxes_bboxes_grid(fig, caxes_grid)
    bboxes = get_bboxes_grid(fig, axes_grid)

    for _ in range(2):
        tbboxes = get_tbboxes_grid(fig, axes_grid, renderer)

        hpads_now = get_hspaces(nparams["hpads_use_bbox"], bboxes, tbboxes)
        vpads_now = get_vspaces(nparams["vpads_use_bbox"], bboxes, tbboxes)

        hdeltas = nparams["hpads"] - hpads_now
        for i, hdelta in enumerate(hdeltas):
            add_hspace(fig, i, hdelta, axes_grid, bboxes, caxes_grid, caxes_bboxes)
            bboxes = get_bboxes_grid(fig, axes_grid)
            caxes_bboxes = get_caxes_bboxes_grid(fig, caxes_grid)

        vdeltas = nparams["vpads"] - vpads_now
        for i, vdelta in enumerate(vdeltas):
            add_vspace(fig, i, vdelta, axes_grid, bboxes, caxes_grid, caxes_bboxes)
            bboxes = get_bboxes_grid(fig, axes_grid)
            caxes_bboxes = get_caxes_bboxes_grid(fig, caxes_grid)

    fw = fig.get_size_inches()[0]
    if fw > nparams["max_figwidth"]:
        msg = f"figure size ({fw}in) larger than max_figwidth ({nparams['max_figwidth']}in)"
        raise utils.InvalidFigureError(msg)
