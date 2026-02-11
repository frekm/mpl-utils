import typing as tp


class FigureWidths(tp.NamedTuple):
    nature_1col: float
    nature_2col: float
    prl_1col: float
    prl_2col: float
    science_1col: float
    science_2col: float
    science_3col: float
    a4: float
    a5: float


class Colors(tp.NamedTuple):
    red: tp.Literal["#AE1117"]
    teal: tp.Literal["#008081"]
    blue: tp.Literal["#376EB5"]
    green: tp.Literal["#007F00"]
    grey: tp.Literal["#9D9D9C"]
    orange: tp.Literal["#ED7800"]
    pink: tp.Literal["#D4B9DA"]
    yellow: tp.Literal["#FCE205"]
    lemon: tp.Literal["#EFFD5F"]
    corn: tp.Literal["#E4CD05"]
    purple: tp.Literal["#CA8DFD"]
    dark_purple: tp.Literal["#9300FF"]
    forest_green: tp.Literal["#0B6623"]
    bright_green: tp.Literal["#3BB143"]


class OkabeIto(tp.NamedTuple):
    blue: tp.Literal["#56b4e9"]
    orange: tp.Literal["#e69f00"]
    green: tp.Literal["#009e73"]
    yellow: tp.Literal["#f0e442"]
    darkblue: tp.Literal["#0072b2"]
    darkorange: tp.Literal["#d55e00"]
    violet: tp.Literal["#cc79a7"]
    black: tp.Literal["#000000"]


class OkabeItoMuted(tp.NamedTuple):
    sandstone: tp.Literal["#D9CBBE"]
    mist: tp.Literal["#C3CDD6"]
    mauve: tp.Literal["#CAB9C1"]
    ivory: tp.Literal["#F0EDD6"]


class OkabeItoAccent(tp.NamedTuple):
    blue: tp.Literal["#044F7E"]
    red: tp.Literal["#954000"]
    green: tp.Literal["#026D4E"]
