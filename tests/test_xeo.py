import json
from importlib.resources import files
from io import StringIO

import pandas as pd
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
