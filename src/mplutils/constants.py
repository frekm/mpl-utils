import typing as tp
import math

from ._constants import FigureWidths, Colors, OkabeIto, OkabeItoAccent, OkabeItoMuted

MM_PER_INCH: tp.Final = 25.4
PTS_PER_INCH: tp.Final = 72.0
PTS_PER_MM: tp.Final = PTS_PER_INCH / MM_PER_INCH
GOLDENRATIO = 1.0 + math.sqrt(5.0) / 2.0  # 1.618

FIG_WIDTHS: tp.Final = FigureWidths(
    nature_1col=3.54,
    nature_2col=7.09,
    prl_1col=3.375,
    prl_2col=6.75,
    science_1col=2.25,
    science_2col=4.75,
    science_3col=7.25,
    a4=210.0 / MM_PER_INCH,
    a5=148.0 / MM_PER_INCH,
)

COLORS = Colors(
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

OKABE_ITO = OkabeIto(
    "#56b4e9",
    "#e69f00",
    "#009e73",
    "#f0e442",
    "#0072b2",
    "#d55e00",
    "#cc79a7",
    "#000000",
)

OKABE_ITO_MUTED = OkabeItoMuted(
    "#D9CBBE",
    "#C3CDD6",
    "#CAB9C1",
    "#F0EDD6",
)


OKABE_ITO_ACCENT = OkabeItoAccent(
    "#044F7E",
    "#954000",
    "#026D4E",
)
