# Publishing Guide: PyPI and Release Management

This guide covers the process of publishing Llama-GPU to PyPI and managing releases.

## Table of Contents

- [Prerequisites](#prerequisites)
- [PyPI Account Setup](#pypi-account-setup)
- [Package Preparation](#package-preparation)
- [Publishing to PyPI](#publishing-to-pypi)
- [TestPyPI Publishing](#testpypi-publishing)
- [Release Management](#release-management)
- [Post-Publication](#post-publication)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

```bash
# Install build tools
pip install build twine

# Install additional tools for testing
pip install pytest pytest-cov black flake8 isort
```

### Package Structure Verification

Ensure your package structure is correct:

```bash
# Check package structure
tree -I 'venv|__pycache__|*.pyc|.git|.pytest_cache' -a

# Expected structure:
Llama-GPU/
├── src/
│   ├── backend/
│   ├── utils/
│   └── llama_gpu.py
├── tests/
├── docs/
├── examples/
├── scripts/
├── setup.py
├── MANIFEST.in
├── requirements.txt
├── README.md
└── LICENSE
```

## PyPI Account Setup

### 1. Create PyPI Account

1. Go to [PyPI](https://pypi.org/account/register/)
2. Create an account with a unique username
3. Verify your email address
4. Enable two-factor authentication (recommended)

### 2. Create TestPyPI Account

1. Go to [TestPyPI](https://test.pypi.org/account/register/)
2. Create an account (can use same username as PyPI)
3. Verify your email address

### 3. Configure Authentication

Create a `~/.pypirc` file for secure authentication:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

**Note**: Replace `your-token-here` with your actual PyPI API tokens.

## Package Preparation

### 1. Update Version

Before publishing, update the version in `setup.py`:

```python
setup(
    name="llama-gpu",
    version="1.0.0",  # Update this version
    # ... rest of setup configuration
)
```

### 2. Update Changelog

Add a new version entry to `CHANGELOG.md`:

```markdown
## [1.0.0] - 2024-01-XX

### Added
- Initial release with multi-backend support
- AWS GPU instance optimization
- Batch and streaming inference
- Comprehensive testing suite
```

### 3. Run Quality Checks

```bash
# Run all tests
python -m pytest tests/ -v

# Check code formatting
black --check src/ tests/
isort --check-only src/ tests/

# Run linter
flake8 src/ tests/

# Check package metadata
python setup.py check --metadata --strict
```

### 4. Build Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build source distribution and wheel
python -m build

# Verify the build
ls -la dist/
```

### 5. Check Package

```bash
# Check package metadata
twine check dist/*

# Test installation
pip install dist/*.whl --force-reinstall
```

## Publishing to PyPI

### 1. TestPyPI First (Recommended)

Always test on TestPyPI before publishing to PyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ llama-gpu
```

### 2. Publish to PyPI

Once tested on TestPyPI:

```bash
# Upload to PyPI
twine upload dist/*

# Verify upload
pip install llama-gpu --upgrade
```

### 3. Verify Publication

```bash
# Check package on PyPI
pip show llama-gpu

# Test import
python -c "from llama_gpu import LlamaGPU; print('Package installed successfully!')"
```

## TestPyPI Publishing

### When to Use TestPyPI

- Testing package installation
- Verifying metadata and dependencies
- Testing CI/CD workflows
- Pre-release validation

### TestPyPI Workflow

```bash
# 1. Build package
python -m build

# 2. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 3. Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ llama-gpu

# 4. Test functionality
python -c "from llama_gpu import LlamaGPU; print('TestPyPI package works!')"
```

## Release Management

### 1. Create GitHub Release

After publishing to PyPI:

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Title: `Llama-GPU v1.0.0 - Initial Release`
5. Description: Copy from CHANGELOG.md
6. Upload built packages (optional)

### 2. Update Documentation

```bash
# Update version in documentation
sed -i 's/version = "1.0.0"/version = "1.1.0"/' setup.py

# Update changelog
# Add new version entry to CHANGELOG.md
```

### 3. Tag Release

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Post-Publication

### 1. Monitor Installation

```bash
# Check download statistics (if available)
pip install pip-download-stats
pip-download-stats llama-gpu
```

### 2. Community Engagement

- Monitor GitHub issues and discussions
- Respond to user questions
- Review and merge pull requests
- Update documentation based on feedback

### 3. Version Planning

- Plan next release features
- Update roadmap
- Create milestone for next version

## Automated Publishing

### GitHub Actions Workflow

Add to `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Environment Setup

1. Add `PYPI_API_TOKEN` to GitHub repository secrets
2. Create API token on PyPI with upload permissions
3. Add token to repository settings

## Troubleshooting

### Common Issues

#### 1. Package Already Exists

```bash
# Error: File already exists
# Solution: Update version number in setup.py
```

#### 2. Authentication Failed

```bash
# Error: 401 Unauthorized
# Solution: Check ~/.pypirc file and API tokens
```

#### 3. Invalid Package Metadata

```bash
# Error: Invalid metadata
# Solution: Run twine check dist/* and fix issues
```

#### 4. Missing Dependencies

```bash
# Error: Missing required dependencies
# Solution: Update install_requires in setup.py
```

### Debug Commands

```bash
# Check package contents
tar -tzf dist/llama_gpu-1.0.0.tar.gz

# Verify wheel contents
unzip -l dist/llama_gpu-1.0.0-py3-none-any.whl

# Test package installation
pip install dist/*.whl --force-reinstall --no-deps
```

### Rollback Procedure

If a bad version is published:

1. **Don't delete the version** (PyPI doesn't allow this)
2. **Publish a new version** with fixes
3. **Update documentation** to point to correct version
4. **Communicate** the issue to users

## Best Practices

### 1. Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version before each release
- Keep changelog up to date

### 2. Quality Assurance

- Always test on TestPyPI first
- Run full test suite before publishing
- Check package metadata thoroughly

### 3. Documentation

- Keep README.md updated
- Include installation instructions
- Provide usage examples

### 4. Security

- Use API tokens instead of passwords
- Enable two-factor authentication
- Regularly rotate tokens

## Next Steps After Publishing

1. **Monitor feedback** from the community
2. **Address issues** and feature requests
3. **Plan next release** based on user needs
4. **Maintain documentation** and examples
5. **Engage with users** through GitHub discussions

---

## Quick Reference

### Publishing Checklist

- [ ] Update version in `setup.py`
- [ ] Update `CHANGELOG.md`
- [ ] Run all tests: `python -m pytest tests/ -v`
- [ ] Check code formatting: `black --check src/ tests/`
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test installation from TestPyPI
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Create GitHub release
- [ ] Tag release: `git tag -a v1.0.0 -m "Release v1.0.0"`

### Useful Commands

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install llama-gpu

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ llama-gpu
```

---

**Note**: This guide assumes you have the necessary permissions and API tokens for PyPI. Always test on TestPyPI before publishing to the main PyPI repository. 