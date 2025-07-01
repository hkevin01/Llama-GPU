# Contributing to Llama-GPU

Thank you for your interest in contributing to Llama-GPU! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python and machine learning concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/Llama-GPU.git
   cd Llama-GPU
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/hkevin01/Llama-GPU.git
   ```

## Development Setup

### Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

3. Run the setup scripts:
   ```bash
   # For local development
   ./scripts/setup_local.sh
   
   # For AWS development
   ./scripts/setup_aws.sh
   ```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_backend.py -v
python -m pytest tests/test_aws_detection.py -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- Maximum line length: 127 characters
- Use type hints for function parameters and return values
- Use docstrings for all public functions and classes

### Code Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Linting

We use `flake8` for linting:

```bash
# Run linter
flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup
- Mock external dependencies

### Test Structure

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = "test input"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == "expected output"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_backend.py -v

# Run specific test function
python -m pytest tests/test_backend.py::test_specific_function -v

# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=html
```

## Submitting Changes

### Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following the style guide
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   python -m pytest tests/ -v
   black --check src/ tests/
   flake8 src/ tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build or tool changes

Examples:
```
feat(backend): add support for ROCm backend
fix(aws): resolve AWS detection issue
docs(readme): update installation instructions
```

### Pull Request Guidelines

- Provide a clear description of the changes
- Include any relevant issue numbers
- Ensure all tests pass
- Update documentation if needed
- Add examples for new features

## Issue Reporting

### Before Reporting

1. Check existing issues to avoid duplicates
2. Search the documentation for solutions
3. Try the troubleshooting guide

### Issue Template

When reporting an issue, include:

- **Description**: Clear description of the problem
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, GPU type, etc.
- **Error messages**: Full error messages and stack traces

### Example Issue

```
**Description**
The CUDA backend fails to load on Ubuntu 20.04 with NVIDIA RTX 3080.

**Steps to reproduce**
1. Install Llama-GPU following the README
2. Run: python -c "from llama_gpu import LlamaGPU; llama = LlamaGPU('model_path')"
3. Observe error

**Expected behavior**
CUDA backend should load successfully.

**Actual behavior**
RuntimeError: CUDA not available

**Environment**
- OS: Ubuntu 20.04
- Python: 3.9.7
- GPU: NVIDIA RTX 3080
- CUDA: 11.8

**Error messages**
[Include full error traceback]
```

## Feature Requests

### Guidelines

- Describe the feature clearly
- Explain the use case and benefits
- Consider implementation complexity
- Check if similar features exist

### Feature Request Template

```
**Feature Description**
Brief description of the feature.

**Use Case**
Explain when and why this feature would be useful.

**Proposed Implementation**
Optional: suggest how to implement the feature.

**Alternatives Considered**
Optional: describe alternatives you considered.

**Additional Context**
Any other relevant information.
```

## Documentation

### Documentation Guidelines

- Write clear, concise documentation
- Include code examples
- Keep documentation up to date
- Use proper markdown formatting

### Documentation Structure

- `README.md`: Project overview and quick start
- `docs/usage.md`: Detailed usage guide
- `docs/api.md`: API reference
- `docs/troubleshooting.md`: Common issues and solutions
- `docs/benchmarks.md`: Performance benchmarks

### Updating Documentation

When adding new features:

1. Update relevant documentation files
2. Add code examples
3. Update API documentation
4. Add troubleshooting information if needed

## Getting Help

### Resources

- [Documentation](docs/)
- [Issues](https://github.com/hkevin01/Llama-GPU/issues)
- [Discussions](https://github.com/hkevin01/Llama-GPU/discussions)

### Contact

- Create an issue for bugs or feature requests
- Use discussions for questions and general help
- Follow the code of conduct in all interactions

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- Contributor statistics

Thank you for contributing to Llama-GPU! 🚀
