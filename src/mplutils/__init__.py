from .layout import (
    set_axes_size,
    set_colorbar_pad,
    set_colorbar_thickness,
    align_axes_horizontally,
    align_axes_vertically,
    get_axes_margins,
)

from .colors import (
    Colors,
    OkabeItoPalette,
    OkabeItoMutedPalette,
    OkabeItoAccentPalette,
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

from . import constants as constants

from .layout_engine import FixedLayoutEngine

from ._version import __version__
