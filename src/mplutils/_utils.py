from .errors import AliasError
from .core import FONT_SCALINGS

import matplotlib.pyplot as plt


def normalize_lw_fs_lh(
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
        if fontsize_ in FONT_SCALINGS:
            fontsize_ = FONT_SCALINGS[fontsize_] * plt.rcParams["font.size"]
        else:
            raise ValueError("Invalid specifier for fontsize")

    return lw, fontsize_, lh
