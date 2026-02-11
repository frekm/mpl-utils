from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar

from ._layout import (
    normalize_anchor,
    normalize_width_height,
    set_axes_width_inch,
    set_axes_height_inch,
    set_colorbar_thickness_inch,
    set_colorbar_pad_inch,
)
from .constants import PTS_PER_INCH
from .core import convert_to_inches


def set_axes_size(
    width_inch: float,
    height_inch: float | None = None,
    *,
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
    width_inch, height_inch = normalize_width_height(width_inch, height_inch, aspect)
    anchor_ = normalize_anchor(ax.get_anchor() if anchor == "auto" else anchor)
    ax.set_anchor(anchor_)
    set_axes_width_inch(fig, ax, width_inch, anchor_)
    set_axes_height_inch(fig, ax, height_inch, anchor_)


def set_colorbar_thickness(
    colorbar: Colorbar | Axes,
    thickness: float,
    unit: Literal["mm", "pts", "inch"] = "pts",
) -> None:
    cax = colorbar if isinstance(colorbar, Axes) else colorbar.ax
    thickness_inch = convert_to_inches(thickness, unit)
    set_colorbar_thickness_inch(cax.figure, cax, thickness_inch)


def set_colorbar_pad(
    colorbar: Colorbar | Axes, pad: float, unit: Literal["mm", "pts", "inch"] = "pts"
) -> None:
    cax = colorbar if isinstance(colorbar, Axes) else colorbar.ax
    pad_inch = convert_to_inches(pad, unit)
    set_colorbar_pad_inch(cax.figure, cax, pad_inch)


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
