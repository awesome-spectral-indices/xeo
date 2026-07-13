import json
from importlib.resources import files
from io import StringIO

import pandas as pd
import pytest
import xeo
from rich.console import Console


def test_public_package_metadata():
    assert xeo.__version__ == "2026.2.0"
    assert xeo.__all__ == [
        "Catalogue",
        "Instrument",
        "Instruments",
        "catalogue",
        "instruments",
    ]


def test_catalogue_uses_one_shared_instrument_collection():
    assert isinstance(xeo.catalogue, xeo.Catalogue)
    assert isinstance(xeo.instruments, xeo.Instruments)
    assert xeo.catalogue.instruments is xeo.instruments
    assert xeo.instruments["MSI_S2A"] is xeo.instruments.MSI_S2A


def test_instrument_metadata_is_available_as_attributes():
    instrument = xeo.instruments.MSI_S2A

    assert isinstance(instrument, xeo.Instrument)
    assert instrument.id == "MSI_S2A"
    assert instrument.name == "MultiSpectral Instrument"
    assert instrument.acronym == "MSI"
    assert instrument.operator == ["ESA", "Copernicus"]
    assert instrument.platform == ["Sentinel-2A"]
    assert instrument.platform_type == "satellite"
    assert instrument.status == "operational"
    assert "spectral" in instrument.extension_names
    assert instrument.extensions == instrument.data["extensions"]


def test_raw_catalogue_data_remains_json_serializable():
    raw_instrument = xeo.catalogue.data["instruments"]["MSI_S2A"]

    assert isinstance(raw_instrument, dict)
    assert json.loads(json.dumps(xeo.catalogue.data))["name"] == xeo.catalogue.name


def test_to_dict_returns_independent_data():
    instrument = xeo.instruments.MSI_S2A
    instrument_data = instrument.to_dict()
    catalogue_data = xeo.catalogue.to_dict()

    instrument_data["status"] = "changed"
    catalogue_data["name"] = "changed"

    assert instrument.status == "operational"
    assert xeo.catalogue.name == "Awesome Earth Observation Instruments"


def test_representations_are_concise():
    instrument = xeo.instruments.MSI_S2A

    assert repr(instrument) == "Instrument(MSI_S2A: MultiSpectral Instrument)"
    assert str(instrument) == "MSI_S2A: MultiSpectral Instrument"
    assert repr(xeo.instruments).startswith("Instruments(['ALTUMAL04_lte_MICASENSE'")
    assert "spectral_response_function" not in repr(instrument)
    assert len(repr(xeo.instruments)) < 2_000


def test_bands_returns_an_indexed_dataframe():
    instrument = xeo.instruments.MSI_S2A
    bands = instrument.bands()

    assert instrument.has_bands
    assert isinstance(bands, pd.DataFrame)
    assert bands.index.name == "band"
    assert list(bands.index) == list(instrument.extensions["spectral"]["bands"])
    assert {"center_wavelength", "bandwidth"}.issubset(bands.columns)


def test_srf_returns_a_dataframe_when_available():
    instrument = xeo.instruments.MSI_S2A
    srf = instrument.srf()

    assert instrument.has_srf
    assert isinstance(srf, pd.DataFrame)
    assert "wavelength" in srf.columns
    assert set(instrument.bands().index).issubset(srf.columns)


def test_srf_returns_none_when_unavailable():
    instrument = xeo.instruments.EMIT

    assert not instrument.has_srf
    assert instrument.srf() is None


def test_get_data_access_uses_earth_engine_primary_by_default():
    result = xeo.instruments.MSI_S2A.get_data_access()

    assert result == {
        "stac_endpoint": None,
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "docs": (
            "https://developers.google.com/earth-engine/datasets/catalog/"
            "COPERNICUS_S2_SR_HARMONIZED"
        ),
    }


def test_get_data_access_supports_provider_and_processing_level():
    planetary_computer = xeo.instruments.MSI_S2A.get_data_access(
        "planetary_computer", "boa"
    )
    cdse = xeo.instruments.MSI_S2A.get_data_access("cdse", "toa")

    assert planetary_computer == {
        "stac_endpoint": "https://planetarycomputer.microsoft.com/api/stac/v1",
        "collection": "sentinel-2-l2a",
        "docs": "https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a",
    }
    assert cdse["collection"] == "sentinel-2-l1c"
    assert cdse["stac_endpoint"] == "https://stac.dataspace.copernicus.eu/v1"


def test_get_data_access_returns_none_when_valid_access_point_is_unavailable():
    assert xeo.instruments.MSI_S2A.get_data_access(processing_level="raw") is None
    assert xeo.instruments.ASTER.get_data_access(provider="eopf") is None
    assert xeo.instruments.ALTUMPT_MICASENSE.get_data_access() is None


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"provider": "planetary"}, "provider must be one of"),
        ({"processing_level": "l2a"}, "processing_level must be one of"),
    ],
)
def test_get_data_access_rejects_unknown_options(kwargs, message):
    with pytest.raises(ValueError, match=message):
        xeo.instruments.MSI_S2A.get_data_access(**kwargs)


def test_rich_instrument_table_still_renders():
    output = StringIO()
    console = Console(file=output, color_system=None, width=160)

    console.print(xeo.instruments)

    rendered = output.getvalue()
    assert "Awesome Earth Observation Instruments" in rendered
    assert "MSI_S2A" in rendered


def test_catalogue_is_packaged_under_xeo():
    catalogue_path = files("xeo.data") / "catalogue.json"

    assert catalogue_path.is_file()
