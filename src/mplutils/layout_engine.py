from matplotlib.layout_engine import LayoutEngine, ConstrainedLayoutEngine
from matplotlib.figure import Figure
from ._trimmed_layout import trim_figure
import numpy as np

from ._fixed_layout import do_fixed_layout, validate_figure, ParamsDict


class FixedLayoutEngine(LayoutEngine):
    """
    Custom matplotlib :class:`LayoutEngine <matplotlib.layout_engine.LayoutEngine>`.

    This layout engine adjust the size of the figure while fixing the
    size of the axes.

    .. attention::

        The layout engine must be attached to a figure before any
        colorbars are added to it.

    **Constrains:**

    - Fancy gridspecs are not supported. For example, an axes cannot span multiple
      cells in the grid.
    - The layout needs to be set before any colorbars are added.
    - :meth:`Suptitles <matplotlib.pyplot.suptitle>` of figures are currently not
      seen by the engine.
    - Colorbars should be added by :meth:`matplotlib.figure.Figure.colorbar` or
      :func:`.add_colorbar`.
    - This layout is not intended for interactive backends (such as used by
      :func:`matplotlib.pyplot.show`). Using this with an interactive backend
      will eventually break the layout.

    .. note::

        Use :func:`.set_axes_size`, :func:`.set_colorbar_thickness`, and
        :func:`.set_colorbar_pad` to control the physical size of axes and colorbars.

    .. warning::

        Calling :func:`matplotlib.pyplot.tight_layout` will disable this layout engine.

    Parameters
    ----------
    margin_pads_pts : float or (float, ...), default 3.0
        Add padding around the subplot area.

        If axes labels are taken into account when calculating the necessary margins
        is controlled by `margin_pads_ignore_labels`.

        Depending on the number of values passed, control:

        1 value:
            (top, right, bottom, left)

        2 values:
            (top, bottom), (right, left)

        3 values:
            top, (right, left), bottom

        4 values:
            top, right, bottom, left

    margin_pads_ignore_labels : bool or tuple(bool, ...), default False
        Control if `margin_pad_pts` should ignore axes decorations, such as
        labels or colorbars.

        The number of bools passed is analogous to `margin_pad_pts`.

    col_pads_pts : float or tuple(floats, ...), default 10.0
        Padding between each column of the subplots.

        If axes labels are taken into account when calculating the necessary space
        is controlled by `col_pads_ignore_labels`.

        Multiple values will correspond to each column.

    col_pads_ignore_labels : bool or tuple(bools, ...), default False
        Control if `col_pad_pts` should ignore axes decorations, such as labels or
        colorbars.

        The number of bools passed is analogous to `col_pads_pts`.

    row_pads_pts : float or tuple(floats, ...), default 10.0
        Padding between each row of the subplots.

        If axes labels are taken into account when calculating the necessary space
        is controlled by `row_pads_ignore_labels`.

        Multiple values will correspond to each row.

    row_pads_ignore_labels : bool or tuple(bools, ...), default False
        Control if `row_pad_pts` should ignore axes decorations, such as labels or
        colorbars.

        The number of bools passed is analogous to `row_pads_pts`.

    max_figwidth : float, default :obj:`numpy.inf`
        Maximum allowed figure width in inches after layout is applied.

        If the current parameters result in a figure with a width larger than this,
        :class:`.InvalidFigureError` will be raised.

    Raises
    ------
    :class:`.InvalidFigureError`
        Raised if figure width exceeds `max_figwidth`.

    Examples
    --------

    For a figure to use this layout, its layout engine needs to be configured.
    Some ways to do this are

    .. code-block:: python

        fig, ax = plt.subplots_mosaic([["a"]], layout=mplu.FixedLayoutEngine())
        fig, ax = plt.subplots(layout=mplu.FixedLayoutEngine())
        ax = plt.subplot()
        plt.gcf().set_layout_engine(mplu.FixedLayoutEngine())

    The two examples below showcase the difference between this layout engine
    and, e.g., the
    `compressed layout <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html>`__
    of matplotlib.

    With the "compressed" layout of matplotilb,
    since the figure height is fixed, the axes in the subplots are shrunk dramatically,
    and lots of space within the figure is "wasted". To fix this, one has to manually
    adjust the figure height.

    With the `FixedAxesLayoutEngine`, the size of the axes is fixed. This way, we
    can set our desired size using :func:`.set_axes_size` and all necessary parameters
    will be calculated by the engine (such as figure width and height, margins,
    padding between rows and columns).

    .. plot:: _examples/layout_compressed.py
        :include-source:

    .. plot:: _examples/layout_fixed.py
        :include-source:
    """

    _adjust_compatible = False
    _colorbar_gridspec = False

    def __init__(
        self,
        margin_pads_pts: (
            float
            | tuple[float, float]
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ) = 3.0,
        margin_pads_ignore_labels: (
            bool
            | tuple[bool, bool]
            | tuple[bool, bool, bool]
            | tuple[bool, bool, bool, bool]
        ) = False,
        col_pads_pts: float | tuple[float, ...] = 10.0,
        col_pads_ignore_labels: bool | tuple[bool, ...] = False,
        row_pads_pts: float | tuple[float, ...] = 10.0,
        row_pads_ignore_labels: bool | tuple[bool, ...] = False,
        max_figwidth: float = np.inf,
    ):
        self._params: ParamsDict = {
            "margin_pads_pts": margin_pads_pts,
            "margin_pads_ignore_labels": margin_pads_ignore_labels,
            "col_pads_pts": col_pads_pts,
            "col_pads_ignore_labels": col_pads_ignore_labels,
            "row_pads_pts": row_pads_pts,
            "row_pads_ignore_labels": row_pads_ignore_labels,
            "max_figwidth": max_figwidth,
        }
        self._is_executing = False

    def set(
        self,
        margin_pads_pts: (
            float
            | tuple[float, float]
            | tuple[float, float, float]
            | tuple[float, float, float, float]
            | None
        ) = None,
        margin_pads_ignore_labels: (
            bool
            | tuple[bool, bool]
            | tuple[bool, bool, bool]
            | tuple[bool, bool, bool, bool]
            | None
        ) = None,
        col_pads_pts: float | tuple[float, ...] | None = None,
        col_pads_ignore_labels: bool | tuple[bool, ...] | None = None,
        row_pads_pts: float | tuple[float, ...] | None = None,
        row_pads_ignore_labels: bool | tuple[bool, ...] | None = None,
        max_figwidth: float | None = None,
    ):
        for td in self.set.__kwdefaults__:  # type: ignore
            if locals()[td] is not None:
                self._params[td] = locals()[td]

    def get(self) -> ParamsDict:
        return self._params

    def execute(self, fig):
        if self._is_executing:
            return
        self._is_executing = True
        validate_figure(fig)
        do_fixed_layout(fig, **self._params)
        self._is_executing = False


class TrimmedLayoutEngine(ConstrainedLayoutEngine):
    """
    Layout Engine that trims excess figure after a "compressed" layout is applied.

    Parameters
    ----------
    pad_pts : float | Iterable[float]
        Set padding around the subplots in pts.

        Depending on how many values are passed, they correspond to:

        1 value:
            (top, right, bottom, left)

        2 values:
            (top, bottom), (right, left)

        3 values:
            top, (right, left), bottom

        4 values:
            top, right, bottom, left

    **kwargs
        Keyword arguments passed to
        :class:`matplotlib.layout_engine.ConstrainedLayoutEngine`

        See also
        `matplotlib's constrained layout guide <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html#constrainedlayout-guide>`__.

    Notes
    -----
    Interactive resizeing of the figure (e.g., after calling plt.show()) will
    result in messed up layouts. Don't use this engine for these use cases.

    Examples
    --------

    Since the compressed layout does not change figure size (for good reasons),
    a fixed aspect of an axes may result in empty space in the figure:

    .. plot:: _examples/layout/trimmedlayoutengine.py
        :include-source:

    `TrimmedLayoutEngine` simply removes this extra space after the compressed
    layout has been applied:

    .. plot:: _examples/layout/trimmedlayoutengine2.py
        :include-source:
    """

    def __init__(
        self,
        pad_pts: (
            float
            | tuple[float, float]
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ) = 5.0,
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
            trim_figure(fig, self.pad_pts)
        finally:
            self._is_executing = False
