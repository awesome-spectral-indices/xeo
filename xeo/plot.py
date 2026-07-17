"""Plot spectral bands and spectral response functions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .axioms import instruments as catalogue_instruments

if TYPE_CHECKING:
    from matplotlib.axes import Axes


@dataclass(frozen=True)
class _BandSelection:
    band_id: str
    style: dict[str, Any]


InstrumentInput = (
    str
    | Sequence[
        str
        | Mapping[
            str,
            None
            | str
            | Sequence[str | Mapping[str, Mapping[str, Any]]]
            | Mapping[str, Mapping[str, Any]],
        ]
    ]
    | Mapping[
        str,
        None
        | str
        | Sequence[str | Mapping[str, Mapping[str, Any]]]
        | Mapping[str, Mapping[str, Any]],
    ]
)


def _import_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise ImportError(
            "Plotting requires Matplotlib. Install it with "
            "`python -m pip install 'xeo[plot]'`."
        ) from error
    return plt


def _parse_band_selection(value: Any) -> list[_BandSelection] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return [_BandSelection(value, {})]

    if isinstance(value, Mapping):
        items: Sequence[Any] = [
            {band_id: style} for band_id, style in value.items()
        ]
    elif isinstance(value, Sequence):
        items = value
    else:
        raise TypeError(
            "band selections must be a band id, a sequence of band ids, "
            "or styled band dictionaries"
        )

    if not items:
        raise ValueError("band selections must not be empty")

    selections: list[_BandSelection] = []
    for item in items:
        if isinstance(item, str):
            selections.append(_BandSelection(item, {}))
            continue
        if not isinstance(item, Mapping) or len(item) != 1:
            raise TypeError(
                "each styled band must be a one-item dictionary such as "
                "{'B4': {'color': 'red'}}"
            )

        band_id, style = next(iter(item.items()))
        if not isinstance(band_id, str) or not isinstance(style, Mapping):
            raise TypeError("styled bands must map a band id to a style dictionary")
        selections.append(_BandSelection(band_id, dict(style)))

    band_ids = [selection.band_id for selection in selections]
    duplicates = sorted(
        band_id for band_id in set(band_ids) if band_ids.count(band_id) > 1
    )
    if duplicates:
        raise ValueError(f"duplicate band selections: {', '.join(duplicates)}")
    return selections


def _normalise_instruments(
    value: InstrumentInput,
) -> list[tuple[str, list[_BandSelection] | None]]:
    if isinstance(value, str):
        requested = [(value, None)]
    elif isinstance(value, Mapping):
        requested = [
            (instrument_id, _parse_band_selection(selection))
            for instrument_id, selection in value.items()
        ]
    elif isinstance(value, Sequence):
        requested = []
        for item in value:
            if isinstance(item, str):
                requested.append((item, None))
            elif isinstance(item, Mapping):
                requested.extend(
                    (
                        instrument_id,
                        _parse_band_selection(selection),
                    )
                    for instrument_id, selection in item.items()
                )
            else:
                raise TypeError(
                    "instrument sequences must contain ids or dictionaries "
                    "of band selections"
                )
    else:
        raise TypeError(
            "instruments must be an instrument id, a sequence of ids, "
            "a dictionary of band selections, or a sequence of such dictionaries"
        )

    if not requested:
        raise ValueError("at least one instrument id is required")

    instrument_ids = [instrument_id for instrument_id, _ in requested]
    if not all(isinstance(instrument_id, str) for instrument_id in instrument_ids):
        raise TypeError("instrument ids must be strings")

    duplicates = sorted(
        instrument_id
        for instrument_id in set(instrument_ids)
        if instrument_ids.count(instrument_id) > 1
    )
    if duplicates:
        raise ValueError(f"duplicate instrument ids: {', '.join(duplicates)}")

    unknown = [
        instrument_id
        for instrument_id in instrument_ids
        if instrument_id not in catalogue_instruments
    ]
    if unknown:
        raise ValueError(f"unknown instrument ids: {', '.join(unknown)}")
    return requested


def _make_axes(plt, ax: Axes | None, figsize: tuple[float, float] | None):
    if ax is not None:
        if figsize is not None:
            raise ValueError("figsize cannot be used when ax is provided")
        return ax
    _, ax = plt.subplots(figsize=figsize)
    return ax


def _instrument_colors(plt, count: int) -> list[str]:
    colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["C0"])
    return [colors[index % len(colors)] for index in range(count)]


def _selected_bands(
    instrument_id: str,
    available_band_ids: Sequence[str],
    selection: list[_BandSelection] | None,
) -> list[_BandSelection]:
    if selection is None:
        return [_BandSelection(band_id, {}) for band_id in available_band_ids]

    available = set(available_band_ids)
    unknown = [item.band_id for item in selection if item.band_id not in available]
    if unknown:
        raise ValueError(
            f"unknown band ids for {instrument_id}: {', '.join(unknown)}"
        )
    return selection


def _interval_lanes(
    intervals: list[tuple[float, float, _BandSelection]],
) -> tuple[list[tuple[float, float, _BandSelection, int]], int]:
    lane_ends: list[float] = []
    assigned = []
    for start, end, selection in sorted(intervals, key=lambda item: (item[0], item[1])):
        for lane, lane_end in enumerate(lane_ends):
            if start >= lane_end:
                lane_ends[lane] = end
                break
        else:
            lane = len(lane_ends)
            lane_ends.append(end)
        assigned.append((start, end, selection, lane))
    return assigned, len(lane_ends)


def plot_bands(
    instruments: InstrumentInput,
    *,
    ax: Axes | None = None,
    figsize: tuple[float, float] | None = None,
    title: str | None = "Spectral bands",
    band_labels: bool = True,
) -> Axes:
    """Plot instrument band ranges along the wavelength axis.

    Overlapping bands are placed in compact sub-lanes within the instrument's
    row. Non-overlapping bands reuse the same lane.

    Parameters
    ----------
    instruments : str, sequence, or dict
        One instrument id, several ids, a dictionary mapping instrument ids to
        selected bands, or a list of such dictionaries. A selection can be one
        band id, a sequence of band ids, or styled bands such as
        ``{"MSI_S2A": [{"B4": {"color": "red", "linewidth": 2}}]}``.
        A list of dictionaries can define different selections and styles for
        each instrument. Style dictionaries accept Matplotlib ``barh`` keyword
        arguments.
    ax : matplotlib.axes.Axes, optional
        Axes on which to draw. A new figure and axes are created by default.
    figsize : tuple of float, optional
        Figure size in inches when creating new axes. It cannot be combined
        with ``ax``.
    title : str or None, default="Spectral bands"
        Axes title. Use ``None`` to leave the title unset.
    band_labels : bool, default=True
        Whether to place band ids on their wavelength ranges.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the plot.

    Examples
    --------
    >>> import xeo
    >>> ax = xeo.plot_bands({"MSI_S2A": ["B2", "B3", "B4"]})
    """

    plt = _import_matplotlib()
    requested = _normalise_instruments(instruments)
    if figsize is None and ax is None:
        figsize = (10, max(3.0, 1.15 * len(requested)))
    ax = _make_axes(plt, ax, figsize)
    colors = _instrument_colors(plt, len(requested))

    for row, ((instrument_id, selection), instrument_color) in enumerate(
        zip(requested, colors)
    ):
        frame = catalogue_instruments[instrument_id].bands()
        if frame is None:
            raise ValueError(f"{instrument_id} has no spectral bands")

        selected = _selected_bands(instrument_id, list(frame.index), selection)
        intervals = []
        for item in selected:
            center = float(frame.loc[item.band_id, "center_wavelength"])
            bandwidth = float(frame.loc[item.band_id, "bandwidth"])
            intervals.append(
                (center - bandwidth / 2, center + bandwidth / 2, item)
            )

        assigned, lane_count = _interval_lanes(intervals)
        lane_height = 0.8 / lane_count
        for start, end, item, lane in assigned:
            y = row - 0.4 + lane_height * (lane + 0.5)
            style = {"alpha": 0.8}
            style.update(item.style)
            if not {"color", "facecolor", "fc"}.intersection(style):
                style["color"] = instrument_color

            ax.barh(
                y,
                end - start,
                left=start,
                height=lane_height * 0.82,
                align="center",
                **style,
            )
            if band_labels:
                ax.text(
                    (start + end) / 2,
                    y,
                    item.band_id,
                    ha="center",
                    va="center",
                    fontsize=8,
                    clip_on=True,
                )

    ax.set_yticks(range(len(requested)), [item[0] for item in requested])
    ax.set_ylim(len(requested) - 0.4, -0.6)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Instrument")
    if title is not None:
        ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    return ax


def _annotation_levels(
    annotations: list[tuple[float, str]], x_min: float, x_max: float
) -> list[int]:
    span = x_max - x_min or 1.0
    lane_ends: list[float] = []
    levels = [0] * len(annotations)

    for index, (x, text) in sorted(
        enumerate(annotations), key=lambda item: item[1][0]
    ):
        center = (x - x_min) / span
        half_width = max(0.015, 0.0045 * len(text))
        start = center - half_width
        end = center + half_width
        for level, lane_end in enumerate(lane_ends):
            if start > lane_end + 0.005:
                lane_ends[level] = end
                break
        else:
            level = len(lane_ends)
            lane_ends.append(end)
        levels[index] = level
    return levels


def _trim_zero_response(curve, band_id: str):
    nonzero_positions = [
        position
        for position, value in enumerate(curve[band_id])
        if value != 0
    ]
    if not nonzero_positions:
        return curve

    start = max(nonzero_positions[0] - 1, 0)
    stop = min(nonzero_positions[-1] + 2, len(curve))
    return curve.iloc[start:stop]


def plot_srf(
    instruments: InstrumentInput,
    *,
    ax: Axes | None = None,
    figsize: tuple[float, float] | None = None,
    title: str | None = "Spectral response functions",
    band_labels: bool = True,
    legend: bool = True,
) -> Axes:
    """Plot spectral response functions for one or more instruments.

    Curves use one default color per instrument. Band ids are placed near their
    response peaks and distributed across vertical label levels when nearby
    peaks would otherwise collide.

    Parameters
    ----------
    instruments : str, sequence, or dict
        One instrument id, several ids, a dictionary mapping instrument ids to
        selected bands, or a list of such dictionaries. A selection can be one
        band id, a sequence of band ids, or styled bands such as
        ``{"MSI_S2A": [{"B4": {"color": "red", "linestyle": "--"}}]}``.
        A list of dictionaries can define different selections and styles for
        each instrument. Style dictionaries accept Matplotlib ``plot`` keyword
        arguments.
    ax : matplotlib.axes.Axes, optional
        Axes on which to draw. A new figure and axes are created by default.
    figsize : tuple of float, optional
        Figure size in inches when creating new axes. It cannot be combined
        with ``ax``.
    title : str or None, default="Spectral response functions"
        Axes title. Use ``None`` to leave the title unset.
    band_labels : bool, default=True
        Whether to place band ids near the response peaks.
    legend : bool, default=True
        Whether to add an instrument legend.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the plot.

    Examples
    --------
    >>> import xeo
    >>> ax = xeo.plot_srf({"MSI_S2A": ["B2", "B3", "B4"]})
    """

    plt = _import_matplotlib()
    requested = _normalise_instruments(instruments)
    ax = _make_axes(plt, ax, figsize or ((10, 6) if ax is None else None))
    colors = _instrument_colors(plt, len(requested))
    annotations: list[tuple[float, float, str, Any]] = []

    for (instrument_id, selection), instrument_color in zip(requested, colors):
        frame = catalogue_instruments[instrument_id].srf()
        if frame is None:
            raise ValueError(f"{instrument_id} has no spectral response function")

        available_band_ids = [
            column for column in frame.columns if column != "wavelength"
        ]
        selected = _selected_bands(
            instrument_id, available_band_ids, selection
        )

        for index, item in enumerate(selected):
            curve = frame[["wavelength", item.band_id]].dropna()
            if curve.empty:
                raise ValueError(
                    f"{instrument_id}.{item.band_id} has no spectral response values"
                )
            curve = _trim_zero_response(curve, item.band_id)

            style = dict(item.style)
            if not {"color", "c"}.intersection(style):
                style["color"] = instrument_color
            style.setdefault("label", instrument_id if index == 0 else "_nolegend_")
            (line,) = ax.plot(
                curve["wavelength"],
                curve[item.band_id],
                **style,
            )

            peak_index = curve[item.band_id].idxmax()
            annotations.append(
                (
                    float(curve.loc[peak_index, "wavelength"]),
                    float(curve.loc[peak_index, item.band_id]),
                    item.band_id,
                    line.get_color(),
                )
            )

    if band_labels and annotations:
        x_min, x_max = ax.get_xlim()
        levels = _annotation_levels(
            [(x, band_id) for x, _, band_id, _ in annotations], x_min, x_max
        )
        for (x, y, band_id, color), level in zip(annotations, levels):
            ax.annotate(
                band_id,
                xy=(x, y),
                xytext=(0, 6 + level * 11),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
                clip_on=False,
            )
        y_min, y_max = ax.get_ylim()
        y_span = y_max - y_min or 1.0
        label_headroom = 0.08 + max(levels) * 0.06
        ax.set_ylim(y_min, y_max + y_span * label_headroom)

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Spectral response")
    if title is not None:
        ax.set_title(title)
    ax.grid(alpha=0.25)
    if legend:
        ax.legend(title="Instrument")
    return ax


__all__ = ["plot_bands", "plot_srf"]
