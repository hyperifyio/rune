# Rune

## Build and CI

To build locally with hatch:

```bash
python -m pip install --upgrade pip && pip install hatch
hatch build -t sdist -t wheel
ls dist/*.whl dist/*.tar.gz
```

A GitHub Actions workflow in `.github/workflows/build.yml` builds the package on every push and pull request and uploads `dist/` as an artifact.
