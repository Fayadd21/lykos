# Documentation

This directory contains the Sphinx documentation for Lykos.

## Generating the Documentation

To generate the HTML documentation, run:

```bash
poetry run sphinx-build -b html docs/source docs/build/html
```

Or if you're in the `docs` directory:

```bash
cd docs
make.bat html
```

On Linux/Mac:

```bash
cd docs
make html
```

## Viewing the Documentation

After generation, open `docs/build/html/index.html` in your web browser.

## Regenerating

After making changes to docstrings or documentation files, run the generation command again to update the documentation.

