# Getting Started

`xeo` is the Python interface to the [Awesome Earth Observation Instruments catalogue](https://awesome-spectral-indices.github.io/awesome-earth-observation-instruments/). It lets you explore instrument metadata, search the catalogue, load spectral bands and spectral response functions (SRFs) as pandas DataFrames, and discover available data-access collections.

## Installation

`xeo` requires Python 3.10 or newer. Install a published release from PyPI with:

```bash
python -m pip install xeo
```

Plotting support is an optional extra:

```bash
python -m pip install "xeo[plot]"
```

The package is also planned for conda-forge. Once it is available there, install it with:

```bash
conda install -c conda-forge xeo
```

## Import xeo

Import the package to access the bundled catalogue and its instrument collection:

```python
import xeo

print(f"xeo version: {xeo.__version__}")
print(f"Catalogue version: {xeo.catalogue.version}")
print(f"Number of instruments: {len(xeo.instruments)}")
```

The Python package version and catalogue version are independent: a package release bundles a particular snapshot of the catalogue.

## Select an instrument

Instrument identifiers are the keys of `xeo.instruments`. You can use either attribute or mapping access:

```python
print(list(xeo.instruments)[:10])

msi = xeo.instruments.MSI_S2A
assert msi is xeo.instruments["MSI_S2A"]

print(msi.name)
print(msi.platform)
print(msi.operator)
print(msi.status)
```

Use `msi.data` to inspect the original catalogue record, or `msi.to_dict()` to get an independent dictionary that is safe to modify.

## Search the catalogue

Use `Catalogue.search()` to find instruments by metadata or data availability. It returns an `Instruments` collection with the same lookup interface as `xeo.instruments`:

```python
results = xeo.catalogue.search(
    operator=["ESA", "NASA"],
    platform_type="satellite",
    has_bands=True,
)

print(list(results))
```

Different search properties are combined with AND. A list means “match any of these values.” Start dates also accept inclusive intervals:

```python
results = xeo.catalogue.search(
    start_date="2000-01-01/2003-01-01"
)
```

## Load bands and SRFs

When spectral data are available, `bands()` and `srf()` return pandas DataFrames:

```python
if msi.has_bands:
    bands = msi.bands()
    print(bands.head())

if msi.has_srf:
    srf = msi.srf()
    print(srf.head())
```

`bands()` is indexed by band identifier. `srf()` contains a `wavelength` column and one response column per band. Either method returns `None` when its data are unavailable.

## Plot bands and SRFs

With the optional plotting extra installed, plot all bands for one or more instruments by passing their ids:

```python
bands_ax = xeo.plot_bands(["MSI_S2A", "OLI_L8"])
```

Use a dictionary to select bands and attach native Matplotlib styles. A list of dictionaries can give each instrument its own band selection and styling:

```python
srf_ax = xeo.plot_srf(
    [
        {
            "MSI_S2A": [
                {"B3": {"color": "green"}},
                {"B4": {"color": "red", "linestyle": "--", "linewidth": 2}},
            ]
        },
        {"OLI_L8": [{"B5": {"color": "blue", "linewidth": 2}}]},
    ],
    title="Selected instrument responses",
    figsize=(10, 6),
)
```

Both functions return a Matplotlib `Axes`. Pass an existing `ax` or use the returned object to customize labels, limits, legends, themes, and any other plot details.

## Discover data access

`get_data_access()` returns the available data-access metadata for a provider and processing level. By default, it requests the primary Google Earth Engine collection:

```python
earth_engine = msi.get_data_access()
planetary_computer = msi.get_data_access(
    provider="planetary_computer",
    processing_level="boa",
)

print(earth_engine)
print(planetary_computer)
```

Supported providers are `ee`, `planetary_computer`, `cdse`, and `eopf`. Supported processing levels are `primary`, `boa`, `toa`, and `raw`. Available entries contain `stac_endpoint`, `collection`, and `docs`; unavailable combinations return `None`.

## Next steps

- Follow the [tutorials](/tutorials/) for complete, executable examples.
- See the [API reference](/api) for every public class, property, and method.
- Visit the [Instrument Catalogue](https://awesome-spectral-indices.github.io/awesome-earth-observation-instruments/) to learn about the underlying data project.
