import io
from typing import Optional, TypeVar, Literal, Any, NamedTuple, Type, cast, Final
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
from matplotlib.backend_bases import RendererBase
from matplotlib.gridspec import SubplotSpec
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.transforms import Bbox
import matplotlib.transforms as mtrans
import itertools
import numpy as np
from numpy.typing import ArrayLike, NDArray
from dataclasses import dataclass


MM_PER_INCH: Final = 25.4
PTS_PER_INCH: Final = 72.0
PTS_PER_MM: Final = PTS_PER_INCH / MM_PER_INCH


_COLORBAR_LABEL: Final = "mplutils colorbar axes"


@dataclass
class _Colorbar:
    colorbar: Colorbar
    parent_ax: Axes
    location: Literal["left", "right", "top", "bottom"]
    thickness_inch: float
    pad_inch: float

    @property
    def ax(self) -> Axes:
        return self.colorbar.ax


class _ColorbarManager:
    def __init__(self) -> None:
        self.colorbars: list[_Colorbar] = []


_colorbar_manager = _ColorbarManager()

from ._misc import Array

T = TypeVar("T")

# TODO add fix_figwidth keyword to add_colpad, add_margins, etc...


def add_colorbar(
    mappable: ScalarMappable,
    ax: Optional[Axes] = None,
    location: Literal["left", "right", "top", "bottom"] = "right",
    thickness_pts: Optional[float] = None,
    pad_pts: Optional[float] = None,
) -> Colorbar:
    """
    Add a colorbar to `axes`.

    Create a new :class:`matplotlib.axes.Axes` next to `ax` with the same height
    (or width), then plot a :class:`matplotlib.color.Colorbar`` in it.

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

        If ``None``, the width will be 5% of the current width (or height,
        depending on `location`) of the axes.

    pad_pts : float, optional
        The pad between the colorbar and `axes` in pts.

        If ``None``, the pad will be 60% of `thickness_pts`.

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
    previous_current_axes = plt.gca()
    valid_positions = ["left", "right", "top", "bottom"]
    if location not in valid_positions:
        msg = f"{location=}, but it should be in {valid_positions}"
        raise ValueError(msg)

    DEFAULT_THICKNESS = 0.05
    DEFAULT_PAD = 0.6

    ax = ax or plt.gca()
    fig = plt.gcf()
    fig_width, fig_height = fig.get_size_inches()
    bbox = ax.get_position()

    if location in ["left", "right"]:
        fig_size = fig_width
        bbox_size = bbox.width
    elif location in ["top", "bottom"]:
        fig_size = fig_height
        bbox_size = bbox.height

    if thickness_pts is None:
        thickness = bbox_size * DEFAULT_THICKNESS
    else:
        thickness = thickness_pts / PTS_PER_INCH / fig_size

    if pad_pts is None:
        pad = thickness * DEFAULT_PAD
    else:
        pad = pad_pts / PTS_PER_INCH / fig_size

    if location == "left":
        height = bbox.height
        width = thickness
        x0 = bbox.x0 - pad - width
        y0 = bbox.y0

    elif location == "right":
        width = thickness
        height = bbox.height
        x0 = bbox.x1 + pad
        y0 = bbox.y0

    elif location == "top":
        width = bbox.width
        height = thickness
        x0 = bbox.x0
        y0 = bbox.y1 + pad

    elif location == "bottom":
        width = bbox.width
        height = thickness
        x0 = bbox.x0
        y0 = bbox.y0 - pad - height

    colorbar_axes = fig.add_axes((x0, y0, width, height), label=_COLORBAR_LABEL)

    colorbar = fig.colorbar(mappable, cax=colorbar_axes, location=location)

    _colorbar_manager.colorbars.append(
        _Colorbar(colorbar, ax, location, thickness * fig_size, pad * fig_size)
    )

    if_any_frame_visible = False
    for t in [f"axes.spines.{l}" for l in ["left", "right", "top", "bottom"]]:
        if_any_frame_visible = if_any_frame_visible or plt.rcParams[t]
    colorbar.outline.set_visible(if_any_frame_visible)  # type: ignore
    plt.sca(previous_current_axes)
    return colorbar


def set_axes_size_inches(
    size_inch: float | tuple[float, float],
    aspect: Literal["auto"] | float = "auto",
    ax: None | Axes = None,
    anchor: (
        tuple[float, float]
        | Literal["auto", "C", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
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

    anchor : "auto" or (float, float) or {"C", "SW", "S", "SE", "E", "NE", ...}, default "auto"
        Anchor point of `ax`.

        E.g., "upper left" means the upper left corner of `ax` stays fixed.

    Examples
    --------
    Create an axes and check its size::

        >>> ax = plt.subplot()
        >>> mplu.get_axes_size_inches()
        Area(width=4.96, height=3.7)

    Set size to (width, height)::

        >>> mplu.set_axes_size_inches((4, 3))
        >>> mplu.get_axes_size_inches()
        Area(width=4.0, height=3.0)

    Set size to (width, width)::

        >>> mplu.set_axes_size_inches(4)
        >>> mplu.get_axes_size_inches()
        Area(width=4.0, height=4.0)

    Set size to (width, width × aspect)::

        >>> mplu.set_axes_size_inches(4, 4 / 3)
        >>> mplu.get_axes_size_inches()
        Area(width=4.0, height=3.0)
    """

    ax = ax or plt.gca()
    fig = ax.get_figure()
    if not isinstance(fig, Figure):
        raise ValueError("axes must be part of a figure")
    # fig.canvas.draw()
    fw, fh = fig.get_size_inches()

    size_inch_ = np.asarray(size_inch).astype(float)
    if not size_inch_.ndim > 0:
        if aspect == "auto":
            new_size_inch = (size_inch_, size_inch_)
        else:
            new_size_inch = (size_inch_, size_inch_ * aspect)
    else:
        if aspect != "auto" and size_inch_[1] / size_inch_[0] != aspect:
            raise ValueError("size_inch and aspect contradict each other")
        else:
            new_size_inch = size_inch_
    new_size = new_size_inch[0] / fw, new_size_inch[1] / fh

    old_pos = ax.get_position().frozen()

    if anchor == "auto":
        anchor = ax.get_anchor()
    if anchor in old_pos.coefs:
        anchor = old_pos.coefs[anchor]
    fx, fy = float(anchor[0]), float(anchor[1])
    ax.set_anchor((fx, fy))

    fixed_x = old_pos.x0 + fx * old_pos.width
    fixed_y = old_pos.y0 + fy * old_pos.height

    new_x0 = fixed_x - fx * new_size[0]
    new_y0 = fixed_y - fy * new_size[1]

    new_pos = Bbox.from_bounds(new_x0, new_y0, new_size[0], new_size[1])

    for cax in ax._colorbars:
        cax.set_box_aspect(None)
        cax.set_aspect("auto")
        old_cbar = cax.get_position().frozen()
        sw = new_size[0] / old_pos.width
        sh = new_size[1] / old_pos.height

        # 2. Calculate the colorbar's position relative to the parent's origin
        # How far is the cbar from the parent's (x0, y0)?
        rel_x0 = old_cbar.x0 - old_pos.x0
        rel_y0 = old_cbar.y0 - old_pos.y0

        location = cax._colorbar_info["location"]
        if location in ["right", "left"]:
            # Stretch vertically, maintain horizontal gap
            new_w = old_cbar.width
            new_h = old_cbar.height * sh

            # If it's on the right, the x-offset must shift with the parent's width change
            if location == "right":
                # Gap between parent right-edge and cbar left-edge
                gap = old_cbar.x0 - old_pos.x1
                cbar_new_x0 = new_x0 + gap
            else:  # left
                gap = old_pos.x0 - old_cbar.x1
                cbar_new_x0 = new_x0 - gap - new_w

            # The vertical start point scales proportionally
            cbar_new_y0 = new_y0 + (rel_y0 * sh)

        else:  # top or bottom
            # Stretch horizontally, maintain vertical gap
            new_w = old_cbar.width * sw
            new_h = old_cbar.height

            if location == "top":
                gap = old_cbar.y0 - old_pos.y1
                cbar_new_y0 = new_y0 + new_size[1] + gap
            else:  # bottom
                gap = old_pos.y0 - old_cbar.y1
                cbar_new_y0 = new_y0 - gap - new_h

            # The horizontal start point scales proportionally
            cbar_new_x0 = new_x0 + (rel_x0 * sw)
        box = Bbox.from_bounds(cbar_new_x0, cbar_new_y0, new_w, new_h)
        cax.set_position(box, which="both")
    ax.set_position(new_pos, which="both")
    fig.stale = True


def add_margins_pts(
    margins_pts: ArrayLike,
    fig: None | Figure = None,
) -> None:
    """
    Add margins to the figure.

    .. note::

        `add_margins_pts` will change the width of the figure. If you do not want that,
        use :func:`.make_me_nice` instead.

    .. tip::

        Instead of manually formatting the margins, use :func:`.make_me_nice`!

    Parameters
    ----------
    margins_pts : array_like
        New margin(s) in pts.

        float:
            Add the same margin to top, right, bottom, left
        (float, float):
            Add the same margin to (top, bottom) and (right, left)
        (float, float, float):
            Add the same margins to top, (right, left), bottom
        (float, float, float, float):
            Add different margins to each side.

    fig : :class:`matplotlib.figure.Figure`, optional
        If ``None``, use last active figure.

    See also
    --------
    make_me_nice
    get_margins_pts
    add_column_pad_pts
    get_column_pad_pts
    add_row_pad_pts
    get_row_pad_pts

    Examples
    --------
    Create an axes and get its current margins using :func:`.get_margins_pts`::

        >>> ax = plt.subplot()
        >>> mplu.get_margins_pts()
        Quadrants(top=37.51, right=38.16, bottom=20.93, left=34.75)

    Add 5 pts to all margins::

        >>> mplu.add_margins_pts(5)
        >>> mplu.get_margins_pts()
        Quadrants(top=42.51, right=43.16, bottom=25.93, left=39.75)

    Remove all "extra" margins of the figure::

        >>> margins = mplu.get_margins_pts()
        >>> mplu.add_margins_pts(-margins)
        >>> mplu.get_margins_pts(ignore_labels=False)
        Quadrants(top=0.0, right=0.0, bottom=0.0, left=0.0)

    As the following plot shows, this removes the extra whitespace around the axes:

    .. plot:: _examples/layout/add_margins_pts.py
        :include-source:

    """
    ...


def add_column_pad_pts(
    icol: int,
    pad_pts: float,
    fig: None | Figure = None,
) -> None:
    """
    Add padding *after* column `icol`.

    .. note::

        `add_column_pad_pts` will change the width of the figure. If you do not want
        that, use :func:`.make_me_nice` instead.

    .. tip::

        Instead of manually formatting the column padding, use :func:`.make_me_nice`!

    Parameters
    ----------
    icol : int
        The column after which padding is inserted.

        ``icol=0`` adds padding *before* the first column (i.e., the left
        figure margin), ``icol=1`` after the first column, ...

    pad_pts : float
        The padding that is added in pts.

    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    See also
    --------
    make_me_nice
    add_margins_pts
    get_margins_pts
    get_column_pad_pts
    add_row_pad_pts
    get_row_pad_pts

    Examples
    --------
    Create two axes and get their current padding using :func:`get_column_pad_pts`::

        >>> plt.subplot(121)
        >>> plt.subplot(122)
        >>> mplu.get_column_pad_pts(1)
        1.71

    Add 5 pts to the padding::

        >>> mplu.add_column_pad_pts(1, 5)
        >>> mplu.get_column_pad_pts(1)
        6.71

    The below example shows how to remove any extra padding in-between columns:

    .. plot:: _examples/layout/add_column_pad_pts.py
        :include-source:
    """
    ...


def add_row_pad_pts(irow: int, pad_pts: float, fig: None | Figure = None) -> None:
    """
    Add padding *after* row `irow`.

    .. note::

        `add_row_pad_pts` will change the height of the figure.

    .. tip::

        Instead of manually formatting the row padding, use :func:`.make_me_nice`!


    Parameters
    ----------
    irow : int
        The row after which padding is inserted. Rows are counted starting from the top.

        ``irow=0`` adds padding *before* the first row (i.e., the top
        figure margin), ``irow=1`` after the first row, ...

    pad_pts : float
        The padding that is added in pts.

    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    See also
    --------
    make_me_nice
    add_margins_pts
    get_margins_pts
    get_column_pad_pts
    add_row_pad_pts
    get_row_pad_pts

    Examples
    --------
    Create two axes and get their current padding using :func:`get_column_pad_pts`::

        >>> plt.subplot(121)
        >>> plt.subplot(122)
        >>> mplu.get_column_pad_pts(1)
        1.71

    Add 5 pts to the padding::

        >>> mplu.add_column_pad_pts(1, 5)
        >>> mplu.get_column_pad_pts(1)
        6.71

    The below example shows how to remove any extra padding in-between columns:

    .. plot:: _examples/layout/add_row_pad_pts.py
        :include-source:
    """
    ...


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
