import typing as tp
import inspect
import os
import pathlib
import math

import cycler
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.axes as maxes
import matplotlib.text as mtext
import matplotlib.figure as mfig
import matplotlib.colors as mcolors
import matplotlib.colorbar as mcbar
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import numpy as np
import numpy.typing as npt

from .constants import PTS_PER_INCH
from .colors import OkabeItoPalette
from ._core import FontsizeLike, convert_to_inches
from ._fixed_layout import get_axes_for_layout, get_axes_grid, get_bboxes_inch_grid
from ._layout import (
    set_colorbar_thickness_inch,
    set_colorbar_pad_inch,
    set_axes_width_inch,
    set_axes_height_inch,
)
from ._utils import normalize_lw_fs_lh


def centers_to_edges(
    centers: npt.ArrayLike,
    lower: None | float = None,
    upper: None | float = None,
) -> npt.NDArray[np.float64]:
    """
    Work out bin edges from bin centers.

    If the bins don't have constant size, at least one limit has to be
    provided, from which the edges can be determined.

    .. attention::

        If `centers` are not the centers of *all* bins, or if `lower` or `upper`
        are not indeed the lower or upper edge, `centers_to_edges` will silently
        produce nonsense.

    Parameters
    ----------
    centers : array_like, shape(n)
        centers of the bins

    lower, uppper : float, optional
        Lower/upper limits of the range.

        At least one limit must be provided if bins don't have a constant
        size. If both lower and upper limits are provided, the lower one
        will be prioritized.

    Returns
    -------
    edges : ndarray, shape(n+1)
        Edges of the bins.
    """
    # if bins don't have a constant size, determine xbinedges differently
    centers = np.asarray(centers, copy=True).astype(np.float64)
    edges = np.empty(len(centers) + 1)
    binsizes = np.diff(centers)
    if not np.allclose(binsizes, binsizes[0], atol=0.0):
        if lower is not None:
            # take lower edge and work out binsize forward
            edges[0] = lower
            for i in range(len(centers)):
                edges[i + 1] = 2.0 * centers[i] - edges[i]

        elif upper is not None:
            # take upper edge and work out binsize backward
            edges[-1] = upper
            for i in reversed(range(len(centers))):
                edges[i] = 2.0 * centers[i] - edges[i + 1]
        else:
            # cannot determine binsize, throw exception
            raise ValueError(
                "cannot determine binsizes without 'upper' or 'lower' bounds"
            )
    else:  # bins have equal size
        edges[:-1] = centers - 0.5 * binsizes[0]
        edges[-1] = centers[-1] + 0.5 * binsizes[0]
    return edges


def savefig(
    fname: None | str = None,
    ftype: None | str | tp.Sequence[str] = None,
    fig: None | mfig.Figure = None,
    **savefig_kwargs,
) -> None:
    r"""
    Save a :class:`matplotlib.figure.Figure` to a file.

    Wraps :func:`matplotlib.pyplot.savefig`.

    Parameters
    ----------
    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    fname : str, optional
        File name (and path).

        If None, uses the filename of the programs entry point.

        If a file name without a file-type extension is provided, uses
        `rcParams["savefig.format"] <https://matplotlib.org/stable/users/explain/customizing.html#matplotlibrc-sample>`__
        unless `ftype` is provided.

        If `fname` ends in ``/`` or ``\``, it is assumed as a directory in which
        the output will be saved using the file name of the programs entry
        point.

        If ``*`` is in `fname`, replace it with the file name of the programs
        entry point.

    ftype : str or Sequence[str], optional
        The file type(s).

        If provided, the appropriate extension is appended to
        `fname` and the file is saved as that file type.

        If a sequence is provided, saves one file for each provided type.

        If nothing is provided, infers the file type from `fname`.

    Other Parameters
    ----------------
    **savefig_kwargs
        Keyword arguments of :func:`matplotlib.pyplot.savefig`.

    See also
    --------
    matplotlib.pyplot.savefig

    Examples
    --------
    Assume a script named ``my_plot.py`` with the contents

    .. code-block:: python
        :caption: ``my_plot.py``

        import mplutils as mplu
        import matplotlib.pyplot as plt

        plt.plot(some_data)

        mplu.savefig()
        mplu.savefig(ftype="pdf")
        mplu.savefig("output/")
        mplu.savefig("output/*_extra")
        mplu.savefig("a_plot")
        mplu.savefig("a_plot", ftype=("pdf", "png"))
        mplu.savefig("a_plot.pdf", ftype=("pdf", "png"))

    Executing ``my_plot.py`` will save:

    - ``my_plot.png`` (assuming `plt.rcParams["savefig.format"] <https://matplotlib.org/stable/users/explain/customizing.html#the-default-matplotlibrc-file>`__ = "png")
    - ``my_plot.pdf``
    - ``output/my_plot.png``
    - ``output/my_plot_extra.png``
    - ``a_plot.png``
    - ``a_plot.pdf`` and ``a_plot.png``
    - ``a_plot.pdf.pdf`` and ``a_plot.pdf.png``

    """

    fig = fig or plt.gcf()

    main_caller_fname = inspect.stack()[-1].filename
    main_caller_fname_base, _ = os.path.splitext(main_caller_fname)
    if fname is None:
        fname = main_caller_fname_base
    elif fname.endswith("\\") or fname.endswith("/"):
        if fname.startswith("\\") or fname.startswith("/"):
            fname = fname[1:]
        path = pathlib.Path(main_caller_fname_base)
        fname = path.parent / fname / path.name  # type: ignore
    elif "*" in fname:
        path = pathlib.Path(main_caller_fname_base)
        fname = fname.replace("*", path.name)

    assert fname is not None

    # create directories if not present
    pathlib.Path(fname).parent.mkdir(parents=True, exist_ok=True)  # type: ignore

    if ftype is None:
        fig.savefig(fname, **savefig_kwargs)
    else:
        ftypes = (ftype,) if isinstance(ftype, str) else tuple(ftype)
        for type in ftypes:
            fig.savefig(f"{fname}.{type}", **savefig_kwargs)


def for_pcolormesh(
    xcenters: npt.ArrayLike,
    ycenters: npt.ArrayLike,
    z: npt.ArrayLike,
    *,
    iteration_order: tp.Literal["x_first", "y_first"] = "x_first",
    xmin: float | None = None,
    xmax: float | None = None,
    ymin: float | None = None,
    ymax: float | None = None,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """
    Convert `xcenters, ycenters, z` such that they can be plotted by
    :func:`matplotlib.pyplot.pcolormesh`.

    See Examples for an example how the arrays are structured.

    Parameters
    ----------
    xcenters : array_like

        A flat sequence of x-coordinates, representing the horizontal position of each
        element in the grid.

        If the bins are not all equal in size, `xmin` or `xmax` needs to be
        specified.

      ycenters : array_like

        A flat sequence of y-coordinates, representing the vertical position of each
        element in the grid.

        If the bins are not all equal in size, `ymin` or `ymax` needs to be
        specified.

    z : array_like
        A flat sequence of data values corresponding to each (xcenters, ycenters)
        coordinate

        The x, y, and z sequences must all be the same length, where each
        z[i] corresponds to the position (xcenters[i], ycenters[i]) in a 2D grid.


    iteration_order : {"x_first", "y_first"}, default "x_first"
        Specify if the outer iteration is along x or y.

    xmin, xmax, ymin, ymax : float, optional
        If x (y) bins do not have constant size, at least one corresponding
        limit has to be provided.

        .. note::

            This does not refer to the limits of the bin centers, but the limits of
            the bin edges!

    Returns
    -------
    X, Y, C : ndarray
        Output formatted to work with :func:`matplotlib.pyplot.pcolormesh`.
    """
    z_ = np.asarray(z)
    if len(np.asarray(xcenters)) != len(np.asarray(ycenters)) != len(z_):
        raise ValueError("xcenters, ycenters, and z must have the same length")

    x_ = np.unique(xcenters)
    y_ = np.unique(ycenters)

    xedges = centers_to_edges(x_, xmin, xmax)
    yedges = centers_to_edges(y_, ymin, ymax)

    if iteration_order == "x_first":
        z_ = z_.reshape(y_.size, x_.size)
    elif iteration_order == "y_first":
        z_ = z_.reshape(x_.size, y_.size).T
    else:
        msg = f"'{iteration_order=}', but it should be 'x_first' or 'y_first'"
        raise ValueError(msg)

    return xedges, yedges, z_


def convert_to_steps(
    x: npt.ArrayLike,
    y: npt.ArrayLike,
    start_at: float | tp.Literal["auto"] = 0.0,
    xlim_lower: float | None = None,
    xlim_upper: float | None = None,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """
    Convert (x,y) data to steps.

    Parameters
    ----------
    x : array_like
        *x* data, corresponding to the centers of the resulting steps.

    y : array_like
        corresponding *y* data.

    start_at : float or "auto", default 0.0
        Start/end steps at this value.

        If "auto", start (end) at first (last) *y* value.

    xlim_lower, ylim_uppper : float, optional
        Lower/upper limits of the range.

        At least one limit must be provided if *x* data doesn't have constant
        spacing. If both lower and upper limits are provided, the lower one
        will be prioritized.

    Returns
    -------
    x, y : ndarray
        Data corresponding to steps.

    Examples
    --------

    .. plot:: _examples/convert_to_steps.py
        :include-source:
    """
    y = np.asarray(y)
    edges = centers_to_edges(x, xlim_lower, xlim_upper)
    x_ = np.repeat(edges, 2)
    y_ = np.empty_like(x_, dtype=np.float64)
    y_[0] = start_at if start_at != "auto" else y[0]
    y_[1:-1] = np.repeat(y, 2)
    y_[-1] = start_at if start_at != "auto" else y[-1]
    return x_, y_


def set_color_cycle(
    *colors: str,
    nsteps: int = 7,
    fig: mfig.Figure | None = None,
) -> None:
    """
    Set the color cycle in plots.

    Modifies ``rcParams`` of matplotlib
    (see `here <https://matplotlib.org/stable/users/explain/customizing.html#the-default-matplotlibrc-file>`__).

    Parameters
    ----------
    *colors : str, optional
        Colors seperated by comma and given in HEX-codes.

        If no colors are provided, defaults to :class:`.OkabeItoPalette`
        (see `here <https://jfly.uni-koeln.de/color/>`__ for a motivation).

        Alternatively, the name of a colormap can be specified and the color
        cycle picks ``nsteps`` colors from that colormap.

        See `matplolib's colormaps documenation <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`__
        for available colormaps.

    nsteps : int, default 7
        Define how many different colors will be set in the color cycler.

        Irrelevant if specific colors are passed in `colors`.

    fig : :class:`matplotlib.figure.Figure`, optional
        Optionally, provide a figure. The color cycle of all axes of that figure
        will be updated.

        If None, check if a figure already exists. If so, update the color
        cycle of all axes of the last active figure.

    Examples
    --------

    .. code:: python

        # Set color cycle to red, green, blue
        set_color_cycle("#FF0000", "#00FF00", "#0000FF")

        # Set color cycle to Okabe and Ito palette
        set_color_cycle()

        # Set color cycle to a continuous colormap that repeats after 8 colors
        set_color_cylce(cmap="viridis", nsteps=8)

        # Set color cycle to a diverging colormap that passes through zero
        # with the second color
        set_color_cylce("RdBu", nsteps=3)

    See also
    --------
    OkabeItoPalette
    OkabeItoMutedPalette
    OkabeItoAccentPalette
    """
    # format colors appropriately
    if not colors:
        if nsteps > 7:
            msg = (
                "For Okabe and Ito palette, a maximum of 7 distinct colors can "
                f"be used, but {nsteps=}"
            )
            raise ValueError(msg)
        colors = OkabeItoPalette()[:nsteps]
    if len(colors) == 1 and colors[0] in plt.colormaps():
        cmap_ = plt.get_cmap(colors[0])
        colors = tuple([mcolors.to_hex(cmap_(i / (nsteps - 1))) for i in range(nsteps)])

    # no figure passed, but a figure exists
    if fig is None and plt.get_fignums():
        fig = plt.gcf()

    # some axes exist already, update the cycler for them
    if fig is not None and fig.get_axes():
        axs = fig.get_axes()
        color_cycler = cycler.cycler(color=colors)
        for ax in axs:
            ax.set_prop_cycle(color_cycler)

    # update rcParams so future axes will use this one
    cycler_str = "cycler('color', ["
    for color in colors:
        if color[0] == "#":
            color = color[1:]
        cycler_str += f"'{color}', "
    cycler_str += "])"
    plt.rcParams["axes.prop_cycle"] = cycler_str


def set_latex_backend(font: tp.Literal["FiraSans", "Times", "ScholaX"]) -> None:
    """
    Enable a latex backend for rendering figures.

    Must be called before figure creation.

    Parameters
    ----------
    font : {``"FiraSans"``, ``"Times"``, ``"ScholaX"``}
        Choose a font. ``"FiraSans"`` uses ``lualatex`` (which is very slow)
        as backend, the other fonts use ``pdflatex`` (not as slow).
    """
    plt.rcParams["pgf.rcfonts"] = False
    plt.rcParams["backend"] = "pgf"

    if font == "FiraSans":
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["pgf.texsystem"] = "lualatex"
        plt.rcParams["pgf.preamble"] = (
            r"\usepackage[mathrm=sym]{unicode-math}\setmathfont{Fira Math}[Scale=MatchUppercase,Numbers=Tabular]\setsansfont{Fira Sans}[Scale=MatchUppercase,Numbers=Lining]\usepackage{picture,xcolor}\usepackage{nicefrac}"
        )
    elif font == "Times":
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["pgf.texsystem"] = "pdflatex"
        plt.rcParams["pgf.preamble"] = (
            r"\usepackage[T1]{fontenc}\usepackage{newtxtext,newtxmath}\usepackage{picture,xcolor}\usepackage{nicefrac}"
        )
    elif font == "ScholaX":
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["pgf.texsystem"] = "pdflatex"
        plt.rcParams["pgf.preamble"] = (
            r"\usepackage{scholax}\usepackage{amsmath,amsthm}\usepackage[scaled=1.075,ncf,vvarbb]{newtxmath}\usepackage{picture,xcolor}\usepackage{nicefrac}"
        )


def crop_colormap(
    cmap,
    x: float = 0.0,
    y: float = 1.0,
    new_cmap_name: str | None = None,
    register: bool = False,
    n_lut: int = 256,
) -> mcolors.LinearSegmentedColormap:
    """
    Return a colormap within (x,y) range

    Parameters
    ----------
    cmap
        A matplotlib colormap, as returned by
        ``matplotlib.colormaps["colormap_name"]``.

    x : float, default = 0.0
        Lower limit of the colorbar (in relative units).

    y : float, default = 1.0
        Upper limit of the colorbar (in relative units).

    new_cmap_name : str, optional
        Optionally, give the colormap a name.

        If ``None``, colormap will be called ``"_new_colormap"``.

    register : bool, default ``False``
        Register the colormap.

        If it is registered, one can call it simply by it's name
        (i.e., ``new_cmap_name``).

    n_lut : int, default 256
        The number of segments of the old colormap.

    Returns
    -------
    new_cmap : :class:`matplotlib.colors.LinearSegmentedColormap`.
        The new colormap.

    Examples
    --------

    .. plot:: _examples/crop_colormap.py
        :include-source:
    """
    if x < 0.0 or x > 1.0:
        raise ValueError(f"{x=}, but it must be within [0.0, 1.0]")
    if y < 0.0 or y > 1.0:
        raise ValueError(f"{y=}, but it must be within [0.0, 1.0]")

    # Ensure we have a list of colors (works for both Listed and LinearSegmented)
    if hasattr(cmap, "colors"):
        # ListedColormap
        colors = cmap.colors
    else:
        # LinearSegmentedColormap → sample N colors
        colors = [cmap(i / (n_lut - 1)) for i in range(n_lut)]

    length = len(colors)
    index_low = int(x * length)
    index_high = int(y * length)

    new_cmap_name = new_cmap_name or "_new_colormap"
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        new_cmap_name, colors[index_low:index_high]
    )

    if register:
        matplotlib.colormaps.register(new_cmap)

    return new_cmap


def textwithbox(
    axes: maxes.Axes,
    x: float,
    y: float,
    text: str,
    pad: float = 1.0,
    boxbackground: str | None = "white",
    boxedgecolor: str = "black",
    boxedgewidth: float = 0.5,
    **text_kwargs,
) -> mtext.Text:
    """
    Plot text with matplotlib surrounded by a box using LaTeX commands.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`
        the axes

    x : float
        x-position

    y : float
        y-position

    text : str
        The text to be surrounded by the box

    pad : float, default: :code:`1.0` (in pts)
        padding between boxedge and text

    boxbackground : ``None``, ``False``, or str, default: ``"white"``
        background of box

        - ``None`` or ``False``: No background color
        - str: latex xcolor named color

    boxedgecolor : str, optional, default: :code:`"black"`
        edge color using named color from latex package *xcolor*
        only used if boxbackground != None

    boxedgewidth : float, default :code:`0.5` (in pts)
        Linewidth of the box' edges.

    **text_kwargs
     Additional :class:`matpotlib.text.Text` keyword arguments.

    Returns
    -------
    text : :class:`matplotlib.text.Text`
        The text artist.

    See also
    --------
    set_latex_backend
    """
    sep = r"\setlength{\fboxsep}{%lfpt}" % pad
    rule = r"\setlength{\fboxrule}{%lfpt}" % boxedgewidth
    if boxbackground is not None:
        text = r"%s\fcolorbox{%s}{%s}{%s}" % (
            sep + rule,
            boxedgecolor,
            boxbackground,
            text,
        )
    else:
        text = r"%s\fbox{%s}" % (sep + rule, text)
    return axes.text(x, y, text, **text_kwargs)


def dotted(
    linewidth: float | None = None,
    fontsize: FontsizeLike = None,
    legend_handlelength: float | None = None,
    **aliases,
) -> tuple[float, tuple[float, float]]:
    """
    Return a tuple to create a dotted line that fits perfectly into a
    legend.

    For that to work properly you may need to provide the linewidth of
    the graph and the fontsize of the legend.

    Parameters
    ----------
    linewidth (or lw) : float, optional, default: ``rcParams["lines.linewidth"]``

    fontsize : float or str, Optional, default: ``rcParams["legend.fontsize"]``
        The fontsize used in the legend

        - float: fontsize in pts
        - str: :code:`"xx-small"`, :code:`"x-small"`, :code:`"small"`,
          :code:`"medium"`, :code:`"large"`, :code:`"x-large"`,
          :code:`"xx-large"`, :code:`"larger"`, or :code:`"smaller"`

    legend_handlelength (or lh) : float, default ``rcParams["legend.handlelength"]``
        Length of the legend handles (the dotted line, in this case) in font
        units

    Returns
    -------
    tuple : (float, (float, float))
        tuple to be used as linetype in plotting

    See Also
    --------
    :func:`.dash_dotted` : Create dotted-line linestyle.
    :func:`.dashed` : Create dash-dotted-line linestyle.

    Examples
    --------
    .. code-block:: python

        import matplotlib.pyplot as plt
        import mplutils as mplu

        plt.plot([0., 1.], linestyle=mplu.dotted())
        plt.legend()

        # if one changes the linewidth, the fontsize of the legend, or the
        # handlelength of the legend from the default, this needs to be passed
        # to dotted().
        plt.plot([0., 1.],
                 linewidth=2.,
                 linestyle=(mplu.dotted(linewidth=2.,
                                      legend_handlelength=3.,
                                      fontsize="x-small")))
        plt.legend(fontsize="x-small", handlelength=3.)

        # alternatively, use rcParams to set these values
        plt.rcParams["lines.linewidth"] = 2.
        plt.rcParams["legend.handlelength"] = 3.
        plt.rcParams["legend.fontsize"] = "x-small"
        plt.plot([0., 1.], linestyle=mplu.dotted())
        plt.legend()

    .. plot:: _examples/legend_dotted.py
        :include-source:
    """
    lw_, fs_, lh_ = normalize_lw_fs_lh(
        linewidth, fontsize, legend_handlelength, **aliases
    )

    total_points = fs_ * lh_ / lw_
    n_dots = math.ceil(total_points / 2.0)
    spacewidth = (total_points - n_dots) / (n_dots - 1)

    return 0.0, (1.0, spacewidth)


def dash_dotted(
    ratio: float = 3.0,
    n_dashes: int = 2,
    linewidth: float | None = None,
    fontsize: FontsizeLike = None,
    legend_handlelength: float | None = None,
    **aliases,
) -> tuple[float, tuple[float, float, float, float]]:
    """
    Return a tuple to create a dash-dotted line that fits perfectly into a
    legend. For that to work properly you may need to provide the linewidth of
    the graph and the fontsize of the legend.

    Parameters
    ----------
    ratio : float, default: 3.0
        Ratio between dash-length and gap-length

    n_dashes : int, default: 2
        Number of dashes drawn

    linewidth (or lw) : float, optional, default: ``rcParams["lines.linewidth"]``

    fontsize : float or str, Optional, default: ``rcParams["legend.fontsize"]``
        The fontsize used in the legend

        - float: fontsize in pts
        - str: :code:`"xx-small"`, :code:`"x-small"`, :code:`"small"`,
          :code:`"medium"`, :code:`"large"`, :code:`"x-large"`,
          :code:`"xx-large"`, :code:`"larger"`, or :code:`"smaller"`

    legend_handlelength (or 'lh') : float, default :code:`rcParams["legend.handlelength"]`
        Length of the legend handles (the dotted line, in this case) in font
        units

    Returns
    -------
    tuple : (float, (float, float, float, float))
        tuple to be used as linetype in plotting

    See Also
    --------
    :func:`.dotted` : Create dotted-line linestyle.
    :func:`.dashed` : Create dash-dotted-line linestyle.

    Examples
    --------
    .. plot:: _examples/legend_dash_dotted.py
        :include-source:
    """
    lw_, fs_, lh_ = normalize_lw_fs_lh(
        linewidth, fontsize, legend_handlelength, **aliases
    )

    total_points = fs_ * lh_ / lw_
    spacewidth = (total_points - n_dashes) / (2.0 * n_dashes - 1 + n_dashes * ratio)
    dashwidth = ratio * spacewidth

    return 0.0, (dashwidth, spacewidth, 1.0, spacewidth)


def dashed(
    ratio: float = 1.5,
    n_dashes: int = 3,
    linewidth: float | None = None,
    fontsize: FontsizeLike = None,
    legend_handlelength: float | None = None,
    **aliases,
) -> tuple[float, tuple[float, float]]:
    """
    Return a tuple to create a dashed line that fits perfectly into a
    legend. For that to work properly you may need to provide the linewidth of
    the graph and the fontsize of the legend.

    Parameters
    ----------
    ratio : float, default: 1.5
        Ratio between dash-length and gap-length

    n_dashes : int, default: 3
        Number of dashes drawn

    linewidth (or lw) : float, optional, default: rcParams["lines.linewidth"]

    fontsize : float or str, Optional, default: rcParams["legend.fontsize"]
        The fontsize used in the legend

        - float: fontsize in pts
        - str: :code:`"xx-small"`, :code:`"x-small"`, :code:`"small"`,
          :code:`"medium"`, :code:`"large"`, :code:`"x-large"`,
          :code:`"xx-large"`, :code:`"larger"`, or :code:`"smaller"`

    legend_handlelength (or lh) : float, default ``rcParams["legend.handlelength"]``
        Length of the legend handles (the dotted line, in this case) in font
        units

    Returns
    -------
    (float, (float, float, float, float))
        tuple to be used as linetype in plotting

    See Also
    --------
    :func:`.dotted` : Create dotted-line linestyle.
    :func:`.dash_dotted` : Create dash-dotted-line linestyle.

    Examples
    --------
    .. plot:: _examples/legend_dashed.py
        :include-source:
    """
    lw_, fs_, lh_ = normalize_lw_fs_lh(
        linewidth, fontsize, legend_handlelength, **aliases
    )

    total_points = fs_ * lh_ / lw_

    n_gaps = n_dashes - 1
    spacewidth = total_points / (n_gaps + n_dashes * ratio)
    dashwidth = ratio * spacewidth

    return 0.0, (dashwidth, spacewidth)


def add_abc(
    fig: mfig.Figure | None = None,
    xoffset_pts: npt.ArrayLike = 2.0,
    yoffset_pts: npt.ArrayLike = -12.0,
    anchor: tp.Literal[
        "top left", "top right", "bottom left", "bottom right"
    ] = "top left",
    labels: str = "a;b;c;d;e;f;g;h;i;j;k;l;m;n;o;p;q;r;s;t;u;v;w;x;y;z",
    labels_sep: str = ";",
    pre: str = "(",
    post: str = ")",
    start_at: int = 0,
    rowsfirst: bool = True,
    **text_kwargs,
) -> dict[maxes.Axes, mtext.Text]:
    """
    Add labels to all suplots in `fig`.

    By default, adds '(a)', '(b)', ... to each subplot in the upper-right
    corner.

    Parameters
    ----------
    fig : :class:`matplotlib.figure.Figure`, optional
        If None, use last active figure.

    xoffset_pts : float, default: ``2.0``
        Offset in pts from `anchor`. Positive moves right.

    yoffset_pts : float, default: ``-12.0``
        Offset in pts from `anchor`. Positive moves up.

    anchor : {``"top left"``, ``"top right"``, ``"bottom left"``, ``"bottom right"``}
        Specify anchor point of the labels (offsets are relative to this).
        Refers to the corner of the graph-area of the axes.

    labels : str, optional, default ``"a;b;c;d; ... ;y;z",``
        A string of labels, where each label is seperated by `labels_sep`.

        If ``None``, use label of the respective axes
        (i.e., :meth:`ax.get_label() <matplotlib.artist.Artist.get_label>`).

    labels_sep : str, default ``";"``
        Separator used for `labels`.

    pre : str, default: ``"("``
        String in front of `labels`.

    post : str, default: ``")"``
        String after `labels`.

    start_at : int, default: 0
        Skip `start_at` entries in `labels`. Only applies if `labels` is not
        ``None``.

    rowsfirst : bool, default: ``True``
        Label rows first, e.g., "a b c / d e f" instead of "a c e / b d f".
        Only applies if `labels` is not ``None``.

    text_kwargs
        Additional keyword arguments of :class:`matplotlib.text.Text`.
        For a list thereof, see `here <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.text.html>`_.

    Returns
    -------
    text_dict : dict[:class:`matplotlib.axes.Axes`, :class:`matplotlib.text.Text`]
        A dictionary with the axes of `fig` as keys and the corresponding
        text instances added by ``add_abc`` as values.

        Can be used to manipulate the text later (to, e.g., change the color
        of the text only for certain subplots).

    Notes
    -----
    Cannot handle a fancy :class:`matplotlib.gridspec.GridSpec`, e.g.,
    where one subplot spans multiple other subplots.
    If you need one of those, you're on your own.

    Examples
    --------

    .. plot:: _examples/add_abc0.py
        :include-source:

    .. plot:: _examples/add_abc1.py
        :include-source:

    .. plot:: _examples/add_abc2.py
        :include-source:

    """
    fig = fig or plt.gcf()
    axs = get_axes_grid(get_axes_for_layout(fig.axes))
    nrows, ncols = axs.shape

    valid_anchors = ["top left", "top right", "bottom left", "bottom right"]
    if anchor not in valid_anchors:
        err_msg = f"{anchor=}, but it needs to be one of {valid_anchors}"
        raise ValueError(err_msg)
    topbottom, leftright = anchor.split(" ")

    # process offsets
    xoffsets_inch = np.asarray(xoffset_pts) / PTS_PER_INCH
    if xoffsets_inch.ndim == 0:
        xoffsets_inch = np.full(axs.shape, xoffsets_inch)
    elif xoffsets_inch.ndim == 1:
        xoffsets_inch = np.repeat(xoffsets_inch[np.newaxis, :], nrows, axis=0)
    if xoffsets_inch.shape != (nrows, ncols):
        msg = f"{xoffset_pts=} but must be either scalar or of shapes ({ncols},) or ({nrows}, {ncols})"
        raise ValueError(msg)
    yoffsets_inch = np.asarray(yoffset_pts) / PTS_PER_INCH
    if yoffsets_inch.ndim == 0:
        yoffsets_inch = np.full(axs.shape, yoffsets_inch)
    elif yoffsets_inch.ndim == 1:
        yoffsets_inch = np.repeat(yoffsets_inch[:, np.newaxis], ncols, axis=1)
    if yoffsets_inch.shape != (nrows, ncols):
        msg = f"{yoffset_pts=} but must be either scalar or of shapes ({nrows},) or ({nrows}, {ncols})"
        raise ValueError(msg)

    if labels is not None:
        labels_ = labels.split(labels_sep)
    out: dict[maxes.Axes, mtext.Text] = {}
    bboxes_inch = get_bboxes_inch_grid(fig, axs)
    for (row, col), bbox in np.ndenumerate(bboxes_inch):
        xloc = 0.0 if leftright == "left" else 1.0
        yloc = 1.0 if topbottom == "top" else 0.0
        x = xloc + xoffsets_inch[row, col] / bbox.width
        y = yloc + yoffsets_inch[row, col] / bbox.height
        if labels is None:
            text = pre + str(axs[row, col].get_label()) + post
        else:
            idx = start_at + (ncols * row + col if rowsfirst else nrows * col + row)
            text = pre + labels_[idx] + post

        out[axs[row, col]] = axs[row, col].text(
            x, y, text, transform=axs[row, col].transAxes, **text_kwargs
        )

    return out


def square_polar_axes(ax: maxes.Axes | None = None, zorder: float = 0.98) -> None:
    """
    Format a polar axes to have a squared outline.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`, optional
        If None, use last active axes.

    Examples
    --------

    .. plot:: _examples/square_polar_axes.py
        :include-source:

    """
    ax = ax or plt.gca()
    ec = plt.rcParams["axes.edgecolor"]

    def circle_to_square_distance(theta_rad):
        h = 1.0
        max_cos_sin = np.maximum(np.abs(np.cos(theta_rad)), np.abs(np.sin(theta_rad)))
        return h / max_cos_sin - h

    ax.add_patch(
        mpatches.Rectangle(
            (-0.0, -0.0),
            1.0,
            1.0,
            transform=ax.transAxes,
            fill=False,
            edgecolor=ec,
            lw=plt.rcParams["axes.linewidth"],
            clip_on=False,
        )
    )

    kwargs = dict(
        clip_on=False,
        solid_capstyle="butt",
        lw=plt.rcParams["axes.linewidth"],
        c=ec,
        zorder=zorder,
    )

    # crosshair
    for n in (0, 1, 2, 3):
        ax.axvline(np.pi / 2.0 * n, 0.0, 1.0, **kwargs)

    for angle in (30, 60, 120, 150, 210, 240, 300, 330):
        angle_rad = np.deg2rad(angle)
        dist = circle_to_square_distance(angle_rad)
        ax.axvline(angle_rad, 1.0 + dist / 3.0, 1.0 + dist, **kwargs)

    ax.set_axis_off()


def normalize_colorbar_metrics(
    fig: mfig.Figure,
    ax: maxes.Axes,
    thickness: float | str | None,
    pad: float | str | None,
    unit: tp.Literal["mm", "inch", "pts"],
    location: tp.Literal["left", "right", "top", "bottom"] = "right",
) -> tuple[float | None, float | None]:
    fw, fh = fig.get_size_inches()
    pos = ax.get_position()
    if location in "left right":
        ax_size = pos.width
        fig_size = fw
    else:  # top bottom
        ax_size = pos.height
        fig_size = fh
    metrics: list[float | None] = [None, None]
    for i, metric in enumerate((thickness, pad)):
        if metric is None:
            continue
        elif isinstance(metric, str):
            if metric[-1] != "%":
                raise ValueError("invalid string, must end with a %")
            metrics[i] = (float(metric[:-1]) * ax_size / 100.0) * fig_size
        else:
            metrics[i] = convert_to_inches(metric, unit)
    return tuple(metrics)  # type: ignore


def add_colorbar(
    mappable: cm.ScalarMappable,
    ax: maxes.Axes | None = None,
    location: tp.Literal["left", "right", "top", "bottom"] = "right",
    thickness: float | str | None = "5%",
    pad: float | str | None = "3.5%",
    unit: tp.Literal["inch", "pts", "mm"] = "pts",
    label: str | None = None,
    **text_kwargs,
) -> mcbar.Colorbar:
    """
    Add a colorbar to `ax`.

    It uses :meth:`matplotlib.figure.Figure.colorbar` to create a colorbar
    and adjusts tick positions and labels appropriately depending on `location`.

    .. warning::

        This method is intended to be used with :class:`.FixedLayoutEngine`.
        Matplotlib's own layouts (e.g.,
        `constrained layout <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html>`__)
        may not work as intended.

    .. warning::

        If you use this method with :func:`~matplotlib.pyplot.imshow`, set the
        use the keyword ``aspect="auto"``, otherwise the colorbar may not be
        aligned properly.

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

    thickness : float or str or None, default "5%"
        The thickness of the colorbar in pts.

        If ``None``, use the default values of
        :meth:`matplotlib.figure.Figure.colorbar`.

        If str, must be of form "x%" and will set the thickness relative to the
        axes size.

        .. warning::

            If *thickness* is of form "x%", it is relative to the initial size of the
            axes. If you resize the axes afterward (e.g., with :func:`.set_axes_size`),
            the thickness will not be updated.

    pad : float or str or None, default "3.5%"
        The pad between the colorbar and `axes` in pts.

        Analog to *thickness*.

    label : str, optional
        Label of the colorbar.

        By default, the label of a right-sided colorbar will read from top to bottom.

    unit : {"mm", "pts", "inch"}, default "pts"
        Unit of *thickness* and *pad*.

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

    .. plot:: _examples/add_colorbar.py
        :include-source:

    """
    ax = ax or plt.gca()
    fig = ax.figure
    if not isinstance(fig, mfig.Figure):
        raise ValueError("ax must be in a top-level Figure")

    old_pos = ax.get_position().frozen()
    cbar = fig.colorbar(mappable, ax=ax, use_gridspec=False, location=location)

    axis = cbar.ax.yaxis if location in ("left", "right") else cbar.ax.xaxis
    axis.set_ticks_position(location)  # type: ignore
    axis.set_label_position(location)  # type: ignore

    thickness_inch, pad_inch = normalize_colorbar_metrics(fig, ax, thickness, pad, unit)

    if thickness_inch is not None:
        set_colorbar_thickness_inch(fig, cbar.ax, thickness_inch)
    if pad_inch is not None:
        set_colorbar_pad_inch(fig, cbar.ax, pad_inch)

    if label is not None:
        kwargs = text_kwargs.copy()
        if location == "right":
            if (not "verticalalignment" in kwargs) and (not "va" in kwargs):
                kwargs["verticalalignment"] = "baseline"
            kwargs.setdefault("rotation", 270.0)
        cbar.set_label(label, **kwargs)

    fw, fh = fig.get_size_inches()
    if location in "left right":
        anchor = (0, 0.5) if location == "right" else (1, 0.5)
        set_axes_width_inch(fig, ax, old_pos.width * fw, anchor)
    else:  # top bottom
        anchor = (0.5, 1.0) if location == "top" else (0.5, 0.0)
        set_axes_height_inch(fig, ax, old_pos.height * fh, anchor)

    return cbar
