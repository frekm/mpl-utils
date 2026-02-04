from ._make_me_nice import *


def make_me_nice(fig: Figure | None = None, **params: Unpack[ParamsDict]) -> None:
    # everything is in inches, nothing is in figure coordinates
    fig = fig or plt.gcf()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes_grid = get_axes_grid(get_axes_for_layout(fig.get_axes()))
    nrows, ncols = axes_grid.shape
    nparams: NormParamsDict = normalize_layout_params(params, nrows, ncols)

    caxs = get_caxes_grid(axes_grid)
    caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)
    bboxes = get_bboxes_grid(fig, axes_grid)

    for _ in range(2):
        tbboxes = get_tbboxes_grid(fig, axes_grid, renderer)

        hpads_now = get_hspaces(nparams["hpads_use_bbox"], bboxes, tbboxes)
        vpads_now = get_vspaces(nparams["vpads_use_bbox"], bboxes, tbboxes)

        hdeltas = nparams["hpads"] - hpads_now
        for i, hdelta in enumerate(hdeltas):
            add_hspace(fig, i, hdelta, axes_grid, bboxes, caxs, caxs_bboxes)
            bboxes = get_bboxes_grid(fig, axes_grid)
            caxs = get_caxes_grid(axes_grid)
            caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)

        vdeltas = nparams["vpads"] - vpads_now
        for i, vdelta in enumerate(vdeltas):
            add_vspace(fig, i, vdelta, axes_grid, bboxes, caxs, caxs_bboxes)
            bboxes = get_bboxes_grid(fig, axes_grid)
            caxs = get_caxes_grid(axes_grid)
            caxs_bboxes = get_caxes_bboxes_grid(fig, caxs)

    fw = fig.get_size_inches()[0]
    if fw > nparams["max_figwidth"]:
        msg = f"figure size ({fw}in) larger than max_figwidth ({nparams['max_figwidth']}in)"
        raise utils.InvalidFigureError(msg)
