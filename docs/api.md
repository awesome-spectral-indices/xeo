---
outline: deep
---

## `xeo`

xeo - Earth observation instruments in Python.


**Classes:**

- [**Catalogue**](#xeo.Catalogue) – Awesome Earth Observation Instruments catalogue. 🐈
- [**Instrument**](#xeo.Instrument) – Earth observation instrument from the catalogue.
- [**Instruments**](#xeo.Instruments) – Collection of instruments in the catalogue.

### `xeo.Catalogue`

```python
Catalogue(catalogue, instruments=None)
```

Bases: <code>[object](#object)</code>

Awesome Earth Observation Instruments catalogue. 🐈

**Parameters:**

- **catalogue** (<code>[dict](#dict)</code>) – Raw catalogue data.
- **instruments** (<code>[Instruments](#xeo.Instruments)</code>) – Instrument objects created from the raw catalogue.

**Examples:**

```pycon
>>> import xeo
>>> xeo.catalogue
Awesome Earth Observation Instruments (v0.1.0)
>>> len(xeo.catalogue.instruments)
28
```

**Functions:**

- [**search**](#xeo.Catalogue.search) – Search instruments using core metadata and spectral availability.
- [**to_dict**](#xeo.Catalogue.to_dict) – Return an independent dictionary containing the raw catalogue.

**Attributes:**

- [**data**](#xeo.Catalogue.data) – Raw, JSON-serializable catalogue data.
- [**href**](#xeo.Catalogue.href) – URL of the catalogue. Equivalent to :attr:`link`.
- [**instruments**](#xeo.Catalogue.instruments) – Instruments available in the catalogue.
- [**link**](#xeo.Catalogue.link) – URL of the catalogue.
- [**name**](#xeo.Catalogue.name) – Name of the catalogue.
- [**version**](#xeo.Catalogue.version) – Version of the catalogue.

#### `xeo.Catalogue.data`

```python
data = catalogue
```

Raw, JSON-serializable catalogue data.

#### `xeo.Catalogue.href`

```python
href = catalogue['link']
```

URL of the catalogue. Equivalent to :attr:`link`.

#### `xeo.Catalogue.instruments`

```python
instruments = instruments
```

Instruments available in the catalogue.

#### `xeo.Catalogue.link`

```python
link = catalogue['link']
```

URL of the catalogue.

#### `xeo.Catalogue.name`

```python
name = catalogue['name']
```

Name of the catalogue.

#### `xeo.Catalogue.search`

```python
search(**kwargs)
```

Search instruments using core metadata and spectral availability.

Search values are matched exactly, except that ``start_date`` also
accepts inclusive intervals formatted as
``YYYY-MM-DD/YYYY-MM-DD``. Different properties are combined with AND.
A list supplied for one property uses OR, and list-valued instrument
properties such as ``operator`` and ``platform`` match when any
requested value is present.

**Parameters:**

- ****kwargs** (<code>[Any](#typing.Any)</code>) – Required instrument properties to match. ``has_srf`` and
``has_bands`` are also accepted as boolean filters.

**Returns:**

- <code>[Instruments](#xeo.Instruments)</code> – A frozen collection containing the matching instruments in
catalogue order.


**Examples:**

```pycon
>>> import xeo
>>> result = xeo.catalogue.search(operator=["ESA", "NASA"])
>>> "MSI_S2A" in result and "OLI_L8" in result
True
>>> all(item.has_srf for item in xeo.catalogue.search(has_srf=True).values())
True
>>> list(xeo.catalogue.search(start_date="2000-01-01/2003-01-01"))
['MODIS_AQUA']
```

#### `xeo.Catalogue.to_dict`

```python
to_dict()
```

Return an independent dictionary containing the raw catalogue.

#### `xeo.Catalogue.version`

```python
version = catalogue['version']
```

Version of the catalogue.

### `xeo.Instrument`

```python
Instrument(instrument)
```

Bases: <code>[object](#object)</code>

Earth observation instrument from the catalogue.

Core metadata is available directly as attributes. The complete source record
remains available through :attr:`data`.

**Examples:**

```pycon
>>> import xeo
>>> xeo.instruments.MSI_S2A
Instrument(MSI_S2A: MultiSpectral Instrument)
>>> xeo.instruments.MSI_S2A.operator
['ESA', 'Copernicus']
>>> xeo.instruments.MSI_S2A.bands().shape
(13, 6)
```

**Functions:**

- [**bands**](#xeo.Instrument.bands) – Return spectral bands as a DataFrame, when available.
- [**get_data_access**](#xeo.Instrument.get_data_access) – Return metadata for an available data access point.
- [**srf**](#xeo.Instrument.srf) – Return the spectral response function as a DataFrame, when available. 🐱
- [**to_dict**](#xeo.Instrument.to_dict) – Return an independent dictionary containing the instrument record.

**Attributes:**

- [**acronym**](#xeo.Instrument.acronym) (<code>[str](#str)</code>) – Instrument acronym.
- [**availability**](#xeo.Instrument.availability) (<code>[str](#str)</code>) – Instrument data accessibility level.
- [**data**](#xeo.Instrument.data) (<code>[dict](#dict)[[str](#str), [Any](#typing.Any)]</code>) – Complete instrument record from the catalogue.
- [**data_links**](#xeo.Instrument.data_links) (<code>[list](#list)[[str](#str)]</code>) – URLs where instrument data products can be accessed.
- [**end_date**](#xeo.Instrument.end_date) (<code>[str](#str) | None</code>) – End of instrument operation, when available.
- [**extension_names**](#xeo.Instrument.extension_names) (<code>[list](#list)[[str](#str)]</code>) – Names of the extensions available for this instrument.
- [**extensions**](#xeo.Instrument.extensions) (<code>[dict](#dict)[[str](#str), [Any](#typing.Any)]</code>) – Domain-specific instrument metadata extensions.
- [**family**](#xeo.Instrument.family) (<code>[list](#list)[[str](#str)]</code>) – Identifiers of instruments in the same family. 🐈‍⬛
- [**has_bands**](#xeo.Instrument.has_bands) (<code>[bool](#bool)</code>) – Whether materialized spectral band definitions are available.
- [**has_srf**](#xeo.Instrument.has_srf) (<code>[bool](#bool)</code>) – Whether a spectral response function is available.
- [**id**](#xeo.Instrument.id) (<code>[str](#str)</code>) – Instrument identifier.
- [**name**](#xeo.Instrument.name) (<code>[str](#str)</code>) – Full instrument name.
- [**notes**](#xeo.Instrument.notes) (<code>[str](#str) | None</code>) – Additional notes, when available.
- [**operator**](#xeo.Instrument.operator) (<code>[list](#list)[[str](#str)]</code>) – Organizations operating the instrument.
- [**platform**](#xeo.Instrument.platform) (<code>[list](#list)[[str](#str)]</code>) – Platforms carrying the instrument.
- [**platform_companions**](#xeo.Instrument.platform_companions) (<code>[list](#list)[[str](#str)]</code>) – Identifiers of other instruments on the same platform.
- [**platform_type**](#xeo.Instrument.platform_type) (<code>[str](#str)</code>) – Class of platform carrying the instrument.
- [**references**](#xeo.Instrument.references) (<code>[list](#list)[[str](#str)]</code>) – Reference URLs for the instrument.
- [**start_date**](#xeo.Instrument.start_date) (<code>[str](#str)</code>) – Start of instrument operation.
- [**status**](#xeo.Instrument.status) (<code>[str](#str)</code>) – Instrument lifecycle status.
- [**type**](#xeo.Instrument.type) (<code>[str](#str)</code>) – Instrument sensing modality.

#### `xeo.Instrument.acronym`

```python
acronym: str
```

Instrument acronym.

#### `xeo.Instrument.availability`

```python
availability: str
```

Instrument data accessibility level.

#### `xeo.Instrument.bands`

```python
bands()
```

Return spectral bands as a DataFrame, when available.

The DataFrame is indexed by band identifier. ``None`` is returned when
the instrument has no materialized spectral band definitions.

#### `xeo.Instrument.data`

```python
data: dict[str, Any]
```

Complete instrument record from the catalogue.

#### `xeo.Instrument.data_links`

```python
data_links: list[str]
```

URLs where instrument data products can be accessed.

#### `xeo.Instrument.end_date`

```python
end_date: str | None
```

End of instrument operation, when available.

#### `xeo.Instrument.extension_names`

```python
extension_names: list[str]
```

Names of the extensions available for this instrument.

#### `xeo.Instrument.extensions`

```python
extensions: dict[str, Any]
```

Domain-specific instrument metadata extensions.

#### `xeo.Instrument.family`

```python
family: list[str]
```

Identifiers of instruments in the same family. 🐈‍⬛

#### `xeo.Instrument.get_data_access`

```python
get_data_access(provider='ee', processing_level='primary')
```

Return metadata for an available data access point.

**Parameters:**

- **provider** (<code>[str](#str)</code>) – Data provider. One of ``ee``, ``planetary_computer``, ``cdse``, or
``eopf``.
- **processing_level** (<code>[str](#str)</code>) – Processing level. One of ``primary``, ``boa``, ``toa``, or ``raw``.

**Returns:**

- <code>[dict](#dict) or None</code> – A dictionary containing ``stac_endpoint``, ``collection``, and
``docs``. Missing values, such as the Earth Engine STAC endpoint,
are represented by ``None``. ``None`` is returned when the provider
or processing level is valid but unavailable for this instrument.


**Examples:**

```pycon
>>> import xeo
>>> xeo.instruments.MSI_S2A.get_data_access()["collection"]
'COPERNICUS/S2_SR_HARMONIZED'
>>> xeo.instruments.MSI_S2A.get_data_access("cdse", "toa")["collection"]
'sentinel-2-l1c'
>>> xeo.instruments.MSI_S2A.get_data_access(processing_level="raw") is None
True
```

#### `xeo.Instrument.has_bands`

```python
has_bands: bool
```

Whether materialized spectral band definitions are available.

#### `xeo.Instrument.has_srf`

```python
has_srf: bool
```

Whether a spectral response function is available.

#### `xeo.Instrument.id`

```python
id: str
```

Instrument identifier.

#### `xeo.Instrument.name`

```python
name: str
```

Full instrument name.

#### `xeo.Instrument.notes`

```python
notes: str | None
```

Additional notes, when available.

#### `xeo.Instrument.operator`

```python
operator: list[str]
```

Organizations operating the instrument.

#### `xeo.Instrument.platform`

```python
platform: list[str]
```

Platforms carrying the instrument.

#### `xeo.Instrument.platform_companions`

```python
platform_companions: list[str]
```

Identifiers of other instruments on the same platform.

#### `xeo.Instrument.platform_type`

```python
platform_type: str
```

Class of platform carrying the instrument.

#### `xeo.Instrument.references`

```python
references: list[str]
```

Reference URLs for the instrument.

#### `xeo.Instrument.srf`

```python
srf()
```

Return the spectral response function as a DataFrame, when available. 🐱

``None`` is returned when the instrument has no spectral response
function in the catalogue.

#### `xeo.Instrument.start_date`

```python
start_date: str
```

Start of instrument operation.

#### `xeo.Instrument.status`

```python
status: str
```

Instrument lifecycle status.

#### `xeo.Instrument.to_dict`

```python
to_dict()
```

Return an independent dictionary containing the instrument record.

#### `xeo.Instrument.type`

```python
type: str
```

Instrument sensing modality.

### `xeo.Instruments`

Bases: <code>[Box](#box.Box)</code>

Collection of instruments in the catalogue.

Instruments support both mapping and attribute access. 😺

**Examples:**

```pycon
>>> import xeo
>>> xeo.instruments.MSI_S2A
Instrument(MSI_S2A: MultiSpectral Instrument)
>>> xeo.instruments["MSI_S2A"] is xeo.instruments.MSI_S2A
True
```
