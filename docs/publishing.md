# Publishing Guide

This guide explains how to package, version, and publish Llama-GPU to PyPI and other repositories.

## Packaging
- Ensure `setup.py` and `pyproject.toml` are up to date
- Run:
  ```bash
  python -m build
  twine check dist/*
  ```

## Versioning
- Follow [Semantic Versioning](https://semver.org/)
- Update version in `setup.py` and `pyproject.toml` for each release

## Publishing to PyPI
- Register on PyPI: https://pypi.org/account/register/
- Upload package:
  ```bash
  twine upload dist/*
  ```

## Release Checklist
- All tests pass
- Documentation is up to date
- Changelog is updated
- Version is bumped

---
_Last updated: July 21, 2025_