from typing import Literal
from matplotlib.axes import Axes
from matplotlib.projections import PolarAxes
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox
from matplotlib.backend_bases import RendererBase
import numpy as np

from . import _core as core
from . import constants


def update_colorbar(cax: Axes, parent_bbox_old: Bbox, parent_bbox_new: Bbox) -> None:
    cbinfo = getattr(cax, "_colorbar_info", None)
    if cbinfo is None:
        raise ValueError("cannot retrieve colorbar info")
    cax.set_aspect("auto")
    cax.set_box_aspect(None)
    loc = cbinfo["location"]
    bbox = cax.get_position()
    if loc in ("left", "right"):
        dh = parent_bbox_new.height - parent_bbox_old.height
        dy = parent_bbox_new.y0 - parent_bbox_old.y0
        if loc == "left":
            dx = parent_bbox_new.x0 - parent_bbox_old.x0
        else:  # right
            dx = parent_bbox_new.x1 - parent_bbox_old.x1
        pos = Bbox.from_bounds(bbox.x0 + dx, bbox.y0 + dy, bbox.width, bbox.height + dh)
    else:  # top bottom
        dw = parent_bbox_new.width - parent_bbox_old.width
        dx = parent_bbox_new.x0 - parent_bbox_old.x0
        if loc == "top":
            dy = parent_bbox_old.y1 - parent_bbox_new.y1
        else:  # bottom
            dy = parent_bbox_new.y0 - parent_bbox_old.y0
        pos = Bbox.from_bounds(bbox.x0 + dx, bbox.y0 + dy, bbox.width + dw, bbox.height)
    cax.set_position(pos)
    cbinfo["aspect"] = pos.height / pos.width


def get_fixed_aspect(fig: Figure, ax: Axes) -> float | None:
    def calc_aspect() -> float:
        fw, fh = fig.get_size_inches()
        pos = ax.get_position()
        return (pos.height * fh) / (pos.width * fw)

    old_adjustable = ax.get_adjustable()
    fixed_aspect = None
    try:
        # matplotlib raises a ValueError if set_adjustable("datalim") is called
        # on an axes with a fixed aspect ratio (e.g., polar axes).
        ax.set_adjustable("datalim")
    except ValueError:
        fixed_aspect = calc_aspect()
    if ax.get_aspect() != "auto" and old_adjustable == "box" and fixed_aspect is None:
        fixed_aspect = calc_aspect()
    ax.set_adjustable(old_adjustable)
    return fixed_aspect


def set_axes_width_inch(
    fig: Figure,
    ax: Axes,
    width_inch: float,
    anchor: tuple[float, float],
) -> None:
    old_pos = ax.get_position().frozen()
    fw, fh = fig.get_size_inches()
    aspect = get_fixed_aspect(fig, ax)
    width = width_inch / fw
    height = old_pos.height if aspect is None else aspect * width_inch / fh
    fx, fy = anchor
    fixed_x = old_pos.x0 + fx * old_pos.width
    fixed_y = old_pos.y0 + fy * old_pos.height
    new_x0 = fixed_x - fx * width
    new_y0 = fixed_y - fy * height
    new_pos = Bbox.from_bounds(new_x0, new_y0, width, height)
    ax.set_position(new_pos)
    caxes = getattr(ax, "_colorbars", [])
    for cax in caxes:
        update_colorbar(cax, old_pos, new_pos)


def set_axes_height_inch(
    fig: Figure,
    ax: Axes,
    height_inch: float,
    anchor: tuple[float, float],
) -> None:
    fw, fh = fig.get_size_inches()
    old_pos = ax.get_position().frozen()
    aspect = get_fixed_aspect(fig, ax)
    height = height_inch / fh
    width = old_pos.width if aspect is None else height_inch / fw / aspect
    fx, fy = anchor
    fixed_x = old_pos.x0 + fx * old_pos.width
    fixed_y = old_pos.y0 + fy * old_pos.height
    new_x0 = fixed_x - fx * width
    new_y0 = fixed_y - fy * height
    new_pos = Bbox.from_bounds(new_x0, new_y0, width, height)
    ax.set_position(new_pos)
    caxes = getattr(ax, "_colorbars", [])
    for cax in caxes:
        update_colorbar(cax, old_pos, new_pos)


def normalize_anchor(anchor) -> tuple[float, float]:
    coefs = {
        "C": (0.5, 0.5),
        "SW": (0, 0),
        "S": (0.5, 0),
        "SE": (1.0, 0),
        "E": (1.0, 0.5),
        "NE": (1.0, 1.0),
        "N": (0.5, 1.0),
        "NW": (0, 1.0),
        "W": (0, 0.5),
    }
    if anchor in coefs:
        anchor = coefs[anchor]
    return anchor


def normalize_width_height(
    w: float,
    h: float | None,
    aspect: float | Literal["auto"],
) -> tuple[float, float]:

    if h is None:
        h = w if aspect == "auto" else w * aspect
    elif aspect != "auto" and h / w != aspect:
        raise ValueError("width, height, and aspect-ratio contradict each other")
    return w, h


def set_colorbar_thickness_inch(fig, cax: Axes, thickness_inch: float) -> None:
    if not isinstance(fig, Figure):
        raise ValueError("colorbar must be part of a figure")
    cb_info = getattr(cax, "_colorbar_info", None)
    if cb_info is None:
        raise ValueError("could not retrieve colorbar info")
    parents: list[Axes] = cb_info["parents"]
    if len(parents) != 1:
        raise ValueError("colorbar must belong to exactly one axes")
    parent = parents[0]
    location = cb_info["location"]
    pos_parent = parent.get_position()
    pos_cax = cax.get_position()
    fw, fh = fig.get_size_inches()
    cax.set_aspect("auto")
    cax.set_box_aspect(None)
    if location in ("left", "right"):
        size = thickness_inch / fw
        cb_info["fraction"] = size / pos_parent.width
        cb_info["aspect"] = size / pos_cax.height
        if location == "left":
            cax.set_position((pos_cax.x1 - size, pos_cax.y0, size, pos_cax.height))
        else:  # right
            cax.set_position((pos_cax.x0, pos_cax.y0, size, pos_cax.height))
    else:  # top bottom
        size = thickness_inch / fh
        cb_info["fraction"] = size / pos_parent.height
        cb_info["aspect"] = pos_cax.width / size
        if location == "top":
            cax.set_position((pos_cax.x0, pos_cax.y0, pos_cax.width, size))
        else:  # bottom
            cax.set_position((pos_cax.x0, pos_cax.y1 - size, pos_cax.width, size))


def set_colorbar_pad_inch(fig, cax, pad_inch: float) -> None:
    if not isinstance(fig, Figure):
        raise ValueError("colorbar must be part of a figure")
    cb_info = getattr(cax, "_colorbar_info", None)
    if cb_info is None:
        raise ValueError("could not retrieve colorbar info")
    parents: list[Axes] = cb_info["parents"]
    if len(parents) != 1:
        raise ValueError("colorbar must belong to exactly one axes")
    parent = parents[0]
    pos_parent = parent.get_position()
    location = cb_info["location"]
    pos_cax = cax.get_position()
    fw, fh = fig.get_size_inches()
    if location in ("left", "right"):
        gap = pad_inch / fw
        if location == "left":
            x0 = pos_parent.x0 - gap - pos_cax.width
            pos = Bbox.from_bounds(x0, pos_cax.y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
        else:  # right
            x0 = pos_parent.x1 + gap
            pos = Bbox.from_bounds(x0, pos_cax.y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
    else:  # top bottom
        gap = pad_inch / fh
        if location == "top":
            y0 = pos_parent.y1 + gap
            pos = Bbox.from_bounds(pos_cax.x0, y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
        else:  # bottom
            y0 = pos_parent.y0 - gap - pos_cax.height
            pos = Bbox.from_bounds(pos_cax.x0, y0, pos_cax.width, pos_cax.height)
            cax.set_position(pos)
    cb_info["pad"] = gap


def get_renderer(fig: Figure) -> RendererBase:
    fig.canvas.draw()
    method = getattr(fig, "_get_renderer", None)
    msg = "cannot get renderer for figure for current backend"
    if method is None:
        raise ValueError(msg)
    renderer = method()
    if not isinstance(renderer, RendererBase):
        raise ValueError(msg)
    return renderer
