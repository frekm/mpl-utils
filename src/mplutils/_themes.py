import numpy as np
from numpy.typing import ArrayLike
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.text import Text
import matplotlib.patches as patches

import cycler
import math

from typing import Literal, Union, NamedTuple

from . import _layout

GOLDENRATIO = 1.0 + np.sqrt(5.0) / 2.0  # 1.618


class FigureWdith(NamedTuple):
    nature_1col: float
    nature_2col: float
    prl_1col: float
    prl_2col: float
    science_1col: float
    science_2col: float
    science_3col: float
    a4: float
    a5: float


figwidth = FigureWdith(
    nature_1col=3.54,
    nature_2col=7.09,
    prl_1col=3.375,
    prl_2col=6.75,
    science_1col=2.25,
    science_2col=4.75,
    science_3col=7.25,
    a4=210.0 / _layout.MM_PER_INCH,
    a5=148.0 / _layout.MM_PER_INCH,
)


class _Color(NamedTuple):
    red: Literal["#AE1117"]
    teal: Literal["#008081"]
    blue: Literal["#376EB5"]
    green: Literal["#007F00"]
    grey: Literal["#9D9D9C"]
    orange: Literal["#ED7800"]
    pink: Literal["#D4B9DA"]
    yellow: Literal["#FCE205"]
    lemon: Literal["#EFFD5F"]
    corn: Literal["#E4CD05"]
    purple: Literal["#CA8DFD"]
    dark_purple: Literal["#9300FF"]
    forest_green: Literal["#0B6623"]
    bright_green: Literal["#3BB143"]


colors = _Color(
    red="#AE1117",
    teal="#008081",
    blue="#376EB5",
    green="#007F00",
    grey="#9D9D9C",
    orange="#ED7800",
    pink="#D4B9DA",
    yellow="#FCE205",
    lemon="#EFFD5F",
    corn="#E4CD05",
    purple="#CA8DFD",
    dark_purple="#9300FF",
    forest_green="#0B6623",
    bright_green="#3BB143",
)
c = colors


class _OkabeIto(NamedTuple):
    blue: Literal["#56b4e9"]
    orange: Literal["#e69f00"]
    green: Literal["#009e73"]
    yellow: Literal["#f0e442"]
    darkblue: Literal["#0072b2"]
    darkorange: Literal["#d55e00"]
    violet: Literal["#cc79a7"]
    black: Literal["#000000"]


okabe_ito = _OkabeIto(
    "#56b4e9",
    "#e69f00",
    "#009e73",
    "#f0e442",
    "#0072b2",
    "#d55e00",
    "#cc79a7",
    "#000000",
)


class _OkabeItoMuted(NamedTuple):
    sandstone: Literal["#D9CBBE"]
    mist: Literal["#C3CDD6"]
    mauve: Literal["#CAB9C1"]
    ivory: Literal["#F0EDD6"]


okabe_ito_muted = _OkabeItoMuted(
    "#D9CBBE",
    "#C3CDD6",
    "#CAB9C1",
    "#F0EDD6",
)


class _OkabeItoAccent(NamedTuple):
    blue: Literal["#044F7E"]
    red: Literal["#954000"]
    green: Literal["#026D4E"]


okabe_ito_accent = _OkabeItoAccent(
    "#044F7E",
    "#954000",
    "#026D4E",
)


_CM_ATOM = mcolors.LinearSegmentedColormap.from_list(
    "atom",
    [
        (0.0, (0.5, 1.0, 1.0)),
        (0.3, (0.0, 0.0, 1.0)),
        (0.7, (1.0, 0.0, 0.0)),
        (1.0, (1.0, 1.0, 0.0)),
    ],
)
matplotlib.colormaps.register(_CM_ATOM, force=True)
_CM_ATOM_FROM_WHITE = mcolors.LinearSegmentedColormap.from_list(
    "atom_from_white",
    [
        (0.0, (1.0, 1.0, 1.0)),
        (0.065, (0.5, 1.0, 1.0)),
        (0.3, (0.0, 0.0, 1.0)),
        (0.7, (1.0, 0.0, 0.0)),
        (1.0, (1.0, 1.0, 0.0)),
    ],
)
matplotlib.colormaps.register(_CM_ATOM_FROM_WHITE, force=True)

_CM_BLOR = mcolors.LinearSegmentedColormap.from_list(
    "blor",
    [
        (0.0, colors.blue),
        (1.0, colors.orange),
    ],
)
matplotlib.colormaps.register(_CM_BLOR, force=True)


class _ColorMaps(NamedTuple):
    atom: mcolors.LinearSegmentedColormap
    atom_from_white: mcolors.LinearSegmentedColormap
    blor: mcolors.LinearSegmentedColormap


colormaps = _ColorMaps(_CM_ATOM, _CM_ATOM_FROM_WHITE, _CM_BLOR)

_FONT_SCALINGS = {
    "xx-small": 0.579,
    "x-small": 0.694,
    "small": 0.833,
    "medium": 1.0,
    "large": 1.200,
    "x-large": 1.440,
    "xx-large": 1.728,
    "larger": 1.2,
    "smaller": 0.833,
}


class AliasError(Exception):
    def __init__(self, keyword_arg: str, alias: str):
        self.keyword_arg = keyword_arg
        self.alias = alias

    def __str__(self):
        return (
            f"Both '{self.keyword_arg}' and '{self.alias}' have been "
            "provided, but they are aliases"
        )


FontsizeLike = Union[
    float,
    Literal[
        "xx-small",
        "x-small",
        "small",
        "medium",
        "large",
        "x-large",
        "xx-large",
        "larger",
        "smaller",
    ],
    None,
]


def set_color_cycle(
    *colors: str,
    nsteps: int = 7,
    fig: Figure | None = None,
) -> None:
    """
    Set the color cycle in plots.

    Modifies ``rcParams`` of matplotlib
    (see `here <https://matplotlib.org/stable/users/explain/customizing.html#the-default-matplotlibrc-file>`__).

    Parameters
    ----------
    *colors : str, optional
        Colors seperated by comma and given in HEX-codes.

        If now colors are provided, defaults to Okabe and Ito palette
        (see `here <https://jfly.uni-koeln.de/color/>`__ for a motivation).

        Alternatively, the name of a colormap can be specified and the color
        cycle picks ``nsteps`` colors from that colormap.

        See `matplolib's colormaps documenation <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`__
        for available colormaps.

    nsteps : int, default 7
        Define how many different colors will be set in the color cycler.

        Irrelevant if a specific colors are passed in ``colors``.

    fig : :class:`matplotlib.figure.Figure`, optional
        Optionally, provide a figure. The color cycle of all axes of that figure
        will be updated.

        If ``None``, check if a figure already exists. If so, update the color
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
    """
    # format colors appropriately
    if not colors:
        if nsteps > 7:
            msg = (
                "For Okabe and Ito palette, a maximum of 7 distinct colors can "
                f"be used, but {nsteps=}"
            )
            raise ValueError(msg)
        colors = okabe_ito[:nsteps]
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


def set_latex_backend(font: Literal["FiraSans", "Times", "ScholaX"]) -> None:
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


def set_nice_theme(
    spines: str = "ltbr",
    spines_color: Literal["grid"] | str = "#AFAFAF",
    use_latex: bool = False,
    fontsize: float = 10.0,
    use_serif: bool = True,
):
    """
    Sets a theme me likes.

    .. attention::

        The default behavior of this function may change without further notice.
        Do not assume that the behavior will stay constant over multiple
        versions of ``aplepy``.

        If the behavior changes, however, it will be listed in the
        `changelog <https://github.com/frekm/aplepy/blob/main/changelog.md>`__.

    Parameters
    ----------
    spines : str, default "ltbr"
        Any combination of ``"l"``, ``"b"``, ``"t"``, ``"r"``.
        E.g., ``"lb"`` would enable the left and bottom spines of the axes.
        ``""`` disables all spines.

    use_latex : bool, default `False`
        Use a latex backend for rendering. May be slow.

    fontsize : float, default 10 pts

    use_serif : bool, default `True`
        Use a font-family with serifs. If `False`, use a sans-serif font family.

    """
    spines_sort = "".join(sorted(spines))
    valid_spines = (
        "b",
        "l",
        "r",
        "t",
        "bl",
        "br",
        "bt",
        "blr",
        "blt",
        "brt",
        "blrt",
        "",
    )
    if spines_sort not in valid_spines:
        msg = "invalid spines identifier. spines must only contain b, l, r, or t a maximum of one time"
        raise ValueError(msg)

    plt.style.use("default")

    set_color_cycle()

    if use_latex:
        if use_serif:
            plt.rcParams["font.size"] = fontsize
            plt.rcParams["font.family"] = "serif"
            set_latex_backend(font="ScholaX")
        else:
            plt.rcParams["font.size"] = fontsize
            set_latex_backend(font="FiraSans")
    else:
        if use_serif:
            plt.rcParams["font.size"] = fontsize
            plt.rcParams["font.family"] = "serif"
            plt.rcParams["font.serif"] = (
                "STIXGeneral, DejaVu Serif, Bitstream Vera Serif, Computer Modern Roman, New Century Schoolbook, Century Schoolbook L, Utopia, ITC Bookman, Bookman, Nimbus Roman No9 L, Times New Roman, Times, Palatino, Charter, serif"
            )
            plt.rcParams["mathtext.fontset"] = "stix"
        else:
            plt.rcParams["font.size"] = fontsize * 0.9

    plt.rcParams["figure.figsize"] = (
        80.0 / _layout.MM_PER_INCH,
        60.0 / _layout.MM_PER_INCH,
    )
    plt.rcParams["figure.dpi"] = 600
    plt.rcParams["savefig.format"] = "pdf"

    plt.rcParams["axes.spines.left"] = True if "l" in spines else False
    plt.rcParams["axes.spines.bottom"] = True if "b" in spines else False
    plt.rcParams["axes.spines.top"] = True if "t" in spines else False
    plt.rcParams["axes.spines.right"] = True if "r" in spines else False

    plt.rcParams["xtick.major.pad"] = 1.8
    plt.rcParams["xtick.minor.pad"] = 1.5
    plt.rcParams["ytick.major.pad"] = 1.8
    plt.rcParams["ytick.minor.pad"] = 1.5
    plt.rcParams["axes.labelpad"] = 2.0
    plt.rcParams["axes.titlepad"] = 5.0

    plt.rcParams["axes.grid"] = True
    plt.rcParams["axes.grid.axis"] = "both"
    plt.rcParams["axes.grid.which"] = "major"

    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.linewidth"] = plt.rcParams["axes.linewidth"]

    plt.rcParams["lines.linewidth"] = 2.0
    plt.rcParams["lines.markersize"] = 3.0
    plt.rcParams["errorbar.capsize"] = plt.rcParams["lines.markersize"]

    plt.rcParams["xtick.major.size"] = 3.5
    plt.rcParams["ytick.major.size"] = 3.5
    plt.rcParams["xtick.minor.size"] = 2.0
    plt.rcParams["ytick.minor.size"] = 2.0
    plt.rcParams["xtick.major.width"] = plt.rcParams["axes.linewidth"]
    plt.rcParams["ytick.major.width"] = plt.rcParams["axes.linewidth"]
    plt.rcParams["xtick.minor.width"] = 0.4
    plt.rcParams["ytick.minor.width"] = 0.4

    plt.rcParams["axes.titlelocation"] = "left"

    c_grid = "#E2E2E2"
    c_spines = c_grid if spines_color == "grid" else spines_color

    plt.rcParams["grid.color"] = c_grid
    plt.rcParams["grid.alpha"] = 1.0
    plt.rcParams["axes.edgecolor"] = c_spines
    plt.rcParams["xtick.color"] = c_spines if "b" in spines else c_grid
    plt.rcParams["ytick.color"] = c_spines if "l" in spines else c_grid
    plt.rcParams["xtick.labelcolor"] = "k"
    plt.rcParams["ytick.labelcolor"] = "k"

    plt.rcParams["grid.linewidth"] = plt.rcParams["axes.linewidth"]

    plt.rcParams["legend.frameon"] = False

    plt.rcParams["image.cmap"] = "atom"
    plt.rcParams["image.aspect"] = "auto"


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

    .. plot:: _examples/themes/crop_colormap.py
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
    axes: Axes,
    x: float,
    y: float,
    text: str,
    pad: float = 1.0,
    boxbackground: str | None = "white",
    boxedgecolor: str = "black",
    boxedgewidth: float = 0.5,
    **text_kwargs,
) -> Text:
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


def _set_lw_fs_lh(
    linewidth: float | None,
    fontsize: float | str | None,
    legend_handlelength: float | None,
    **aliases,
) -> tuple[float, float, float]:
    """Process parameters for dashed/dotted/..."""
    # check if aliases are doubled
    if "lw" in aliases and linewidth is not None:
        raise AliasError("linewidth", "lw")
    if "lh" in aliases and legend_handlelength is not None:
        raise AliasError("legend_handlelength", "lh")

    lw = linewidth if linewidth else aliases.get("lw", plt.rcParams["lines.linewidth"])
    lh = (
        legend_handlelength
        if legend_handlelength
        else aliases.get("lh", plt.rcParams["legend.handlelength"])
    )
    fontsize_ = fontsize if fontsize is not None else plt.rcParams["legend.fontsize"]
    if isinstance(fontsize_, str):
        if fontsize_ in _FONT_SCALINGS:
            fontsize_ = _FONT_SCALINGS[fontsize_] * plt.rcParams["font.size"]
        else:
            raise ValueError("Invalid specifier for fontsize")

    return lw, fontsize_, lh


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

    .. plot:: _examples/themes/legend_dotted.py
        :include-source:
    """
    lw_, fs_, lh_ = _set_lw_fs_lh(linewidth, fontsize, legend_handlelength, **aliases)

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
    .. plot:: _examples/themes/legend_dash_dotted.py
        :include-source:
    """
    lw_, fs_, lh_ = _set_lw_fs_lh(linewidth, fontsize, legend_handlelength, **aliases)

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
    .. plot:: _examples/themes/legend_dashed.py
        :include-source:
    """
    lw_, fs_, lh_ = _set_lw_fs_lh(linewidth, fontsize, legend_handlelength, **aliases)

    total_points = fs_ * lh_ / lw_

    n_gaps = n_dashes - 1
    spacewidth = total_points / (n_gaps + n_dashes * ratio)
    dashwidth = ratio * spacewidth

    return 0.0, (dashwidth, spacewidth)


def add_abc(
    fig: Figure | None = None,
    xoffset_pts: ArrayLike = 2.0,
    yoffset_pts: ArrayLike = -12.0,
    anchor: Literal[
        "top left", "top right", "bottom left", "bottom right"
    ] = "top left",
    labels: str = "a;b;c;d;e;f;g;h;i;j;k;l;m;n;o;p;q;r;s;t;u;v;w;x;y;z",
    labels_sep: str = ";",
    pre: str = "(",
    post: str = ")",
    start_at: int = 0,
    rowsfirst: bool = True,
    **text_kwargs,
) -> dict[Axes, Text]:
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

    labels : str, optional
        A string of labels, where each label is seperated by `labels_sep`.

        If ``None``, use label of the respective axes
        (i.e., ``ax.get_label()``).

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

    .. plot:: _examples/themes/add_abc0.py
        :include-source:

    .. plot:: _examples/themes/add_abc1.py
        :include-source:

    .. plot:: _examples/themes/add_abc2.py
        :include-source:

    """

    fig = fig or plt.gcf()
    axs = _layout._get_sorted_axes_grid(fig)
    nrows, ncols = axs.shape

    valid_anchors = ["top left", "top right", "bottom left", "bottom right"]
    if anchor not in valid_anchors:
        err_msg = f"{anchor=}, but it needs to be one of {valid_anchors}"
        raise ValueError(err_msg)
    topbottom = anchor.split(" ")[0]
    leftright = anchor.split(" ")[1]

    # process offsets
    xoffsets_inch = np.asarray(xoffset_pts) / _layout.PTS_PER_INCH
    if xoffsets_inch.ndim == 0:
        xoffsets_inch = np.full(axs.shape, xoffsets_inch)
    elif xoffsets_inch.ndim == 1:
        xoffsets_inch = np.repeat(xoffsets_inch[np.newaxis, :], nrows, axis=0)
    if xoffsets_inch.shape != (nrows, ncols):
        msg = f"{xoffset_pts=} but must be either scalar or of shapes ({ncols},) or ({nrows}, {ncols})"
        raise ValueError(msg)
    yoffsets_inch = np.asarray(yoffset_pts) / _layout.PTS_PER_INCH
    if yoffsets_inch.ndim == 0:
        yoffsets_inch = np.full(axs.shape, yoffsets_inch)
    elif yoffsets_inch.ndim == 1:
        yoffsets_inch = np.repeat(yoffsets_inch[:, np.newaxis], ncols, axis=1)
    if yoffsets_inch.shape != (nrows, ncols):
        msg = f"{yoffset_pts=} but must be either scalar or of shapes ({nrows},) or ({nrows}, {ncols})"
        raise ValueError(msg)

    if labels is not None:
        labels_ = labels.split(labels_sep)
    out: dict[Axes, Text] = {}
    bboxes_inch = _layout._get_bboxes_inch_grid(axs)
    for (row, col), bbox in np.ndenumerate(bboxes_inch):
        if leftright == "left":
            x = xoffsets_inch[row, col] / bbox.width
        else:
            x = 1.0 + xoffsets_inch[row, col] / bbox.width
        if topbottom == "top":
            y = 1.0 + yoffsets_inch[row, col] / bbox.height
        else:
            y = yoffsets_inch[row, col] / bbox.height

        if labels is None:
            text = pre + str(axs[row, col].get_label()) + post
        else:
            idx = start_at + (ncols * row + col if rowsfirst else nrows * col + row)
            text = pre + labels_[idx] + post

        out[axs[row, col]] = axs[row, col].text(
            x, y, text, transform=axs[row, col].transAxes, **text_kwargs
        )

    return out


def square_polar_axes(ax: Axes | None = None, zorder: float = 0.98) -> None:
    """
    Format a polar axes to have a squared outline.

    Parameters
    ----------
    ax : :class:`matplotlib.axes.Axes`, optional
        If None, use last active axes.

    Examples
    --------

    .. plot:: _examples/themes/square_polar_axes.py
        :include-source:

    """
    ax = ax or plt.gca()
    ec = plt.rcParams["axes.edgecolor"]

    def circle_to_square_distance(theta_rad):
        h = 1.0
        max_cos_sin = np.maximum(np.abs(np.cos(theta_rad)), np.abs(np.sin(theta_rad)))
        return h / max_cos_sin - h

    ax.add_patch(
        patches.Rectangle(
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
