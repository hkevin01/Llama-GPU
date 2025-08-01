# API Documentation Automation

This guide describes how API documentation is generated and maintained for the Llama-GPU project.

## Tools Used
- **Sphinx**: For Python API docs (`docs/_build/` is ignored in `.gitignore`).
- **MkDocs**: For general project documentation.
- **docstrings**: All public classes and functions must have clear docstrings.

## Automation Steps
1. **Install Sphinx/MkDocs**:
   - `pip install sphinx mkdocs`
2. **Generate Docs**:
   - Python: `sphinx-apidoc -o docs/source src/`
   - Build: `make html` (from `docs/`)
   - MkDocs: `mkdocs build`
3. **CI/CD Integration**:
   - Docs build is included in CI pipeline.
   - Failed builds block merges.
4. **Preview Locally**:
   - Sphinx: `python -m http.server` in `docs/_build/html`
   - MkDocs: `mkdocs serve`

## Contributor Notes
- Update docstrings with every code change.
- Review API docs before submitting PRs.
- For issues, check `docs/usage.md` and open a documentation issue.

---
_Last updated: July 21, 2025_
