from .layout import (
    set_axes_size,
    set_colorbar_pad,
    set_colorbar_thickness,
    align_axes_horizontally,
    align_axes_vertically,
)

from .constants import (
    FIG_WIDTHS,
    COLORS,
    OKABE_ITO,
    OKABE_ITO_ACCENT,
    OKABE_ITO_MUTED,
    MM_PER_INCH,
    PTS_PER_INCH,
    PTS_PER_MM,
)

from .errors import (
    InvalidFigureError,
    AliasError,
)

from .utils import (
    add_colorbar,
    savefig,
    for_pcolormesh,
    centers_to_edges,
    convert_to_steps,
    set_color_cycle,
    set_latex_backend,
    crop_colormap,
    textwithbox,
    dotted,
    dash_dotted,
    dashed,
    add_abc,
    square_polar_axes,
)

from .layout_engine import FixedLayoutEngine

from ._version import __version__
