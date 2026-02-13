from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar
from matplotlib.transforms import Bbox

from ._layout import (
    normalize_anchor,
    normalize_width_height,
    set_axes_width_inch,
    set_axes_height_inch,
    set_colorbar_thickness_inch,
    set_colorbar_pad_inch,
    get_renderer,
    update_colorbar,
)
from . import constants
from ._core import convert_to_inches, get_ax_bbox_inch, get_ax_tbbox_inch


def set_axes_size(
    width: float,
    height: float | None = None,
    *,
    aspect: Literal["auto"] | float = "auto",
    ax: None | Axes = None,
    anchor: (
        tuple[float, float]
        | Literal["auto", "C", "N", "NW", "W", "SW", "S", "SE", "E", "NE"]
    ) = "auto",
    unit: Literal["mm", "pts", "inch"] = "inch",
) -> None:
    """
    Set physical size of `ax`.

    Parameters
    ----------
    width : float
        Desired width of `ax` in units of `unit`.

    height : float, optional
        Desired height of `ax` in units of `unit`.

        If None, determine height according to `aspect`.

    aspect : "auto" or float, default "auto"
        Control the aspect ratio.

        "auto":
            Determine aspect ratio using `width` and `height`. If `height` is None,
            use an aspect ratio of 1.

        float:
            Set aspect ratio of `ax` to height / width.

            If ``height / width != aspect``, raises a ValueError.

    ax : :class:`matplotlib.axes.Axes`, optional
        If None, change last active axes.

    anchor : (float, float) or {"auto", "C", "N", "NW", "W", "SW", ...}, default "auto"
        Anchor point of `ax`.

        If "auto", use :meth:`matplotlib.axes.Axes.get_anchor`.

    unit : {``"mm"`` , ``"inch"`` , ``"pts"``}, default ``"pts"``
        Units of `width` and `height`.
    """
    ax = ax or plt.gca()
    fig = ax.figure
    if not isinstance(fig, Figure):
        raise ValueError("ax must belong to a Figure (not SubFigure)")
    width, height = normalize_width_height(width, height, aspect)
    width_inch = convert_to_inches(width, unit)
    height_inch = convert_to_inches(height, unit)
    anchor_ = normalize_anchor(ax.get_anchor() if anchor == "auto" else anchor)
    ax.set_anchor(anchor_)
    set_axes_width_inch(fig, ax, width_inch, anchor_)
    set_axes_height_inch(fig, ax, height_inch, anchor_)


def set_colorbar_thickness(
    colorbar: Colorbar | Axes,
    thickness: float,
    unit: Literal["mm", "pts", "inch"] = "pts",
) -> None:
    """
    Adjust thickness of a colorbar.

    Parameters
    ----------
    colorbar : :class:`matplotlib.colorbar.Colorbar` or :class:`matplotlib.axes.Axes`
        Colorbar or axes that contains the colorbar.

    thickness : float
        Desired thickness in units of `unit`.

    unit : {``"mm"`` , ``"inch"`` , ``"pts"``}, default ``"pts"``
        Unit of `thickness`.
    """
    cax = colorbar if isinstance(colorbar, Axes) else colorbar.ax
    thickness_inch = convert_to_inches(thickness, unit)
    set_colorbar_thickness_inch(cax.figure, cax, thickness_inch)


def set_colorbar_pad(
    colorbar: Colorbar | Axes, pad: float, unit: Literal["mm", "pts", "inch"] = "pts"
) -> None:
    """
    Adjust padding between a colorbar and its parent axes.

    Parameters
    ----------
    colorbar : :class:`matplotlib.colorbar.Colorbar` or :class:`matplotlib.axes.Axes`
        Colorbar or axes that contains the colorbar.

    pad : float
        Desired padding in units of `unit`.

    unit : {``"mm"`` , ``"inch"`` , ``"pts"``}, default ``"pts"``
        Unit of `pad`.
    """
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

        Should be in the same row as `ax`.

    alignment : {``"center"``, ``"top"``, ``"bottom"``}, default ``"center"``
        Which reference axis to take from `reference_ax`.
    """
    bbox_ax = ax.get_position()
    bbox_ref = reference_ax.get_position()

    if alignment == "center":
        delta = bbox_ref.height - bbox_ax.height
        y0 = bbox_ref.y0 + delta / 2.0
    elif alignment == "top":
        y0 = bbox_ref.y1 - bbox_ax.height
    elif alignment == "bottom":
        y0 = bbox_ref.y0
    else:
        valid_anchors = "center", "top", "bottom"
        msg = f"{alignment=}, but it should be one of {valid_anchors}"
        raise ValueError(msg)

    new_bbox = Bbox.from_bounds(bbox_ax.x0, y0, bbox_ax.width, bbox_ax.height)
    ax.set_position(new_bbox)

    for cax in getattr(ax, "_colorbars", []):
        update_colorbar(cax, bbox_ax, new_bbox)


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

        Should be in the same column as `ax`.

    alignment : {``"center"``, ``"left"``, ``"right"``}, default ``"center"``
        Which reference axis to take from `reference_ax`.
    """
    bbox_ax = ax.get_position()
    bbox_ref = reference_ax.get_position()

    if alignment == "center":
        delta = bbox_ref.width - bbox_ax.width
        x0 = bbox_ref.x0 + delta / 2.0
    elif alignment == "right":
        x0 = bbox_ref.x1 - bbox_ax.width
    elif alignment == "left":
        x0 = bbox_ref.x0
    else:
        valid_anchors = "center", "left", "right"
        msg = f"{alignment=}, but it should be one of {valid_anchors}"
        raise ValueError(msg)

    new_bbox = Bbox.from_bounds(x0, bbox_ax.y0, bbox_ax.width, bbox_ax.height)
    ax.set_position(new_bbox)

    for cax in getattr(ax, "_colorbars", []):
        update_colorbar(cax, bbox_ax, new_bbox)


def get_axes_margins(
    ax: Axes | None = None, unit: Literal["pts", "mm", "inch"] = "pts"
) -> tuple[float, float, float, float]:
    """
    Get the size of the margins of `ax` in physical units.

    The margins are defined by labels, colorbars, etc.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`, optional
        If None, use last active axes.

    unit : ``"pts"`` , ``"mm"`` , ``"inch"`` , default ``"pts"``
        Unit of outputs.

    Returns
    -------
    tuple[float, float, float, float]
        (top, right, bottom, left) margins in units specified by `unit`.

    Examples
    --------

        >>> plt.subplot()
        <Axes: >
        >>> mplu.get_axes_margins()
        (3.9599999999999795, 7.919999999999959, 17.079999999999995, 22.84000000000001)
    """
    ax = ax or plt.gca()
    fig = ax.figure
    if not isinstance(fig, Figure):
        raise ValueError("ax must be part of a Figure")
    renderer = get_renderer(fig)
    bbox = get_ax_bbox_inch(fig, ax)
    tbbox = get_ax_tbbox_inch(fig, ax, renderer)

    out_inch = (
        float(tbbox.y1 - bbox.y1),
        float(tbbox.x1 - bbox.x1),
        float(bbox.y0 - tbbox.y0),
        float(bbox.x0 - tbbox.x0),
    )

    if unit == "inch":
        return out_inch
    if unit == "pts":
        return tuple([el * constants.PTS_PER_INCH for el in out_inch])  # type: ignore
    if unit == "mm":
        return tuple([el * constants.MM_PER_INCH for el in out_inch])  # type: ignore
    raise ValueError(f"{unit=}, but it must be one of ('pts', 'mm', 'inch')")
