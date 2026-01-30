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
from matplotlib.layout_engine import LayoutEngine
import itertools
import numpy as np
from numpy.typing import ArrayLike, NDArray
from dataclasses import dataclass
from functools import wraps

from ._misc import Array

T = TypeVar("T")

# TODO add fix_figwidth keyword to add_colpad, add_margins, etc...


MM_PER_INCH: Final = 25.4
PTS_PER_INCH: Final = 72.0
PTS_PER_MM: Final = PTS_PER_INCH / MM_PER_INCH


class Quadrants(NamedTuple):
    """
    Tuple representing the top/right/bottom/left quadrants of a figure.

    Parameters
    ----------
    top, right, bottom, left :
        The value(s) representing the top, right, bottom, left quadrants.

    Attributes
    ----------
    t, r, b, l :
        Alias for top/right/bottom/left.
    """

    top: Any
    right: Any
    bottom: Any
    left: Any

    @property
    def t(self) -> Any:
        """
        Alias for top.
        """
        return self.top

    @property
    def r(self) -> Any:
        """
        Alias for right.
        """
        return self.right

    @property
    def b(self) -> Any:
        """
        Alias for bottom.
        """
        return self.bottom

    @property
    def l(self) -> Any:
        """
        Alias for left.
        """
        return self.left

    def __neg__(self) -> "Quadrants":
        return Quadrants(*[-el for el in self])

    def __add__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] + val[i] for i in range(4)])
        return Quadrants(*[el + val for el in self])

    def __radd__(self, val) -> "Quadrants":
        return self + val

    def __sub__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] - val[i] for i in range(4)])
        return Quadrants(*[el - val for el in self])

    def __rsub__(self, val) -> "Quadrants":
        return self - val

    def __mul__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] * val[i] for i in range(4)])
        return Quadrants(*[el * val for el in self])

    def __rmul__(self, val) -> "Quadrants":
        return self * val

    def __truediv__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] / val[i] for i in range(4)])
        return Quadrants(*[el / val for el in self])

    def __rtruediv__(self, val) -> "Quadrants":
        return self / val

    def __floordiv__(self, val) -> "Quadrants":
        if isinstance(val, Quadrants):
            return Quadrants(*[self[i] // val[i] for i in range(4)])
        return Quadrants(*[el // val for el in self])

    def __rfloordiv__(self, val) -> "Quadrants":
        return self // val

    def astype(self, t: Type) -> "Quadrants":
        """
        Convert elements to type `t`

        Examples
        --------
        ::

            >>> quadrants = mplu.Quadrants(1.0, 1.0, 1.0, 1.0)
            >>> quadrants
            Quadrants(top=1.0, right=1.0, bottom=1.0, left=1.0)
            >>> quadrants.astype(int)
            Quadrants(top=1, right=1, bottom=1, left=1)
        """
        return Quadrants(*[t(el) for el in self])


class Area(NamedTuple):
    """
    Tuple representing the size of an area.

    Parameters
    ----------
    width, height :
        Width(s) and height(s) of the area.

    Attributes
    ----------
    w, h :
        Aliases for width/height.
    """

    width: Any
    height: Any

    @property
    def w(self) -> Any:
        return self.width

    @property
    def h(self) -> Any:
        return self.height

    def __mul__(self, val) -> "Area":
        if isinstance(val, Area):
            return Area(*[self[i] * val[i] for i in range(2)])
        return Area(*[el * val for el in self])

    def __rmul__(self, val) -> "Area":
        return self * val

    def __add__(self, val) -> "Area":
        if isinstance(val, Area):
            return Area(*[self[i] + val[i] for i in range(2)])
        return Area(*[el + val for el in self])

    def __radd__(self, val) -> "Area":
        return self + val

    def __sub__(self, val) -> "Area":
        if isinstance(val, Area):
            return Area(*[self[i] - val[i] for i in range(2)])
        return Area(*[el - val for el in self])

    def __rsub__(self, val) -> "Area":
        return self - val

    def __truediv__(self, val) -> "Area":
        if isinstance(val, Area):
            return Area(*[self[i] / val[i] for i in range(2)])
        return Area(*[el / val for el in self])

    def __rtruediv__(self, val) -> "Area":
        return self / val

    def __floordiv__(self, val) -> "Area":
        if isinstance(val, Area):
            return Area(*[self[i] // val[i] for i in range(2)])
        return Area(*[el // val for el in self])

    def __rfloordiv__(self, val) -> "Area":
        return self // val

    def __neg__(self) -> "Area":
        return Area(*[-el for el in self])

    def astype(self, t: Type) -> "Area":
        """
        Convert elements to type `t`

        Examples
        --------
        ::

            >>> size = mplu.Area(3.0, 3.0)
            >>> size
            Area(width=3.0, height=3.0)
            >>> size.astype(int)
            Area(width=3, height=3)
        """
        return Area(*[t(el) for el in self])


def _inherit_doc(parent_method):
    def decorator(func):
        # We use wraps to keep the original func's identity,
        # then manually overwrite the docstring.
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__doc__ = parent_method.__doc__
        return wrapper

    return decorator


def _validate_and_get_layout_engine(fig: Figure | None) -> "FixedAxesLayoutEngine":
    fig = fig or plt.gcf()
    engine = fig.get_layout_engine()
    if not isinstance(engine, FixedAxesLayoutEngine):
        msg = f"Figure layout engine must be 'FixedAxesLayoutEngine', but is '{type(engine)}'"
        raise TypeError(msg)
    return engine


def add_column_pad_pts(icol: int, pad_pts: float, fig: None | Figure = None) -> None:
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

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

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
    engine = _validate_and_get_layout_engine(fig)
    return engine._add_column_pad_pts(icol, pad_pts, fig)


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

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`
    """
    fig = _get_topmost_figure(ax)
    engine = _validate_and_get_layout_engine(fig)
    return engine._align_axes_vertically(ax, reference_ax, alignment)


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

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`
    """
    fig = _get_topmost_figure(ax)
    engine = _validate_and_get_layout_engine(fig)
    return engine._align_axes_horizontally(ax, reference_ax, alignment)


def get_row_pad_pts(
    irow: int,
    ignore_labels: bool = False,
    fig: None | Figure = None,
) -> float:
    """
    Get current padding in-between two rows in pts.

    Parameters
    ----------
    irow : int
        Index of row. Starts at 0. The padding in-between row `irow-1` and
        `irow` will be retrieved. If 0, get top figure margin. If
        *total-number-of-rows*, get bottom figure margin.

    ignore_labels : bool, default False
        If ``True``, ignore labels, ticklabels, etc of the axes (typically this means
        that the returned padding will be larger).

    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    Returns
    -------
    pad_pts : float

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

    See also
    --------
    make_me_nice
    add_margins_pts
    get_margins_pts
    add_column_pad_pts
    get_column_pad_pts
    add_row_pad_pts

    Examples
    --------
    Create two axes and get their current padding using :func:`get_row_pad_pts`::

        >>> plt.subplot(211)
        >>> plt.subplot(212)
        >>> mplu.get_row_pad_pts(1)
        3.15

    Ignore axis labels, ticklabels, etc::

        >>> mplu.get_row_pad_pts(1, ignore_labels=True)
        24.19

    Get the row padding *before* the first row (i.e., the top figure margin)::

        >>> mplu.get_row_pad_pts(0)
        37.51
        >>> mplu.get_margins.pts().top
        37.51
    """
    engine = _validate_and_get_layout_engine(fig)
    return engine._get_row_pad_pts(irow, ignore_labels, fig)


def get_margins_pts(
    ignore_labels: ArrayLike = False,
    fig: None | Figure = None,
) -> Quadrants:
    """
    Get the margins of the figure in pts.

    Parameters
    ----------
    ignore_labels : array_like, default False
        If True, ignore labels, ticklabels, etc of the axes.

        bool:
            Ignore/consider all labels.
        (bool, bool)
            Ignore/consider (top, bottom), (right, left) labels separately.
        (bool, bool, bool)
            Ignore/consider top, (right, left), bottom labels separately.
        (bool, bool, bool)
            Ignore/consider all sides separately.

    fig : :class:`matplotlib.figure.Figure`, optional
        If ``None``, use last active figure.

    Returns
    -------
    margins_pts : :class:`.Quadrants`
        (top, right, bottom, left) margins

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

    Examples
    --------

    Create a :class:`matplotlib.axes.Axes`::

        >>> ax = plt.subplot()

    Get margins, ignoring all labels, etc::

        >>> mplu.get_margins_pts()
        Quadrants(top=37.51, right=38.16, bottom=20.93, left=34.75)

    Get margins, taking labels, etc, into account::

        >>> mplu.get_margins_pts(ignore_labels=False)
        Quadrants(top=41.47, right=46.07, bottom=38.01, left=57.6)

    Get margins, taking only labels, etc, from the top and bottom margins into account::

        >>> mplu.get_margins_pts(ignore_labels=(False, True))
        Quadrants(top=37.51, right=46.07, bottom=20.93, left=57.6)
    """
    engine = _validate_and_get_layout_engine(fig)
    return engine._get_margins_pts(ignore_labels, fig)


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

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

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
    engine = _validate_and_get_layout_engine(fig)
    return engine._add_margins_pts(margins_pts, fig)


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

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

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
    engine = _validate_and_get_layout_engine(fig)
    return engine._add_row_pad_pts(irow, pad_pts, fig)


def get_column_pad_pts(
    icol: int, ignore_labels: bool = False, fig: None | Figure = None
) -> float:
    """
    Get current padding in-between two columns in pts.

    Parameters
    ----------
    icol : int
        Index of column. Starts at 0. The padding in-between column `icol-1` and
        `icol` will be retrieved. If 0, get left figure margin. If
        <total-number-of-columns>, get right figure margin.

    ignore_labels : bool, default False
        If ``True``, ignore labels, ticklabels, etc of the axes (typically this means
        that the returned padding will be larger).

    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    Returns
    -------
    pad_pts : float

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

    See also
    --------
    make_me_nice
    add_margins_pts
    get_margins_pts
    add_column_pad_pts
    add_row_pad_pts
    get_row_pad_pts


    Examples
    --------
    Create two axes and get their current padding using :func:`get_column_pad_pts`::

        >>> plt.subplot(121)
        >>> plt.subplot(122)
        >>> mplu.get_column_pad_pts(1)
        1.71

    Ignore axis labels, ticklabels, etc::

        >>> mplu.get_column_pad_pts(1, ignore_labels=True)
        32.47

    Get the column padding *before* the first column (i.e., the left figure margin)::

        >>> mplu.get_column_pad_pts(0)
        34.76
        >>> mplu.get_margins.pts().left
        34.76
    """
    engine = _validate_and_get_layout_engine(fig)
    return engine._get_column_pad_pts(icol, ignore_labels, fig)


def get_axes_size_inches(ax: Axes | None = None) -> Area:
    """
    Get the size of `ax` in inches.

    Parameters
    ----------
    ax : :class:`matplotlib.pyplot.Axes`, optional
        If ``None``, change last active axes.

    Returns
    -------
    area : :class:`.Area`
        Area wrapped in a NamedTuple (width, height) in inches.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

    Examples
    --------

    ::

        >>> ax = plt.subplot()
        >>> size = mplu.get_axes_size_inches(ax)
        >>> size.width
        4.96
        >>> size.height
        3.69
    """
    ax = ax or plt.gca()
    fig = _get_topmost_figure(ax)
    engine = _validate_and_get_layout_engine(fig)
    return engine._get_axes_size_inches(ax)


def set_axes_size_inches(
    size_inch: ArrayLike,
    aspect: Literal["auto"] | float = "auto",
    ax: None | Axes = None,
    anchor: Literal[
        "center",
        "left",
        "right",
        "upper",
        "lower",
        "upper left",
        "upper right",
        "upper center",
        "center left",
        "center right",
        "center center",
        "lower left",
        "lower right",
        "lower center",
    ] = "center",
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

    anchor : {"left", "right", "upper", "lower", "upper left", "upper right", \
"upper center", "center left", "center right", "center center", "lower left", \
"lower right", "lower center"}, default "center"
        Anchor point of `ax`.

        E.g., "upper left" means the upper left corner of `ax` stays fixed.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

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
    fig = _get_topmost_figure(ax)
    engine = _validate_and_get_layout_engine(fig)
    return engine._set_axes_size_inches(size_inch, aspect, ax, anchor)


def get_axes_position_inch(ax: None | Axes = None) -> Bbox:
    """
    Get the bounding box of `ax` in inches, excluding labels, titles, etc.

    Wrapper function for :meth:`matplotlib.axes.Axes.get_position()` which
    converts it to inches.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`, optional
        If ``None``, use last active axes.

    Returns
    -------
    bbox : :class:`matplotlib.transforms.Bbox`
        The bounding box of just the graph-area of `ax` in inches.

        Useful members:

        ``bbox.x0``, ``bbox.x1``
            Location of the left and right edge in inches. Negative values are
            left of the figure left edge.

        ``bbox.y0``, ``bbox.y1``
            Lower and upper edge in inches. Negative values are below the
            figure bottom edge.

        ``bbox.width``, ``bbox.height``
            Width and height of the graph-area of `ax`.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`
    """
    ax = ax or plt.gca()
    engine = _validate_and_get_layout_engine(_get_topmost_figure(ax))
    return engine._get_axes_position_inch(ax)


def set_axes_position_inch(
    x0_inch: float,
    y0_inch: float,
    width_inch: float,
    height_inch: float,
    ax: None | Axes = None,
) -> None:
    """
    Update the axes position using aboslute (instead of relative) units.

    Parameters
    ----------
    x0_inch, y0_inch : float
        The new origin.

    width_inch, height_inch : float
        The new dimensions

    ax : :class:`matplotlib.axes.Axes`, optional
        If ``None``, use last active axes.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`
    """
    ax = ax or plt.gca()
    engine = _validate_and_get_layout_engine(_get_topmost_figure(ax))
    return engine._set_axes_position_inch(x0_inch, y0_inch, width_inch, height_inch, ax)


def get_axes_tightbbox_inch(
    ax: None | Axes = None, renderer: None | RendererBase = None
) -> Bbox:
    """
    Get bounding box of `ax` including labels in inches.

    Wrapper function for :meth:`matplotlib.axes.Axes.get_tightbbox()` which
    converts it to inches.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`, optional
        If ``None``, use last active axes.

    renderer : :class:`matplotlib.backend_bases.RendererBase`, optional
        The renderer used to draw the figure.

        Generally not necessary to pass it. If, however, you use
        a backend that takes a long time to render (e.g., a LuaLaTeX pgf
        backend), it may increase performance by passing the renderer.
        Use :func:`.get_renderer` to get your current renderer.

    Returns
    -------
    bbox : :class:`matplotlib.transforms.Bbox`
        The bounding box of `ax` including x/ylabels, titles, etc, in inches.

        Useful members:

        ``bbox.x0``, ``bbox.x1``
            Location of the left and right edge in inches. Negative values are
            left of the figure left edge.

        ``bbox.y0``, ``bbox.y1``
            Lower and upper edge in inches. Negative values are below the
            figure bottom edge.

        ``bbox.width``, ``bbox.height``
            Width and height of the `ax`, including labels, titles, etc.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`

    Notes
    -----
    This ignores text elements added to `ax`. In particular, this means if
    you used :func:`.add_abc` to add labels outside of the graph-area of `ax`,
    the dimensions returned by ``get_axes_tightbbox_inch`` will not include
    those.
    """
    ax = ax or plt.gca()
    engine = _validate_and_get_layout_engine(_get_topmost_figure(ax))
    return engine._get_axes_tightbbox_inch(ax, renderer)


def get_axes_margins_inches(ax: Axes | None = None) -> Quadrants:
    """
    Get the margins (size of labels, etc) of `ax` in inches.

    Parameters
    ----------
    ax : :class:`matplotlib.pyplot.Axes`, optional
        If ``None``, change last active axes.

    Returns
    -------
    Quadrants : :class:`.Quadrants`
        (top, right, bottom, left) margins.

    Raises
    ------
    TypeError if the layout engine of `fig` is not :class:`.FixedAxesLayoutEngine`
    """
    ax = ax or plt.gca()
    engine = _validate_and_get_layout_engine(_get_topmost_figure(ax))
    return engine._get_axes_margins_inches(ax)


def _is_colorbar_axes(ax: Axes):
    return hasattr(ax, "_colorbar")


def _get_colorbar_location(cax: Axes, parent_axes: list[Axes]):
    cax_bb = cax.get_position()

    parent_bb = Bbox.union([ax.get_position() for ax in parent_axes])

    cx, cy = cax_bb.x0 + cax_bb.width / 2, cax_bb.y0 + cax_bb.height / 2
    px, py = parent_bb.x0 + parent_bb.width / 2, parent_bb.y0 + parent_bb.height / 2

    dx = cx - px
    dy = cy - py

    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "top" if dy > 0 else "bottom"


def _get_topmost_figure(ax: Axes) -> Figure:
    """
    Get the parent figure of `ax`.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`

    Returns
    -------
    figure : :class:`matplotlib.figure.Figure`
    """
    fig = ax.get_figure()
    if fig is None:
        raise ValueError("'ax' is not assigned to any figure")
    while isinstance(fig, SubFigure):
        fig = fig.get_figure()
    return cast(Figure, fig)


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

    colorbar_axes = fig.add_axes((x0, y0, width, height))

    colorbar = fig.colorbar(mappable, cax=colorbar_axes, location=location)

    if_any_frame_visible = False
    for t in [f"axes.spines.{l}" for l in ["left", "right", "top", "bottom"]]:
        if_any_frame_visible = if_any_frame_visible or plt.rcParams[t]
    colorbar.outline.set_visible(if_any_frame_visible)  # type: ignore
    plt.sca(previous_current_axes)
    return colorbar


def _process_marginslike_arg(arg: ArrayLike) -> Quadrants:
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
        rtn = Quadrants(arg, arg, arg, arg)
    elif len(arg) == 1:
        rtn = Quadrants(arg[0], arg[0], arg[0], arg[0])
    elif len(arg) == 2:
        rtn = Quadrants(arg[0], arg[1], arg[0], arg[1])
    elif len(arg) == 3:
        rtn = Quadrants(arg[0], arg[1], arg[2], arg[1])
    elif len(arg) == 4:
        rtn = Quadrants(*arg)
    else:
        raise ValueError(f"{arg=} has invalid length")
    return rtn


def _get_renderer(fig: Optional[Figure]) -> RendererBase:
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


# class Config(TypedDict, total=False):
#     fix_figwidth: bool
#     margin_pad_pts: ArrayLike
#     margin_pad_ignores_labels: bool | tuple[bool, ...]


# class Foo:
#     def __init__(self, **kwargs: Unpack[Config]): ...


class FixedAxesLayoutEngine(LayoutEngine):
    """
    Layout engine with absoulte axes sizes in inches.

    Re-arange axes in `fig` such that their margins don't overlap.
    Also change margins at the edges of the figure such that everything fits.
    Trim or expand the figure height accordingly.

    **Advantages** over :obj:`matplotlib.pyplot.tight_layout` or
    `constrained layout <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html>`_:

    - Keeps widths constant (either of the axes or of the figure).
    - Handle colorbars as one may expect (if they were added using
    :func:`.add_colorbar`).
    - Updates figure height to optimize white-space for fixed aspect ratios.

    **Disadvantages**:

    - Can only handle `nrows` times `ncols` grids. If you have anything fancy
    (an axes that spans multiple columns), you cannot use this
    straightforwardly.

    Parameters
    ----------
    margin_pad_pts : array_like, default 3.0
        float:
            Add the same margin to top, right, bottom, left
        (float, float):
            Add the same margin to (top, bottom) and (right, left)
        (float, float, float):
            Add the same margins to top, (right, left), bottom
        (float, float, float, float):
            Add different margins to top, right, bottom, left.

    margin_pad_ignores_labels : array_like, default ``False``
        Boolean controlling if ``margin_pad_pts`` should add padding taking
        into account axes labels or not.

        Passing more than one value works analogously to `margin_pad_pts`.

    col_pad_pts, row_pad_pts : array_like, default ``10.0``
        Extra padding between the columns (rows) in pts.

        float:
            Same padding in-between all columns (rows).
        (float, ...):
            Different values in-between all columns. Must have a length
            of ``ncols-1`` (``nrows-1``).

    col_pad_ignores_labels, row_pad_ignores_labels : array_like, default ``False``
        Boolean controlling if the padding in-between columns (rows) of axes
        should ignore axes labels or not.

        Passing more than one value works analogously to `col/row_pad_pts`.

    max_figwidth : float, default ``numpy.inf``
        Maximum figure width in inches. If the figure width after rescaling exceeds
        this value, throws a ValueError.

    nruns : int, default 2
        Minimum number of times the algorithm runs.

        If the layout of the figure changes dramatically during a run, `matplotlib`
        may adjust the amount of ticklabels displayed. This changes the overall size
        of axes.

        To account for this change, the algorithm may have to run multiple times.

    log : bool, default False
        Print logs in the standard output.

    See also
    --------
    add_margins_pts
    get_margins_pts
    add_column_pad_pts
    get_column_pad_pts
    add_row_pad_pts
    get_row_pad_pts

    Notes
    -----
    - Cannot handle a fancy :class:`matplotlib.gridspec.GridSpec`, e.g., where
    one subplot spans multiple other subplots.
    If you need one of those, you're on your own.

    Examples
    --------
    Remove margins from a single axes while keeping the axes size constant.

    .. plot:: _examples/layout/make_me_nice_default.py
        :include-source:
    """

    _colorbar_gridspec = False
    _adjust_compatible = False

    def __init__(
        self,
        *,
        margin_pad_pts: ArrayLike = 3.0,
        margin_pad_ignores_labels: ArrayLike = False,
        col_pad_pts: ArrayLike = 10.0,
        col_pad_ignores_labels: ArrayLike = False,
        row_pad_pts: ArrayLike = 10.0,
        row_pad_ignores_labels: ArrayLike = False,
        max_figwidth: float = np.inf,
        nruns: int = 2,
        log: bool = False,
    ):
        self.margin_pad_pts = margin_pad_pts
        self.margin_pad_ignores_labels = margin_pad_ignores_labels
        self.col_pad_pts = col_pad_pts
        self.col_pad_ignores_labels = col_pad_ignores_labels
        self.row_pad_pts = row_pad_pts
        self.row_pad_ignores_labels = row_pad_ignores_labels
        self.max_figwidth = max_figwidth
        self.nruns = nruns
        self.log = log

        self._execute_in_progress = False
        self._axes_grid = None  # will update every time execute is called
        self._colorbars: list[FixedAxesLayoutEngine._Colorbar] = []

    def execute(self, fig):
        if self._execute_in_progress:
            return
        self._execute_in_progress = True

        self._axes_grid = self._get_sorted_axes_grid(fig)
        self._colorbars = self._get_list_of_colorbars(fig)

        try:
            self._apply(
                fig=fig,
                margin_pad_pts=self.margin_pad_pts,
                margin_pad_ignores_labels=self.margin_pad_ignores_labels,
                col_pad_pts=self.col_pad_pts,
                col_pad_ignores_labels=self.col_pad_ignores_labels,
                row_pad_pts=self.row_pad_pts,
                row_pad_ignores_labels=self.row_pad_ignores_labels,
                max_figwidth=self.max_figwidth,
                nruns=self.nruns,
                log=self.log,
            )
        finally:
            self._execute_in_progress = False
            self._axes_grid = None
            self._colorbars = []

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

    def _get_list_of_colorbars(
        self, fig: Figure | None = None
    ) -> list["FixedAxesLayoutEngine._Colorbar"]:
        output: list[FixedAxesLayoutEngine._Colorbar] = []
        fig = plt.gcf() if fig is None else fig
        axs = fig.get_axes()
        figsize = fig.get_size_inches()
        for ax in axs:
            if not _is_colorbar_axes(ax):
                continue
            cbar = ax._colorbar  # type: ignore
            parent = cbar.mappable.axes
            location = _get_colorbar_location(ax, [parent])
            cax_pos = ax.get_position()
            par_pos = parent.get_position()
            if location in ("left", "right"):
                thickness = cax_pos.width * figsize[0]
                if location == "right":
                    pad = (cax_pos.x0 - par_pos.x1) * figsize[0]
                else:
                    pad = (par_pos.x0 - cax_pos.x1) * figsize[0]
            else:
                thickness = cax_pos.height * figsize[1]
                if location == "top":
                    pad = (cax_pos.y0 - par_pos.y1) * figsize[1]
                else:
                    pad = (par_pos.y0 - cax_pos.y1) * figsize[1]

            output.append(
                FixedAxesLayoutEngine._Colorbar(cbar, parent, location, thickness, pad)
            )
        return output

    def _get_sorted_axes_grid(self, fig: Optional[Figure] = None) -> Array[Axes]:
        """
        Get all axes from `fig` and sort them into a 2D grid.

        Only works if all axes of `fig` are part of one-and-the-same
        :class:`matplotlib.gridspec.GridSpec` and if axes are arranged
        in a 2D grid.

        Ignores colormap axes added by :func:`.add_colorbar`.

        Parameters
        ----------
        fig : :class:`matplotlib.figure.Figure`, optional
            If ``None``, use last active figure.

        Returns
        -------
        axes_grid : ndarray, shape(nrows, ncols)
            A 2D numpy array containing the axes of `fig`.

            ``axes_grid[0, 0]`` refers to the top-left,
            ``axes_grid[nrows-1, ncols-1]`` to the bottom right corner.
        """
        fig = fig or plt.gcf()

        axs_unordered: list[Axes] = []
        for ax in fig.get_axes():
            if not _is_colorbar_axes(ax):
                axs_unordered.append(ax)

        # get subplotspecs, ensureing that it is not None
        subplotspecs: dict[Axes, SubplotSpec] = {}
        for ax in axs_unordered:
            subplotspec = ax.get_subplotspec()
            if subplotspec is None:
                msg = "axes not part of a GridSpec, this won't work"
                raise ValueError(msg)
            else:
                subplotspecs[ax] = subplotspec
        assert subplotspecs, "subplotspecs were empty here"

        # check that there is only one GridSpec in the figure
        gridspec = subplotspecs[axs_unordered[0]].get_gridspec()
        for subplotspec in subplotspecs.values():
            if subplotspec.get_gridspec() is not gridspec:
                raise ValueError("Multiple GridSpecs in figure, this won't work")
            if subplotspec.num1 != subplotspec.num2:
                msg = "GridSpec too fancy for me. I can't handle this :c"
                raise ValueError(msg)

        # create a ndarray of axes arranged in a grid corresponding to the gridspec
        axs = np.empty((gridspec.nrows, gridspec.ncols), dtype=Axes)
        for row in range(gridspec.nrows):
            for col in range(gridspec.ncols):
                for ax in axs_unordered:
                    if subplotspecs[ax] == gridspec[row, col]:
                        axs[row, col] = ax

        return axs  # type: ignore

    @_inherit_doc(align_axes_vertically)
    def _align_axes_vertically(
        self,
        ax: Axes,
        reference_ax: Axes,
        alignment: Literal["center", "top", "bottom"] = "center",
    ) -> None:
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
        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars()
        ax.set_position((bbox_ax.x0, y0, bbox_ax.width, bbox_ax.height))
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(align_axes_horizontally)
    def _align_axes_horizontally(
        self,
        ax: Axes,
        reference_ax: Axes,
        alignment: Literal["center", "left", "right"] = "center",
    ) -> None:
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

        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars()
        ax.set_position((x0, bbox_ax.y0, bbox_ax.width, bbox_ax.height))
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(get_row_pad_pts)
    def _get_row_pad_pts(
        self,
        irow: int,
        ignore_labels: bool = False,
        fig: None | Figure = None,
    ) -> float:
        fig = fig or plt.gcf()
        axs = (
            self._get_sorted_axes_grid() if self._axes_grid is None else self._axes_grid
        )
        bboxes = self._get_bboxes_inch_grid(axs)
        tbboxes = self._get_tbboxes_inch_grid(axs, _get_renderer(fig))
        if 0 < irow < axs.shape[0]:
            pads_inch = self._get_rowpads_inch(
                axs.shape[0], ignore_labels, bboxes, tbboxes
            )
            return pads_inch[irow - 1] * PTS_PER_INCH
        else:
            pads_inch = self._get_margins_inch(
                ignore_labels, bboxes, tbboxes, Area(*fig.get_size_inches())
            )
            pads_pts = pads_inch * PTS_PER_INCH
            return pads_pts.top if irow == 0 else pads_pts.bottom

    def _get_margins_inch(
        self,
        ignore_labels: ArrayLike,
        bboxes_inch: NDArray,
        tbboxes_inch: NDArray,
        figsize: Area,
    ) -> Quadrants:
        """
        Implementation of :func:`.get_margins_pts`.

        Parameters
        ----------
        ignore_labels : array_like
            margins-like, (see :func:`._layout._process_marginslike_arg`).

            If ``True``, use `bboxes_inch`, otherwise `tbboxes_inch` for respective
            margin.

        bboxes_inch : ndarray
            Grid of Bboxes without labels, see :func:`._layout._get_bboxes_inch_grid`.

        tbboxes_inch : ndarray
            Grid of Bboxes with labels, see :func:`._layout._get_tbboxes_inch_grid`.

        Return
        ------
        margins_inch : :class:`.Quadrants`
            (top, right, bottom, left) margins in inches
        """
        # TODO: Implement consideration of figure supertitles
        ignore_labels = _process_marginslike_arg(ignore_labels)
        margins_relevant_bboxes = Quadrants(
            bboxes_inch[0] if ignore_labels.top else tbboxes_inch[0],
            bboxes_inch[:, -1] if ignore_labels.right else tbboxes_inch[:, -1],
            bboxes_inch[-1] if ignore_labels.bottom else tbboxes_inch[-1],
            bboxes_inch[:, 0] if ignore_labels.left else tbboxes_inch[:, 0],
        )
        margins = Quadrants(
            np.min([figsize.h - b.y1 for b in margins_relevant_bboxes.top]),
            np.min([figsize.w - b.x1 for b in margins_relevant_bboxes.right]),
            np.min([b.y0 for b in margins_relevant_bboxes.bottom]),
            np.min([b.x0 for b in margins_relevant_bboxes.left]),
        )
        return margins

    @_inherit_doc(get_margins_pts)
    def _get_margins_pts(
        self,
        ignore_labels: ArrayLike = False,
        fig: None | Figure = None,
    ) -> Quadrants:
        fig = fig or plt.gcf()
        figsize = Area(*fig.get_size_inches())
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        renderer = _get_renderer(fig)
        bboxes_inch = self._get_bboxes_inch_grid(axs)
        tbboxes_inch = self._get_tbboxes_inch_grid(axs, renderer)
        margins_inch = self._get_margins_inch(
            ignore_labels, bboxes_inch, tbboxes_inch, figsize
        )
        return margins_inch * PTS_PER_INCH

    def _add_margins_inch(
        self,
        margins_inch: Quadrants,
        axs: NDArray[Any],
        bboxes_inch: NDArray,
        fig: Figure,
    ) -> None:
        """
        Implementation of :func:`.add_margins_pts`.

        Parameters
        ----------
        margins_inch : :class:`.Quadrants`
            margins-like, (see :func:`._layout._process_marginslike_arg`).

            Margins that are added to current margins.

        axs : ndarray
            2D grid of the :class:`axes <matplotlib.axes.Axes>` in the figure.

        bboxes_inch : ndarray
            The corresponding :class:`Bboxes <matplotlib.transform.Bbox>` of `axs`.

        fig : :class:`matplotlib.pyplot.Figure`
        """
        fw_old, fh_old = fig.get_size_inches()
        fw_new = fw_old + margins_inch.left + margins_inch.right
        fh_new = fh_old + margins_inch.top + margins_inch.bottom
        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars(fig)
        fig.set_size_inches(fw_new, fh_new, forward=False)
        for (i, j), bbox in np.ndenumerate(bboxes_inch):
            self._set_axes_position_inch(
                bbox.x0 + margins_inch.left,
                bbox.y0 + margins_inch.bottom,
                bbox.width,
                bbox.height,
                axs[i, j],  # type: ignore
            )
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(add_margins_pts)
    def _add_margins_pts(
        self, margins_pts: ArrayLike, fig: None | Figure = None
    ) -> None:
        fig = fig or plt.gcf()
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        old_bboxes = self._get_bboxes_inch_grid(axs)
        margins = _process_marginslike_arg(margins_pts) / PTS_PER_INCH
        self._add_margins_inch(margins, axs, old_bboxes, fig)

    def _process_rowcol_args(self, vals: ArrayLike, n: int) -> NDArray[Any]:
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
            vals = np.array([vals] * n)
        elif len(vals) != n - 1:
            raise ValueError(f"{vals=}, but must be scalar or of length {n}")
        return vals

    def _add_colpad_inch(
        self, col: int, pad_inch: float, axs: NDArray, bboxes_inch: NDArray, fig: Figure
    ) -> None:
        """
        Add padding after column `col`.

        Implementation of :func:`.add_column_pad_pts`.

        Parameters
        ----------
        col : int
            The column after which padding is inserted.

            ``0`` adds padding to the left figure margin, ``1`` after the first column,
            ``2`` after the second, ...

        pad_inch : float
            The padding that is added in inches.

        axs : ndarray
            2D array of :class:`matplotlib.axes.Axes``.

        bboxes_inch : ndarray
            Corresponding :class:`matplotlib.transforms.Bbox` to `axs`.

        fig : :class:`matplotlib.figure.Figure`
        """
        fw_old, fh_old = fig.get_size_inches()
        fw_new = fw_old + pad_inch
        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars()
        fig.set_size_inches(fw_new, fh_old)
        for (irow, icol), bbox in np.ndenumerate(bboxes_inch):
            pad = 0.0 if icol < col else pad_inch
            self._set_axes_position_inch(
                bbox.x0 + pad,
                bbox.y0,
                bbox.width,
                bbox.height,
                axs[irow, icol],  # type: ignore
            )
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(add_column_pad_pts)
    def _add_column_pad_pts(
        self,
        icol: int,
        pad_pts: float,
        fig: None | Figure = None,
    ) -> None:
        fig = fig or plt.gcf()
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        pad = pad_pts / PTS_PER_INCH
        old_bboxes = self._get_bboxes_inch_grid(axs)
        self._add_colpad_inch(icol, pad, axs, old_bboxes, fig)

    def _add_rowpad_inch(
        self, row: int, pad_inch: float, axs: NDArray, bboxes_inch: NDArray, fig: Figure
    ) -> None:
        fw_old, fh_old = fig.get_size_inches()
        fh_new = fh_old + pad_inch
        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars()
        fig.set_size_inches(fw_old, fh_new)
        for (irow, icol), bbox in np.ndenumerate(bboxes_inch):
            pad = 0.0 if irow >= row else pad_inch
            self._set_axes_position_inch(
                bbox.x0,
                bbox.y0 + pad,
                bbox.width,
                bbox.height,
                axs[irow, icol],  # type: ignore
            )
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(add_row_pad_pts)
    def _add_row_pad_pts(
        self, irow: int, pad_pts: float, fig: None | Figure = None
    ) -> None:
        fig = fig or plt.gcf()
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        old_bboxes = self._get_bboxes_inch_grid(axs)
        pad = pad_pts / PTS_PER_INCH
        self._add_rowpad_inch(irow, pad, axs, old_bboxes, fig)

    def _get_colpads_inch(
        self,
        ncols: int,
        ignore_labels: ArrayLike,
        bboxes: NDArray,
        tbboxes: NDArray,
    ) -> NDArray[np.float64]:
        ignore_labels = self._process_rowcol_args(ignore_labels, ncols)
        current_pads = np.empty(ncols - 1)
        for icol in range(1, ncols):
            col_bboxes = bboxes if ignore_labels[icol - 1] else tbboxes
            left = np.amin([t.x0 for t in col_bboxes[:, icol]])
            right = np.amax([t.x1 for t in col_bboxes[:, icol - 1]])
            current_pads[icol - 1] = left - right
        return current_pads

    @_inherit_doc(get_column_pad_pts)
    def _get_column_pad_pts(
        self, icol: int, ignore_labels: bool = False, fig: None | Figure = None
    ) -> float:
        fig = fig or plt.gcf()
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        bboxes = self._get_bboxes_inch_grid(axs)
        tbboxes = self._get_tbboxes_inch_grid(axs, _get_renderer(fig))
        if 0 < icol < axs.shape[1]:
            pads_inch = self._get_colpads_inch(
                axs.shape[1], ignore_labels, bboxes, tbboxes
            )
            return pads_inch[icol - 1] * PTS_PER_INCH
        else:
            pads_inch = self._get_margins_inch(
                ignore_labels, bboxes, tbboxes, Area(*fig.get_size_inches())
            )
            pads_pts = pads_inch * PTS_PER_INCH
            return pads_pts.left if icol == 0 else pads_pts.right

    def _get_rowpads_inch(
        self,
        nrows: int,
        ignore_labels: ArrayLike,
        bboxes: NDArray,
        tbboxes: NDArray,
    ) -> NDArray[np.float64]:
        ignore_labels = self._process_rowcol_args(ignore_labels, nrows)
        required_space = np.empty(nrows - 1)
        for irow in range(1, nrows):
            row_bboxes = bboxes if ignore_labels[irow - 1] else tbboxes
            top = np.amax([t.y1 for t in row_bboxes[irow]])
            bottom = np.amin([t.y0 for t in row_bboxes[irow - 1]])
            required_space[irow - 1] = bottom - top
        return required_space

    def _apply(
        self,
        fig: None | Figure = None,
        margin_pad_pts: ArrayLike = 3.0,
        margin_pad_ignores_labels: ArrayLike = False,
        col_pad_pts: ArrayLike = 10.0,
        col_pad_ignores_labels: ArrayLike = False,
        row_pad_pts: ArrayLike = 10.0,
        row_pad_ignores_labels: ArrayLike = False,
        max_figwidth: float = np.inf,
        nruns: int = 2,
        log: bool = False,
    ) -> None:
        fig = fig or plt.gcf()
        fig.canvas.draw()
        axs = (
            self._get_sorted_axes_grid(fig)
            if self._axes_grid is None
            else self._axes_grid
        )
        nrows, ncols = axs.shape
        renderer = _get_renderer(fig)
        run = 0

        desired_margin_pads = _process_marginslike_arg(margin_pad_pts) / PTS_PER_INCH
        if ncols > 1:
            desired_colpads = (
                self._process_rowcol_args(col_pad_pts, ncols - 1) / PTS_PER_INCH
            )
        if nrows > 1:
            desired_rowpads = (
                self._process_rowcol_args(row_pad_pts, nrows - 1) / PTS_PER_INCH
            )

        while run < nruns:
            bboxes = self._get_bboxes_inch_grid(axs)
            tbboxes = self._get_tbboxes_inch_grid(axs, renderer)
            current_figsize = Area(*fig.get_size_inches())

            current_colpads = self._get_colpads_inch(
                ncols, col_pad_ignores_labels, bboxes, tbboxes
            )
            current_rowpads = self._get_rowpads_inch(
                nrows, row_pad_ignores_labels, bboxes, tbboxes
            )
            current_margins = self._get_margins_inch(
                margin_pad_ignores_labels, bboxes, tbboxes, current_figsize
            )

            margin_deltas = current_margins - desired_margin_pads
            self._add_margins_inch(-margin_deltas, axs, bboxes, fig)
            bboxes = self._get_bboxes_inch_grid(
                axs
            )  # update bboxes as they have changed

            if ncols > 1:
                colpad_deltas = current_colpads - desired_colpads
                for icol in range(1, ncols):
                    self._add_colpad_inch(
                        icol, -colpad_deltas[icol - 1], axs, bboxes, fig
                    )
                    bboxes = self._get_bboxes_inch_grid(axs)

            if nrows > 1:
                rowpad_deltas = current_rowpads - desired_rowpads
                for irow in range(1, nrows):
                    self._add_rowpad_inch(
                        irow, -rowpad_deltas[irow - 1], axs, bboxes, fig
                    )
                    bboxes = self._get_bboxes_inch_grid(axs)

            run += 1

        necessary_figwidth = fig.get_figwidth()
        if round(necessary_figwidth, 5) > max_figwidth:
            raise ValueError(
                "Parameters result in a figure that is too wide "
                f"({necessary_figwidth=:.5f} > {max_figwidth=:.5f})"
            )

        if log:
            print(f"Number of runs: {run}")

    @_inherit_doc(get_axes_size_inches)
    def _get_axes_size_inches(self, ax: Axes | None = None) -> Area:
        ax = ax or plt.gca()
        fig = _get_topmost_figure(ax)
        figsize = Area(*fig.get_size_inches())
        ax_bbox = ax.get_position()
        return Area(ax_bbox.width * figsize.width, ax_bbox.height * figsize.height)

    @_inherit_doc(set_axes_size_inches)
    def _set_axes_size_inches(
        self,
        size_inch: ArrayLike,
        aspect: Literal["auto"] | float = "auto",
        ax: None | Axes = None,
        anchor: Literal[
            "center",
            "left",
            "right",
            "upper",
            "lower",
            "upper left",
            "upper right",
            "upper center",
            "center left",
            "center right",
            "center center",
            "lower left",
            "lower right",
            "lower center",
        ] = "center",
    ) -> None:
        @dataclass
        class Position:
            x0: float
            y0: float
            width: float
            height: float

        ax = ax or plt.gca()
        figsize = Area(*_get_topmost_figure(ax).get_size_inches())

        size_inch = np.asarray(size_inch).astype(float)
        if not size_inch.ndim > 0:
            if aspect == "auto":
                new_size_inch = Area(size_inch, size_inch)
            else:
                new_size_inch = Area(size_inch, size_inch * aspect)
        else:
            if aspect != "auto" and size_inch[1] / size_inch[0] != aspect:
                raise ValueError("size_inch and aspect contradict each other")
            else:
                new_size_inch = Area(*size_inch)
        new_size = Area(
            new_size_inch.width / figsize.width, new_size_inch.height / figsize.height
        )

        old_pos = ax.get_position()
        new_pos = Position(old_pos.x0, old_pos.y0, new_size.width, new_size.height)

        if anchor == "center":
            anchor = "center center"
        elif anchor == "left":
            anchor = "center left"
        elif anchor == "right":
            anchor = "center right"
        elif anchor == "upper":
            anchor = "upper center"
        elif anchor == "lower":
            anchor = "lower center"

        anchor_split = anchor.split()

        if anchor_split[0] == "lower":
            pass
        elif anchor_split[0] == "upper":
            new_pos.y0 = old_pos.y0 + (old_pos.height - new_pos.height)
        elif anchor_split[0] == "center":
            new_pos.y0 = old_pos.y0 + (old_pos.height - new_pos.height) / 2.0

        if anchor_split[1] == "left":
            pass
        elif anchor_split[1] == "right":
            new_pos.x0 = old_pos.x0 + (old_pos.width - new_pos.width)
        elif anchor_split[1] == "center":
            new_pos.x0 = old_pos.x0 + (old_pos.width - new_pos.width) / 2.0

        if not self._execute_in_progress:
            self._colorbars = self._get_list_of_colorbars()
        ax.set_position((new_pos.x0, new_pos.y0, new_pos.width, new_pos.height))
        self._update_colorbars()
        if not self._execute_in_progress:
            self._colorbars = []

    @_inherit_doc(get_axes_position_inch)
    def _get_axes_position_inch(self, ax: None | Axes = None) -> Bbox:
        ax = ax or plt.gca()
        fw, fh = _get_topmost_figure(ax).get_size_inches()
        bbox = ax.get_position()
        return Bbox([[bbox.x0 * fw, bbox.y0 * fh], [bbox.x1 * fw, bbox.y1 * fh]])

    @_inherit_doc(set_axes_position_inch)
    def _set_axes_position_inch(
        self,
        x0_inch: float,
        y0_inch: float,
        width_inch: float,
        height_inch: float,
        ax: None | Axes = None,
    ) -> None:
        ax = ax or plt.gca()
        fw, fh = _get_topmost_figure(ax).get_size_inches()
        ax.set_position((x0_inch / fw, y0_inch / fh, width_inch / fw, height_inch / fh))

    @_inherit_doc(get_axes_tightbbox_inch)
    def _get_axes_tightbbox_inch(
        self, ax: None | Axes = None, renderer: None | RendererBase = None
    ) -> Bbox:
        ax = ax or plt.gca()
        fig = _get_topmost_figure(ax)
        if fig is None:
            raise ValueError("ax must be part of a figure")
        dpi = fig.get_dpi()

        # TODO figure out why it doesn't include extent of labels
        tbbox_ax = ax.get_tightbbox(renderer, for_layout_only=False)
        assert tbbox_ax
        xy_candidates = Quadrants(
            [tbbox_ax.y1], [tbbox_ax.x1], [tbbox_ax.y0], [tbbox_ax.x0]
        )

        cbars = (
            self._colorbars
            if self._execute_in_progress
            else self._get_list_of_colorbars()
        )

        for cb in cbars:
            if cb.parent_ax is ax:
                tbbox_cb = cb.ax.get_tightbbox(renderer)
                assert tbbox_cb
                if cb.location == "left":
                    xy_candidates.left.append(tbbox_cb.x0)
                    xy_candidates.top.append(tbbox_cb.y1)
                    xy_candidates.bottom.append(tbbox_cb.y0)
                if cb.location == "right":
                    xy_candidates.right.append(tbbox_cb.x1)
                    xy_candidates.top.append(tbbox_cb.y1)
                    xy_candidates.bottom.append(tbbox_cb.y0)
                if cb.location == "top":
                    xy_candidates.top.append(tbbox_cb.y1)
                    xy_candidates.left.append(tbbox_cb.x0)
                    xy_candidates.right.append(tbbox_cb.x1)
                if cb.location == "bottom":
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

    @_inherit_doc(get_axes_margins_inches)
    def _get_axes_margins_inches(self, ax: Axes | None = None) -> Quadrants:
        b = self._get_axes_position_inch(ax)
        t = self._get_axes_tightbbox_inch(ax)
        return Quadrants(t.y1 - b.y1, t.x1 - b.x1, b.y0 - t.y0, b.x0 - t.x0)

    def _get_bboxes_inch_grid(self, axs: NDArray) -> NDArray:
        """
        Get the :class:`Bbox <matplotlib.transforms.Bbox>` of `axs` aranged in a grid
        (`nrows`, `ncols`), excluding labels, etc.

        Parameters
        ----------
        axs : ndarray, shape(`nrows`, `ncols`)
            2D grid of :class:`matplotlib.axes.Axes`.

        Returns
        -------
        bboxes : ndarray
            Corresponding 2D grid of :class:`matplotlib.transforms.Bbox`.
        """
        nrows, ncols = axs.shape
        bboxes_inch = np.empty((nrows, ncols), dtype=Bbox)
        for i, j in itertools.product(range(nrows), range(ncols)):
            bboxes_inch[i, j] = self._get_axes_position_inch(axs[i, j])
        return bboxes_inch

    def _get_tbboxes_inch_grid(
        self, axs: NDArray, renderer: None | RendererBase
    ) -> NDArray:
        """
        Get the :class:`Bbox <matplotlib.transforms.Bbox>` of `axs` aranged in a grid
        (`nrows`, `ncols`) including labels, etc.

        Parameters
        ----------
        axs : ndarray, shape(`nrows`, `ncols`)
            2D grid of :class:`matplotlib.axes.Axes`.

        renderer : :class:`matplotlib.backend_bases.RendererBase`, optional
            The renderer of the figure.

        Returns
        -------
        tbboxes : ndarray
            Corresponding 2D grid of :class:`matplotlib.transforms.Bbox`.
        """
        nrows, ncols = axs.shape
        tbboxes_inch = np.empty((nrows, ncols), dtype=Bbox)
        for i, j in itertools.product(range(nrows), range(ncols)):
            tbboxes_inch[i, j] = self._get_axes_tightbbox_inch(
                axs[i, j], renderer=renderer
            )
        return tbboxes_inch

    def _update_colorbars(self, fig: Figure | None = None) -> None:
        """
        Re-align colorbars to their parent axes.

        Parameters
        ----------
        fig : :class:`matplotlib.figure.Figure`
        """
        fig = plt.gcf() if fig is None else fig
        fig_width_inch, fig_height_inch = fig.get_size_inches()

        cbars = self._colorbars

        for colorbar in cbars:

            bbox_ax = colorbar.parent_ax.get_position()

            if colorbar.location in ("left", "right"):
                pad = colorbar.pad_inch / fig_width_inch
                thickness = colorbar.thickness_inch / fig_width_inch
            elif colorbar.location in ("top", "bottom"):
                pad = colorbar.pad_inch / fig_height_inch
                thickness = colorbar.thickness_inch / fig_height_inch

            if colorbar.location == "left":
                colorbar.ax.set_position(
                    (
                        bbox_ax.x0 - pad - thickness,
                        bbox_ax.y0,
                        thickness,
                        bbox_ax.height,
                    )
                )
            if colorbar.location == "right":
                colorbar.ax.set_position(
                    (bbox_ax.x1 + pad, bbox_ax.y0, thickness, bbox_ax.height)
                )
            if colorbar.location == "top":
                colorbar.ax.set_position(
                    (bbox_ax.x0, bbox_ax.y1 + pad, bbox_ax.width, thickness)
                )
            if colorbar.location == "bottom":
                colorbar.ax.set_position(
                    (bbox_ax.x0, bbox_ax.y0 - pad - thickness, bbox_ax.width, thickness)
                )
