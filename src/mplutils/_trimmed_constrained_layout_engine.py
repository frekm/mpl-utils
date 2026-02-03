from matplotlib.layout_engine import ConstrainedLayoutEngine
from matplotlib.figure import Figure

import numpy as np
from numpy.typing import ArrayLike
from matplotlib.transforms import Bbox
from matplotlib.figure import Figure
import io


PTS_PER_INCH = 72.0


def _get_renderer(fig: Figure):
    """
    Get the renderer of the `fig`.

    Taken from https://stackoverflow.com/questions/22667224/get-text-bounding-box-independent-of-backend/

    Parameters
    ----------
    fig : :class:`matplotlib.figure.Figure`, optional
        If ``None``, use last active figure.

    Returns
    -------
    renderer : :class:`matplotlib.backend_bases.RendererBase`
    """
    fig = fig or plt.gcf()
    if hasattr(fig.canvas, "get_renderer"):
        return fig.canvas.get_renderer()  # type: ignore
    fig.canvas.print_pdf(io.BytesIO())  # type: ignore
    renderer = fig.__dict__.get("_cachedRenderer")
    return renderer  # type: ignore


def _normalize_pads(arg: ArrayLike) -> tuple[float, float, float, float]:
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

    Returns
    -------
    top, right, bottom, left : float
        Padding in inch
    """
    arg = np.asarray(arg, dtype=float) / PTS_PER_INCH
    if not arg.ndim > 0:
        return (float(arg), float(arg), float(arg), float(arg))
    elif len(arg) == 1:
        return (arg[0], arg[0], arg[0], arg[0])
    elif len(arg) == 2:
        return (arg[0], arg[1], arg[0], arg[1])
    elif len(arg) == 3:
        return (arg[0], arg[1], arg[2], arg[1])
    elif len(arg) == 4:
        return (arg[0], arg[1], arg[2], arg[3])
    raise ValueError(f"{arg=} has invalid length")


def _trim_figure(fig, pad_pts: float | tuple[float, ...]):
    tight_bbox = fig.get_tightbbox()

    pads_in = _normalize_pads(pad_pts)
    padded_bbox = Bbox.from_extents(
        tight_bbox.x0 - pads_in[3],
        tight_bbox.y0 - pads_in[2],
        tight_bbox.x1 + pads_in[1],
        tight_bbox.y1 + pads_in[0],
    )

    # New figure size
    new_w_in = padded_bbox.width
    new_h_in = padded_bbox.height

    # Shift axes so content stays in place
    old_w_in, old_h_in = fig.get_size_inches()
    sx = old_w_in / new_w_in
    sy = old_h_in / new_h_in
    dx = -padded_bbox.x0 / new_w_in
    dy = -padded_bbox.y0 / new_h_in

    for ax in fig.get_axes():
        x0, y0, w, h = ax.get_position().bounds
        ax.set_position([x0 * sx + dx, y0 * sy + dy, w * sx, h * sy])
    fig.set_size_inches(new_w_in, new_h_in, forward=True)


class TrimmedConstrainedLayoutEngine(ConstrainedLayoutEngine):
    def __init__(
        self,
        pad_pts: float | tuple[float, ...] = 5.0,
        **kwargs,
    ):
        super().__init__(compress=True, **kwargs)
        self.pad_pts = pad_pts

        self._is_executing = False

    def execute(self, fig: Figure):
        if self._is_executing:
            return
        self._is_executing = True
        try:
            super().execute(fig)
            _trim_figure(fig, self.pad_pts)
        finally:
            self._is_executing = False
