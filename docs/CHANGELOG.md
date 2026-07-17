# Changelog

All notable changes to `xeo` are documented in this file.

## 0.2.1

### Added

- Added `plot_bands()` for Gantt-style spectral-band plots with automatic sub-lanes for overlapping bands.
- Added `plot_srf()` for multi-instrument spectral response curves with peak labels and collision-aware label placement.
- Added flexible instrument and band selection, including lists of per-instrument selection dictionaries and per-band Matplotlib styles.
- Added the optional `plot` dependency extra for installing Matplotlib without making it a core dependency.

### Documentation

- Added a plotting tutorial covering input forms, overlapping bands, per-band Matplotlib styles, SRF comparisons, and axes customization.

### Removed

- Removed rich terminal table rendering from the instrument collection to keep the package minimal.
- Removed Rich from the runtime dependencies.

## 0.2.0

This is the first complete release of `xeo`, the Python interface to the Awesome Earth Observation Instruments catalogue.

### Added

- Added the bundled Awesome Earth Observation Instruments catalogue and exposed its name, version, source link, raw data, and instrument collection through `xeo.catalogue`.
- Added the public `Catalogue`, `Instruments`, and `Instrument` object model.
- Added the shared `xeo.instruments` collection with attribute and mapping access by instrument identifier.
- Added rich terminal rendering for exploring the complete instrument collection as a table.
- Added direct access to core instrument metadata, including names, acronyms, sensing and platform types, platforms, operators, operational dates, status, availability, references, and data links.
- Added access to optional metadata, catalogue extensions, instrument families, and platform companions.
- Added `Catalogue.search()` for advanced instrument discovery, with:
  - Exact matching across catalogue properties.
  - AND matching between different properties.
  - OR matching when a list of values is supplied.
  - Matching against list-valued properties such as `operator` and `platform`.
  - `has_bands` and `has_srf` availability filters.
  - Inclusive `YYYY-MM-DD/YYYY-MM-DD` intervals for `start_date`.
- Added `Instrument.bands()` for loading spectral band definitions as a pandas DataFrame indexed by band identifier.
- Added `Instrument.srf()` for loading spectral response functions as a pandas DataFrame.
- Added `has_bands` and `has_srf` properties for checking spectral-data availability before loading it.
- Added `Instrument.get_data_access()` for discovering catalogue collections and documentation across:
  - Google Earth Engine (`ee`).
  - Microsoft Planetary Computer (`planetary_computer`).
  - Copernicus Data Space Ecosystem (`cdse`).
  - EOPF Sentinel Zarr Samples (`eopf`).
- Added support for the `primary`, `boa`, `toa`, and `raw` processing levels in data-access queries.
- Added `to_dict()` methods for obtaining independent copies of catalogue and instrument records.
- Added concise string and representation methods for catalogue objects, instruments, and instrument collections.

### Changed

- Refactored catalogue loading so `xeo.catalogue.instruments` and `xeo.instruments` share the same frozen instrument collection.
- Refined the public API around catalogue exploration while retaining access to the original JSON-compatible records.
- Updated the bundled catalogue to the current Awesome Earth Observation Instruments snapshot.
- Set the package version to `0.2.0` and the minimum supported Python version to 3.10.

### Documentation

- Added a complete README covering the purpose of `xeo`, its relationship to the upstream catalogue, installation, the principal API features, and links to further learning material.
- Added contributor guidance for development setup, testing, notebooks, pull requests, and directing catalogue-data contributions to the upstream repository.
- Added seven executable tutorial notebooks:
  1. Getting started.
  2. Exploring instruments.
  3. Spectral bands.
  4. Spectral response functions.
  5. Raw data and DataFrame workflows.
  6. Data access.
  7. Advanced catalogue search.
- Added API docstrings and examples throughout the catalogue object model.

### Packaging and maintenance

- Added setuptools-based packaging through `pyproject.toml`.
- Included the catalogue JSON snapshot as package data.
- Added runtime dependencies for pandas, python-box, and Rich.
- Added pytest coverage for the public API, search behavior, spectral data, data access, representations, and packaged catalogue data.
- Added a tox configuration for running the test suite.
- Added a GitHub Actions workflow that downloads the latest generated catalogue from the Awesome Earth Observation Instruments repository and updates the bundled snapshot when it changes.
- Added the MIT License.
