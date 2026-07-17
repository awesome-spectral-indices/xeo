# Contributing to xeo

Thank you for helping improve `xeo`. Contributions can include bug fixes, new Python API features, tests, documentation, and tutorial improvements.

## Choose the right repository

`xeo` is the Python interface to the Awesome Earth Observation Instruments catalogue. Please use:

- The [`xeo` repository](https://github.com/awesome-spectral-indices/xeo) for Python API behavior, packaging, tests, and documentation.
- The [Awesome Earth Observation Instruments repository](https://github.com/awesome-spectral-indices/awesome-earth-observation-instruments) for new or corrected instrument records, bands, spectral response functions, schemas, references, and data-access metadata.

The file `xeo/data/catalogue.json` is a bundled snapshot of the upstream catalogue, not its source of truth. Do not make isolated catalogue-data corrections in that generated snapshot. If a package change requires a catalogue refresh, identify the corresponding upstream catalogue version and include any necessary compatibility tests.

## Report an issue

Before opening an issue, check whether a similar one already exists. A useful report includes:

- The `xeo` and Python versions.
- A small example that reproduces the problem.
- The expected and actual behavior.
- The full traceback, when applicable.

You can inspect the installed package version with:

```python
import xeo

print(xeo.__version__)
```

## Set up a development environment

Fork and clone the repository, then create an isolated environment. For example, with conda:

```bash
git clone https://github.com/YOUR-USERNAME/xeo.git
cd xeo
conda create --name xeo-dev python=3.10
conda activate xeo-dev
python -m pip install --editable ".[plot]"
python -m pip install pytest tox jupyter nbformat nbconvert
```

Python 3.10 is the minimum supported version. Using a newer supported Python version is also fine unless you are investigating version-specific behavior.

Create a focused branch for your change:

```bash
git switch -c your-change
```

## Make a change

Keep each contribution focused and follow the patterns already used in the package:

- Add or update tests for behavioral changes.
- Use type hints for new public interfaces.
- Add concise docstrings and examples for public classes, properties, and methods.
- Preserve catalogue order unless a feature explicitly requires different ordering.
- Return the existing public objects (`Catalogue`, `Instruments`, and `Instrument`) where appropriate so API behavior remains consistent.
- Avoid unrelated formatting or refactoring in the same pull request.

The main project locations are:

- `xeo/axioms.py` for the catalogue object model and its behavior.
- `xeo/xeo.py` and `xeo/__init__.py` for public exports.
- `tests/test_xeo.py` for the test suite.
- `docs/tutorials/` for executable tutorial notebooks.

## Run the tests

Run the test suite from the repository root:

```bash
python -m pytest tests
```

You can also run the configured tox environment:

```bash
tox
```

When fixing a bug, first add a test that demonstrates the failure, then verify that the complete suite passes with the fix.

## Update tutorial notebooks

Tutorials should be short, executable, and build progressively on the public API. Name new notebooks with the next two-digit prefix, such as `08_new_feature.ipynb`.

Run every changed notebook from top to bottom. Before committing it, clear all cell outputs and execution counts:

```bash
jupyter nbconvert --clear-output --inplace docs/tutorials/08_new_feature.ipynb
```

Do not include local paths, credentials, large generated results, or environment-specific state in notebooks.

## Open a pull request

In the pull request description, explain what changed, why it changed, and how it was tested. Keep backward-compatibility implications explicit when modifying the public API.

Before submitting, check that:

- The complete test suite passes.
- New behavior is covered by tests.
- Public-facing changes are documented.
- Changed notebooks execute successfully and have clean outputs.
- Catalogue metadata changes have been proposed in the upstream catalogue repository.
- The pull request contains no unrelated generated files or environment artifacts.
