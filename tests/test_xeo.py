import json
from importlib.resources import files

import pandas as pd
import pytest
import xeo


def test_public_package_metadata():
    assert xeo.__all__ == [
        "Catalogue",
        "Instrument",
        "Instruments",
        "catalogue",
        "instruments",
        "plot_bands",
        "plot_srf",
    ]


def test_catalogue_uses_one_shared_instrument_collection():
    assert isinstance(xeo.catalogue, xeo.Catalogue)
    assert isinstance(xeo.instruments, xeo.Instruments)
    assert xeo.catalogue.instruments is xeo.instruments
    assert xeo.instruments["MSI_S2A"] is xeo.instruments.MSI_S2A


def test_catalogue_search_returns_an_instruments_collection():
    results = xeo.catalogue.search(platform_type="uav")

    assert isinstance(results, xeo.Instruments)
    assert results
    assert all(instrument.platform_type == "uav" for instrument in results.values())
    assert results.ALTUMPT_MICASENSE is xeo.instruments.ALTUMPT_MICASENSE


def test_catalogue_search_uses_or_for_a_list_of_values():
    results = xeo.catalogue.search(operator=["ESA", "NASA"])

    assert "MSI_S2A" in results
    assert "OLI_L8" in results
    assert all(
        set(instrument.operator).intersection({"ESA", "NASA"})
        for instrument in results.values()
    )


def test_catalogue_search_combines_different_properties_with_and():
    results = xeo.catalogue.search(
        operator=["ESA", "NASA"],
        platform_type="satellite",
        status="operational",
        has_srf=True,
    )

    assert results
    assert all(
        instrument.platform_type == "satellite"
        for instrument in results.values()
    )
    assert all(instrument.status == "operational" for instrument in results.values())
    assert all(instrument.has_srf for instrument in results.values())


def test_catalogue_search_supports_boolean_availability_filters():
    with_srf = xeo.catalogue.search(has_srf=True)
    without_srf = xeo.catalogue.search(has_srf=False)
    without_bands = xeo.catalogue.search(has_bands=False)

    assert all(instrument.has_srf for instrument in with_srf.values())
    assert all(not instrument.has_srf for instrument in without_srf.values())
    assert set(with_srf).isdisjoint(without_srf)
    assert set(with_srf).union(without_srf) == set(xeo.instruments)
    assert len(without_bands) == 0


def test_catalogue_search_supports_lists_for_scalar_properties():
    results = xeo.catalogue.search(id=["MSI_S2A", "OLI_L8"])

    assert list(results) == ["MSI_S2A", "OLI_L8"]


def test_catalogue_search_supports_inclusive_start_date_intervals():
    results = xeo.catalogue.search(start_date="2000-01-01/2003-01-01")
    boundary = xeo.catalogue.search(start_date="2002-05-04/2002-05-04")

    assert list(results) == ["MODIS_AQUA"]
    assert list(boundary) == ["MODIS_AQUA"]


def test_catalogue_search_supports_exact_dates_and_lists_of_date_queries():
    exact = xeo.catalogue.search(start_date="2002-05-04")
    multiple = xeo.catalogue.search(
        start_date=["1999-04-15/1999-12-18", "2002-05-04"]
    )

    assert list(exact) == ["MODIS_AQUA"]
    assert list(multiple) == [
        "ASTER",
        "ETM_L7",
        "MODIS_AQUA",
        "MODIS_TERRA",
    ]


@pytest.mark.parametrize(
    "interval",
    [
        "2000-01-01/",
        "/2003-01-01",
        "2000/2003",
        "2000-01-01/2003-01-01/2004-01-01",
        "2003-01-01/2000-01-01",
    ],
)
def test_catalogue_search_rejects_invalid_start_date_intervals(interval):
    with pytest.raises(ValueError, match="start_date interval"):
        xeo.catalogue.search(start_date=interval)


def test_catalogue_search_without_filters_returns_all_instruments():
    results = xeo.catalogue.search()

    assert isinstance(results, xeo.Instruments)
    assert list(results) == list(xeo.instruments)


def test_catalogue_search_rejects_invalid_filters():
    with pytest.raises(ValueError, match="unknown search properties"):
        xeo.catalogue.search(notes="example")
    with pytest.raises(TypeError, match="has_srf must be a boolean"):
        xeo.catalogue.search(has_srf="yes")


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


def test_catalogue_is_packaged_under_xeo():
    catalogue_path = files("xeo.data") / "catalogue.json"

    assert catalogue_path.is_file()
