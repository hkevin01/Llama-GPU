# Development Guide

This guide will help you get started with developing Llama-GPU.

## Prerequisites

- Python 3.8 or later
- ROCm 6.3 or later (for AMD GPUs)
- Git
- Virtual environment tool (venv)

## Setting Up Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/hkevin01/Llama-GPU.git
   cd Llama-GPU
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards.

3. Run the test suite:

   ```bash
   pytest
   ```

4. Format your code:

   ```bash
   black .
   isort .
   ```

5. Run type checking:

   ```bash
   mypy src tests
   ```

6. Commit your changes:

   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

7. Push your changes and create a pull request.

## Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

## Testing

- Write unit tests for all new features
- Place tests in the `tests/` directory
- Follow test file naming convention: `test_*.py`
- Maintain test coverage above 80%

## Documentation

- Update documentation for any new features
- Include docstrings in your code
- Update the README.md if needed
- Add examples for new features

## Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Test updates
- chore: Maintenance tasks

## Project Structure

Please refer to [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed information about the project organization.

## Getting Help

- Check the [documentation](docs/)
- Open an issue for bugs or feature requests
- Join our community discussions

## License

By contributing to this project, you agree that your contributions will be licensed under its MIT license.
