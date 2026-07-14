<p align="center">
  <a href="https://github.com/awesome-spectral-indices/xeo"><img src="docs/public/xeo-logo-2.png" alt="xeo"></a>
</p>
<p align="center">
    <em><a href="https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments">Awesome Earth Observation Instruments</a> in Python</em>
</p>

<p align="center">
<a href="https://github.com/sindresorhus/awesome" target="_blank">
    <img src="https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg" alt="Awesome">
</a>
<a href="https://arxiv.org/abs/2606.13923" target="_blank">
    <img src="https://img.shields.io/badge/arXiv-2606.13923-b31b1b.svg" alt="arXiv">
</a>
<a href="https://github.com/sponsors/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/GitHub%20Sponsors-Donate-ff69b4.svg" alt="GitHub Sponsors">
</a>
<a href="https://www.buymeacoffee.com/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-Donate-ff69b4.svg" alt="Buy me a coffee">
</a>
<a href="https://ko-fi.com/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/kofi-Donate-ff69b4.svg" alt="Ko-fi">
</a>
<a href="https://twitter.com/dmlmont" target="_blank">
    <img src="https://img.shields.io/twitter/follow/dmlmont?style=social" alt="Twitter">
</a>
</p>

---

**Awesome Earth Observation Instruments Catalogue**: <a href="https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments" target="_blank">https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments</a>

**GitHub**: <a href="https://github.com/awesome-spectral-indices/xeo" target="_blank">https://github.com/awesome-spectral-indices/xeo</a>

---

# About xeo

`xeo` is the Python interface to the [Awesome Earth Observation Instruments](https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments) catalogue. It turns the catalogue into a small, exploratory API for discovering instruments, inspecting their metadata, searching across the collection, and loading spectral bands and spectral response functions as pandas DataFrames when they are available.

A snapshot of the catalogue is bundled with each `xeo` release. This keeps catalogue exploration local and makes it straightforward to use instrument metadata in Python workflows.

## What is the Awesome Earth Observation Instruments catalogue?

Awesome Earth Observation Instruments is a community-driven, machine-readable catalogue of instruments used to observe Earth. It organizes spectral, spatial, temporal, operational, platform, and data-access metadata under a consistent schema so that instruments from different missions and operators can be discovered and compared.

The catalogue is the source of the instrument records; `xeo` is the Python interface to those records. Contributions to instrument metadata, bands, SRFs, or catalogue schemas belong in the [catalogue repository](https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments), while contributions to the Python API and its documentation belong here.

# Installation

> [!NOTE]
> The conda-forge package has not been published yet. The commands below will become available with the first release on each channel.

Install `xeo` from PyPI:

```bash
python -m pip install xeo
```

Or install it from conda-forge:

```bash
conda install -c conda-forge xeo
```

To use the current development version:

```bash
git clone https://github.com/awesome-spectral-indices/xeo.git
cd xeo
python -m pip install --editable .
```

`xeo` requires Python 3.10 or newer.

# Getting started

## Explore the catalogue

Import `xeo` to access the bundled catalogue and its instrument collection:

```python
import xeo

print(xeo.catalogue)
print(f"Catalogue version: {xeo.catalogue.version}")
print(f"Number of instruments: {len(xeo.instruments)}")
print(list(xeo.instruments))
```

`xeo.instruments` is a frozen collection keyed by instrument identifier. Instruments support both attribute and mapping access:

```python
msi = xeo.instruments.MSI_S2A
assert msi is xeo.instruments["MSI_S2A"]

print(msi.name)
print(msi.platform)
print(msi.operator)
print(msi.status)
```

## Inspect instrument metadata

Required catalogue fields are exposed as attributes. Optional and domain-specific metadata can be discovered through extensions, while relationships connect an instrument to its family and platform companions:

```python
print(msi.extension_names)
print(msi.extensions["spectral"].keys())
print(msi.family)
print(msi.platform_companions)
print(msi.references)
```

Use `msi.data` to inspect the original record, or `msi.to_dict()` when you need an independent copy that can be modified safely.

## Search for instruments

`Catalogue.search()` returns an `Instruments` collection containing every match. Different properties are combined with AND, while lists mean “match any of these values”:

```python
results = xeo.catalogue.search(
    operator=["ESA", "NASA"],
    platform_type="satellite",
    status="operational",
    has_bands=True,
)

print(list(results))
```

Use `has_bands` and `has_srf` to filter by spectral-data availability. For `start_date`, an inclusive `YYYY-MM-DD/YYYY-MM-DD` interval avoids requiring an exact date:

```python
launched = xeo.catalogue.search(
    start_date="2000-01-01/2003-01-01"
)
```

## Load spectral bands

When band definitions are available, `bands()` returns a DataFrame indexed by band identifier:

```python
if msi.has_bands:
    bands = msi.bands()
    print(bands.loc[["B2", "B3", "B4"], ["center_wavelength", "bandwidth"]])
```

Wavelengths and bandwidths are expressed in nanometres, and band-level ground sampling distances are expressed in metres.

## Load spectral response functions

When an SRF is available, `srf()` returns a DataFrame with a `wavelength` column and one response column per band:

```python
if msi.has_srf:
    srf = msi.srf()
    print(srf[["wavelength", "B2", "B3", "B4"]].head())
```

Both `bands()` and `srf()` return `None` when the requested data is not available.

## Discover data access points

`get_data_access()` retrieves the catalogue entry for a provider and processing level. It defaults to the primary Google Earth Engine collection:

```python
earth_engine = msi.get_data_access()
planetary_computer = msi.get_data_access("planetary_computer", "boa")
cdse = msi.get_data_access("cdse", "toa")
```

Available providers are `ee`, `planetary_computer`, `cdse`, and `eopf`; processing levels are `primary`, `boa`, `toa`, and `raw`. An available entry is returned as a dictionary with `stac_endpoint`, `collection`, and `docs`. Valid combinations that are not available for an instrument return `None`.

## Work with raw catalogue data

The object API is intended for exploration, but the complete JSON-compatible catalogue is also available for custom workflows:

```python
raw_record = xeo.catalogue.data["instruments"]["MSI_S2A"]
catalogue_copy = xeo.catalogue.to_dict()
```

Treat `.data` as read-only. Use `.to_dict()` when downstream code needs to modify a catalogue or instrument dictionary.

# Tutorials

The tutorial notebooks provide complete, executable examples:

1. [Getting started](docs/tutorials/01_getting_started.ipynb)
2. [Exploring instruments](docs/tutorials/02_exploring_instruments.ipynb)
3. [Spectral bands](docs/tutorials/03_spectral_bands.ipynb)
4. [Spectral response functions](docs/tutorials/04_spectral_response_functions.ipynb)
5. [Raw data and DataFrame workflows](docs/tutorials/05_raw_data_and_dataframe_workflows.ipynb)
6. [Data access](docs/tutorials/06_data_access.ipynb)
7. [Advanced search](docs/tutorials/07_advanced_search.ipynb)

# Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, documentation guidance, and where to propose catalogue-data changes.

# License

`xeo` is available under the [MIT License](LICENSE).
