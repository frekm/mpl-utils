import numpy as np
import pathlib
import os
import inspect
from numpy.typing import ArrayLike, NDArray
from typing import TypeVar, Generic, Sequence, Literal

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

DType = TypeVar("DType")


class Array(np.ndarray, Generic[DType]):
    def __getitem__(self, key) -> DType:
        return super().__getitem__(key)  # type: ignore


def centers_to_edges(
    centers: ArrayLike,
    lower: None | float = None,
    upper: None | float = None,
) -> NDArray[np.float64]:
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
    ftype: None | str | Sequence[str] = None,
    fig: None | Figure = None,
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
    xcenters: ArrayLike,
    ycenters: ArrayLike,
    z: ArrayLike,
    *,
    iteration_order: Literal["x_first", "y_first"] = "x_first",
    xmin: float | None = None,
    xmax: float | None = None,
    ymin: float | None = None,
    ymax: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
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
    x: ArrayLike,
    y: ArrayLike,
    start_at: float | Literal["auto"] = 0.0,
    xlim_lower: float | None = None,
    xlim_upper: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
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

    .. plot:: _examples/misc/convert_to_steps.py
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
