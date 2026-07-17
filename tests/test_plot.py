from unittest.mock import patch

import matplotlib
import pytest
import xeo

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from xeo.plot import _annotation_levels, _import_matplotlib


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_optional_matplotlib_dependency_has_a_clear_error():
    with patch.dict("sys.modules", {"matplotlib.pyplot": None}):
        with pytest.raises(ImportError, match=r"xeo\[plot\]"):
            _import_matplotlib()


def test_plot_bands_accepts_one_instrument_and_returns_axes():
    ax = xeo.plot_bands("MSI_S2A", title="Sentinel-2A bands")

    assert ax.get_title() == "Sentinel-2A bands"
    assert ax.get_xlabel() == "Wavelength (nm)"
    assert [tick.get_text() for tick in ax.get_yticklabels()] == ["MSI_S2A"]
    assert len(ax.patches) == 13
    assert len(ax.texts) == 13


def test_plot_bands_uses_sub_lanes_for_overlapping_bands():
    ax = xeo.plot_bands({"MSI_S2A": ["B8", "B8A"]})
    centers = {
        patch.get_y() + patch.get_height() / 2 for patch in ax.patches
    }

    assert len(centers) == 2


def test_plot_bands_accepts_matplotlib_styles_and_an_existing_axes():
    _, original_ax = plt.subplots()
    ax = xeo.plot_bands(
        {"MSI_S2A": [{"B4": {"color": "red", "alpha": 0.4}}]},
        ax=original_ax,
        band_labels=False,
    )

    assert ax is original_ax
    assert ax.patches[0].get_facecolor()[:3] == pytest.approx((1.0, 0.0, 0.0))
    assert ax.patches[0].get_alpha() == pytest.approx(0.4)
    assert not ax.texts


def test_plot_srf_uses_one_default_color_per_instrument_and_labels_peaks():
    ax = xeo.plot_srf(
        {
            "MSI_S2A": ["B3", "B4"],
            "OLI_L8": ["B3", "B4"],
        }
    )

    assert len(ax.lines) == 4
    assert ax.lines[0].get_color() == ax.lines[1].get_color()
    assert ax.lines[2].get_color() == ax.lines[3].get_color()
    assert ax.lines[0].get_color() != ax.lines[2].get_color()
    assert [text.get_text() for text in ax.texts] == ["B3", "B4", "B3", "B4"]
    assert [text.get_text() for text in ax.get_legend().get_texts()] == [
        "MSI_S2A",
        "OLI_L8",
    ]


def test_plot_srf_applies_line_styles_and_separates_nearby_peak_labels():
    ax = xeo.plot_srf(
        {
            "MSI_S2A": [
                {"B4": {"color": "red", "linestyle": "--", "linewidth": 3}}
            ],
            "MSI_S2B": "B4",
        }
    )

    assert ax.lines[0].get_color() == "red"
    assert ax.lines[0].get_linestyle() == "--"
    assert ax.lines[0].get_linewidth() == 3
    assert len(ax.texts) == 2


def test_plot_bands_accepts_a_list_of_per_instrument_dictionaries():
    ax = xeo.plot_bands(
        [
            {"MSI_S2A": [{"B4": {"color": "red"}}]},
            {"OLI_L8": [{"B5": {"color": "blue"}}]},
        ]
    )

    assert [tick.get_text() for tick in ax.get_yticklabels()] == [
        "MSI_S2A",
        "OLI_L8",
    ]
    assert ax.patches[0].get_facecolor()[:3] == pytest.approx((1.0, 0.0, 0.0))
    assert ax.patches[1].get_facecolor()[:3] == pytest.approx((0.0, 0.0, 1.0))


def test_plot_srf_accepts_a_list_of_per_instrument_dictionaries():
    ax = xeo.plot_srf(
        [
            {"MSI_S2A": [{"B4": {"color": "red", "linestyle": "--"}}]},
            {"OLI_L8": [{"B5": {"color": "blue", "linewidth": 3}}]},
        ]
    )

    assert [line.get_color() for line in ax.lines] == ["red", "blue"]
    assert ax.lines[0].get_linestyle() == "--"
    assert ax.lines[1].get_linewidth() == 3


def test_srf_annotation_levels_separate_colliding_labels():
    levels = _annotation_levels([(665, "B4"), (665, "B4")], 600, 700)

    assert levels == [0, 1]


@pytest.mark.parametrize("function_name", ["plot_bands", "plot_srf"])
def test_plotting_rejects_unknown_instrument_ids(function_name):
    with pytest.raises(ValueError, match="unknown instrument ids: UNKNOWN"):
        getattr(xeo, function_name)("UNKNOWN")


@pytest.mark.parametrize("function_name", ["plot_bands", "plot_srf"])
def test_plotting_rejects_unknown_band_ids(function_name):
    with pytest.raises(ValueError, match="unknown band ids for MSI_S2A: B99"):
        getattr(xeo, function_name)({"MSI_S2A": "B99"})


def test_plot_srf_rejects_instruments_without_srf_data():
    with pytest.raises(ValueError, match="has no spectral response function"):
        xeo.plot_srf("ALTUMPT_MICASENSE")


def test_list_of_instrument_dictionaries_rejects_duplicate_instruments():
    with pytest.raises(ValueError, match="duplicate instrument ids: MSI_S2A"):
        xeo.plot_bands(
            [
                {"MSI_S2A": "B3"},
                {"MSI_S2A": "B4"},
            ]
        )


def test_figsize_cannot_be_combined_with_existing_axes():
    _, ax = plt.subplots()

    with pytest.raises(ValueError, match="figsize cannot be used"):
        xeo.plot_bands("MSI_S2A", ax=ax, figsize=(8, 4))
