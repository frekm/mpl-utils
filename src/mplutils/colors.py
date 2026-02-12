import typing
import dataclasses

ColorsLike = typing.Literal[
    "#AE1117",
    "#008081",
    "#376EB5",
    "#D4B9DA",
    "#ED7800",
    "#FCE205",
    "#EFFD5F",
    "#E4CD05",
    "#CA8DFD",
    "#9300FF",
    "#3BB143",
    "#007F00",
    "#0B6623",
    "#9D9D9C",
    "#000000",
    "#FFFFFF",
]


@dataclasses.dataclass(frozen=True)
class Colors:
    red: typing.Literal["#AE1117"] = "#AE1117"
    teal: typing.Literal["#008081"] = "#008081"
    blue: typing.Literal["#376EB5"] = "#376EB5"
    pink: typing.Literal["#D4B9DA"] = "#D4B9DA"
    orange: typing.Literal["#ED7800"] = "#ED7800"
    yellow: typing.Literal["#FCE205"] = "#FCE205"
    lemon: typing.Literal["#EFFD5F"] = "#EFFD5F"
    corn: typing.Literal["#E4CD05"] = "#E4CD05"
    purple: typing.Literal["#CA8DFD"] = "#CA8DFD"
    darkpurple: typing.Literal["#9300FF"] = "#9300FF"
    lightgreen: typing.Literal["#3BB143"] = "#3BB143"
    green: typing.Literal["#007F00"] = "#007F00"
    darkgreen: typing.Literal["#0B6623"] = "#0B6623"
    grey: typing.Literal["#9D9D9C"] = "#9D9D9C"
    black: typing.Literal["#000000"] = "#000000"
    white: typing.Literal["#FFFFFF"] = "#FFFFFF"

    @typing.overload
    def __getitem__(self, i: typing.Literal[0]) -> typing.Literal["#AE1117"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[1]) -> typing.Literal["#008081"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[2]) -> typing.Literal["#376EB5"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[3]) -> typing.Literal["#D4B9DA"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[4]) -> typing.Literal["#ED7800"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[5]) -> typing.Literal["#FCE205"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[6]) -> typing.Literal["#EFFD5F"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[7]) -> typing.Literal["#E4CD05"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[8]) -> typing.Literal["#CA8DFD"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[9]) -> typing.Literal["#9300FF"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[10]) -> typing.Literal["#3BB143"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[11]) -> typing.Literal["#007F00"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[12]) -> typing.Literal["#0B6623"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[13]) -> typing.Literal["#9D9D9C"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[14]) -> typing.Literal["#000000"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[15]) -> typing.Literal["#FFFFFF"]: ...
    @typing.overload
    def __getitem__(self, i: int) -> str: ...
    @typing.overload
    def __getitem__(self, i: slice) -> tuple[str, ...]: ...

    def __getitem__(
        self,
        i: (
            typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
            | int
            | slice
        ),
    ) -> ColorsLike | tuple[str, ...] | str:
        items = (
            self.red,
            self.teal,
            self.blue,
            self.pink,
            self.orange,
            self.yellow,
            self.lemon,
            self.corn,
            self.purple,
            self.darkpurple,
            self.lightgreen,
            self.green,
            self.darkgreen,
            self.grey,
            self.black,
            self.white,
        )
        return items[i]

    def __len__(self) -> int:
        return 16

    def __iter__(
        self,
    ) -> typing.Iterator[ColorsLike]:
        items = (
            self.red,
            self.teal,
            self.blue,
            self.pink,
            self.orange,
            self.yellow,
            self.lemon,
            self.corn,
            self.purple,
            self.darkpurple,
            self.lightgreen,
            self.green,
            self.darkgreen,
            self.grey,
            self.black,
            self.white,
        )
        return iter(items)


@dataclasses.dataclass(frozen=True)
class OkabeItoPalette:
    blue: typing.Literal["#56b4e9"] = "#56b4e9"
    orange: typing.Literal["#e69f00"] = "#e69f00"
    green: typing.Literal["#009e73"] = "#009e73"
    yellow: typing.Literal["#f0e442"] = "#f0e442"
    darkblue: typing.Literal["#0072b2"] = "#0072b2"
    darkorange: typing.Literal["#d55e00"] = "#d55e00"
    violet: typing.Literal["#cc79a7"] = "#cc79a7"

    @typing.overload
    def __getitem__(self, i: typing.Literal[0]) -> typing.Literal["#56b4e9"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[1]) -> typing.Literal["#e69f00"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[2]) -> typing.Literal["#009e73"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[3]) -> typing.Literal["#f0e442"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[4]) -> typing.Literal["#0072b2"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[5]) -> typing.Literal["#d55e00"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[6]) -> typing.Literal["#cc79a7"]: ...
    @typing.overload
    def __getitem__(self, i: int) -> str: ...
    @typing.overload
    def __getitem__(self, i: slice) -> tuple[str, ...]: ...

    def __getitem__(self, i: typing.Literal[0, 1, 2, 3, 4, 5, 6] | slice | int) -> (
        typing.Literal[
            "#56b4e9",
            "#e69f00",
            "#009e73",
            "#f0e442",
            "#0072b2",
            "#d55e00",
            "#cc79a7",
        ]
        | tuple[str, ...]
        | str
    ):
        items = (
            self.blue,
            self.orange,
            self.green,
            self.yellow,
            self.darkblue,
            self.darkorange,
            self.violet,
        )
        return items[i]

    def __len__(self) -> int:
        return 7

    def __iter__(
        self,
    ) -> typing.Iterator[
        typing.Literal[
            "#56b4e9",
            "#e69f00",
            "#009e73",
            "#f0e442",
            "#0072b2",
            "#d55e00",
            "#cc79a7",
        ]
    ]:
        items = (
            self.blue,
            self.orange,
            self.green,
            self.yellow,
            self.darkblue,
            self.darkorange,
            self.violet,
        )
        return iter(items)


@dataclasses.dataclass(frozen=True)
class OkabeItoMutedPalette:
    sandstone: typing.Literal["#D9CBBE"] = "#D9CBBE"
    mist: typing.Literal["#C3CDD6"] = "#C3CDD6"
    mauve: typing.Literal["#CAB9C1"] = "#CAB9C1"
    ivory: typing.Literal["#F0EDD6"] = "#F0EDD6"

    @typing.overload
    def __getitem__(self, i: typing.Literal[0]) -> typing.Literal["#D9CBBE"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[1]) -> typing.Literal["#C3CDD6"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[2]) -> typing.Literal["#CAB9C1"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[3]) -> typing.Literal["#F0EDD6"]: ...
    @typing.overload
    def __getitem__(self, i: int) -> str: ...
    @typing.overload
    def __getitem__(self, i: slice) -> tuple[str, ...]: ...

    def __getitem__(
        self, i: typing.Literal[0, 1, 2, 3] | slice | int
    ) -> (
        typing.Literal["#D9CBBE", "#C3CDD6", "#CAB9C1", "#F0EDD6"]
        | tuple[str, ...]
        | str
    ):
        items = (self.sandstone, self.mist, self.mauve, self.ivory)
        return items[i]

    def __len__(self) -> int:
        return 4

    def __iter__(
        self,
    ) -> typing.Iterator[
        typing.Literal[
            "#D9CBBE",
            "#C3CDD6",
            "#CAB9C1",
            "#F0EDD6",
        ]
    ]:
        items = (self.sandstone, self.mist, self.mauve, self.ivory)
        return iter(items)


@dataclasses.dataclass(frozen=True)
class OkabeItoAccentPalette:
    blue: typing.Literal["#044F7E"] = "#044F7E"
    red: typing.Literal["#954000"] = "#954000"
    green: typing.Literal["#026D4E"] = "#026D4E"

    @typing.overload
    def __getitem__(self, i: typing.Literal[0]) -> typing.Literal["#044F7E"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[1]) -> typing.Literal["#954000"]: ...
    @typing.overload
    def __getitem__(self, i: typing.Literal[2]) -> typing.Literal["#026D4E"]: ...
    @typing.overload
    def __getitem__(self, i: int) -> str: ...
    @typing.overload
    def __getitem__(self, i: slice) -> tuple[str, ...]: ...

    def __getitem__(
        self, i: typing.Literal[0, 1, 2, 3] | slice | int
    ) -> typing.Literal["#044F7E", "#954000", "#026D4E"] | tuple[str, ...] | str:
        items = (self.blue, self.red, self.green)
        return items[i]

    def __len__(self) -> int:
        return 3

    def __iter__(
        self,
    ) -> typing.Iterator[typing.Literal["#044F7E", "#954000", "#026D4E"]]:
        items = (self.blue, self.red, self.green)
        return iter(items)
