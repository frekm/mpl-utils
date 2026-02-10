from typing import Literal, Final

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar
from matplotlib.cm import ScalarMappable
from matplotlib.transforms import Bbox
import numpy as np

from ._layout import (
    normalize_anchor,
    set_axes_width_inch,
    set_axes_height_inch,
)

PTS_PER_INCH: Final = 72.0


def set_axes_size_inches(
    size_inch: float | tuple[float, float],
    aspect: Literal["auto"] | float = "auto",
    ax: None | Axes = None,
    anchor: (
        tuple[float, float]
        | Literal["auto", "C", "N", "NW", "W", "SW", "S", "SE", "E", "NE"]
    ) = "auto",
) -> None:
    """
    Set physical size of `ax`.

    Parameters
    ----------
    size_inch : float or (float, float)
        New width and height of the graph-area of `ax` (that is, excluding
        the axis labels, titles, etc).

        float:
            Change width and height to the same value, unless `aspect` is not "auto".
            Then, change height to `size_inch` × `aspect`.

        (float, float)
            (width, height).

    aspect : "auto" or float, default "auto"
        Control the aspect ratio.

        "auto":
            Determine aspect ratio using `size_inch`.

        float:
            Set aspect ratio of `ax` to height / width.

            If `size_inch` is a tuple and ``size_inch[1] / size_inch[0] != aspect``,
            raises a ValueError.

    ax : :class:`matplotlib.axes.Axes`, optional
        If None, change last active axes.

    anchor : (float, float) or {"auto", "C", "N", "NW", "W", "SW", ...}, default "auto"
        Anchor point of `ax`.

        If "auto", use :meth:`matplotlib.axes.Axes.get_anchor`.
    """
    ax = ax or plt.gca()
    fig = ax.figure
    if not isinstance(fig, Figure):
        raise ValueError("ax must belong to a Figure (not SubFigure)")

    size = np.asarray(size_inch).astype(float)
    if not size.ndim > 0:
        if aspect == "auto":
            width, height = float(size), float(size)
        else:
            width, height = float(size), float(size * aspect)
    else:
        if aspect != "auto" and size[1] / size[0] != aspect:
            raise ValueError("size_inch and aspect contradict each other")
        else:
            width, height = float(size[0]), float(size[1])

    anchor_ = normalize_anchor(ax.get_anchor() if anchor == "auto" else anchor)
    ax.set_anchor(anchor_)

    set_axes_width_inch(fig, ax, width, anchor_)
    set_axes_height_inch(fig, ax, height, anchor_)


def set_colorbar_thickness_pts(colorbar: Colorbar | Axes, thickness: float) -> None:
    cax = colorbar if isinstance(colorbar, Axes) else colorbar.ax
    fig = cax.figure
    if not isinstance(fig, Figure):
        raise ValueError("colorbar must be part of a figure")
    cb_info = getattr(cax, "_colorbar_info", None)
    if cb_info is None:
        raise ValueError("could not retrieve colorbar info")
    parents: list[Axes] = cb_info["parents"]
    if len(parents) != 1:
        raise ValueError("colorbar must belong to exactly one axes")
    parent = parents[0]
    location = cb_info["location"]
    pos_parent = parent.get_position()
    pos_cax = cax.get_position()
    fw, fh = fig.get_size_inches()
    cax.set_aspect("auto")
    cax.set_box_aspect(None)
    if location in ("left", "right"):
        size = thickness / PTS_PER_INCH / fw
        cb_info["fraction"] = size / pos_parent.width
        cb_info["aspect"] = size / pos_cax.height
        if location == "left":
            cax.set_position((pos_cax.x1 - size, pos_cax.y0, size, pos_cax.height))
        else:  # right
            cax.set_position((pos_cax.x0, pos_cax.y0, size, pos_cax.height))
    else:  # top bottom
        size = thickness / PTS_PER_INCH / fh
        cb_info["fraction"] = size / pos_parent.height
        cb_info["aspect"] = pos_cax.width / size
        if location == "top":
            cax.set_position((pos_cax.x0, pos_cax.y0, pos_cax.width, size))
        else:  # bottom
            cax.set_position((pos_cax.x0, pos_cax.y1 - size, pos_cax.width, size))


def set_colorbar_pad_pts(colorbar: Colorbar | Axes, pad: float) -> None:
    cax = colorbar if isinstance(colorbar, Axes) else colorbar.ax
    fig = cax.figure
    if not isinstance(fig, Figure):
        raise ValueError("colorbar must be part of a figure")
    cb_info = getattr(cax, "_colorbar_info", None)
    if cb_info is None:
        raise ValueError("could not retrieve colorbar info")
    parents: list[Axes] = cb_info["parents"]
    if len(parents) != 1:
        raise ValueError("colorbar must belong to exactly one axes")
    parent = parents[0]
    pos_parent = parent.get_position()
    location = cb_info["location"]
    pos_cax = cax.get_position()
    fw, fh = fig.get_size_inches()
    if location in ("left", "right"):
        gap = pad / PTS_PER_INCH / fw
        if location == "left":
            x0 = pos_parent.x0 - gap - pos_cax.width
            pos = Bbox.from_bounds(x0, pos_cax.y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
        else:  # right
            x0 = pos_parent.x1 + gap
            pos = Bbox.from_bounds(x0, pos_cax.y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
    else:  # top bottom
        gap = pad / PTS_PER_INCH / fh
        if location == "top":
            y0 = pos_parent.y1 + gap
            pos = Bbox.from_bounds(pos_cax.x0, y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
        else:  # bottom
            y0 = pos_parent.y0 - gap - pos_cax.height
            pos = Bbox.from_bounds(pos_cax.x0, y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
    cb_info["pad"] = gap


def add_colorbar(
    mappable: ScalarMappable,
    ax: Axes | None = None,
    location: Literal["left", "right", "top", "bottom"] = "right",
    thickness_pts: float | None = None,
    pad_pts: float | None = None,
    label: str | None = None,
    **text_kwargs,
) -> Colorbar:
    """
    Add a colorbar to `axes`.

    Create a new :class:`matplotlib.axes.Axes` next to `ax` with the same height
    (or width), then plot a :class:`matplotlib.colorbar.Colorbar` in it.

    If you change the figure-layout after the fact, you can update the colorbar
    position with :func:`.update_colorbars`.

    Parameters
    ----------
    mappable : :class:`matplotlib.cm.ScalarMappable`
        The colormap described by this colorbar.

        For more information, see :func:`matplotlib.pyplot.colorbar`.

    ax : :class:`matplotlib.axes.Axes`, optional
        The axes to which the colorbar is added.

        If ``None``, use currently active axes.

    location : {"left", "right", "top", "bottom"}, default: ``"right"``
        Location of the colorbar relative to `ax`.

    thickness_pts : float, optional
        The thickness of the colorbar in pts.

        If ``None``, use the default values of
        :meth:`matplotlib.figure.Figure.colorbar`.

    pad_pts : float, optional
        The pad between the colorbar and `axes` in pts.

        If ``None``, use the default values of
        :meth:`matplotlib.figure.Figure.colorbar`.

    label : str, optional
        Label of the colorbar.

        By default, the label of a right-sided colorbar will read from top to bottom.

    Other parameters
    ----------------

    **text_kwargs
        Additional keyword arguments passed to
        :meth:`matplotlib.colorbar.Colorbar.set_label`.

    Returns
    -------
    colorbar : :class:`matplotlib.colorbar.Colorbar`

    Examples
    --------

    .. plot:: _examples/layout/add_colorbar0.py
        :include-source:

    .. plot:: _examples/layout/add_colorbar1.py
        :include-source:

    """
    ax = ax or plt.gca()
    fig = ax.figure

    cbar = fig.colorbar(mappable, ax=ax, use_gridspec=False, location=location)

    axis = cbar.ax.yaxis if location in ("left", "right") else cbar.ax.xaxis
    axis.set_ticks_position(location)  # type: ignore
    axis.set_label_position(location)  # type: ignore

    if label is not None:
        rotation = 270.0 if location == "right" else 0.0
        kwargs = text_kwargs.copy()
        kwargs.setdefault("rotation", rotation)
        cbar.set_label(label, **kwargs)

    if thickness_pts is not None:
        set_colorbar_thickness_pts(cbar, thickness_pts)
    if pad_pts is not None:
        set_colorbar_pad_pts(cbar, pad_pts)

    return cbar


def align_axes_vertically(
    ax: Axes,
    reference_ax: Axes,
    alignment: Literal["center", "top", "bottom"] = "center",
) -> None:
    """
    Set horizontal position of `ax` relative to `reference_ax`.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`
        Axes to reposition.

    reference_ax : :class:`matplotlib.axes.Axes`
        Reference axes.

    alignment : {``"center"``, ``"top"``, ``"bottom"``}, default ``"center"``
        Which reference axis to take from `reference_ax`.
    """
    ...


def align_axes_horizontally(
    ax: Axes,
    reference_ax: Axes,
    alignment: Literal["center", "left", "right"] = "center",
) -> None:
    """
    Set horizontal position of `ax` relative to `reference_ax`.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`
        Axes to reposition.

    reference_ax : :class:`matplotlib.axes.Axes`
        Reference axes.

    alignment : {``"center"``, ``"left"``, ``"right"``}, default ``"center"``
        Which reference axis to take from `reference_ax`.
    """
    ...
