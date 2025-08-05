# Directory Structure Guide

## Overview

This document explains the organization of the Llama-GPU project directories and what belongs in each location.

## Root Level Directories

### `/src` - Source Code

- Main application code
- Core functionality
- Organized by feature/module

```plaintext
src/
├── backends/     # GPU backend implementations
├── server/       # Server and API implementations
├── utils/        # Utility functions
│   └── amd/     # AMD-specific utilities
└── models/       # Model implementations
```

### `/scripts` - Utility Scripts

- Setup and installation scripts
- Network and server management
- Development utilities

```plaintext
scripts/
├── setup/       # Installation and setup scripts
├── network/     # Network and server management scripts
└── utils/       # General utility scripts
```

### `/tests` - Test Suite

- Unit tests
- Integration tests
- Test utilities and helpers
- Test configuration

```plaintext
tests/
├── unit/        # Unit tests
├── integration/ # Integration tests
└── utils/       # Test utilities
```

### `/examples` - Example Code

- Demo applications
- Usage examples
- Integration examples

```plaintext
examples/
├── demos/       # Demo applications
└── tutorials/   # Step-by-step guides
```

### `/docs` - Documentation

- API documentation
- User guides
- Development guides

```plaintext
docs/
├── api/         # API documentation
├── guides/      # User and development guides
└── examples/    # Code examples and tutorials
```

### `/config` - Configuration

- Application configuration
- Environment settings
- Default configurations

```plaintext
config/
├── env/         # Environment-specific configs
└── defaults/    # Default configuration files
```

### `/logs` - Log Files

- Application logs
- Server logs
- Debug logs

```plaintext
logs/
├── server/      # Server logs
├── debug/       # Debug logs
└── archive/     # Historical logs
```

### `/gui` - User Interface

- GUI components
- Frontend assets
- Interface configurations

```plaintext
gui/
├── components/  # UI components
├── assets/      # Static assets
└── styles/      # Style definitions
```

## File Naming Conventions

- Python files: lowercase with underscores (e.g., `file_name.py`)
- Test files: prefix with `test_` (e.g., `test_model.py`)
- Script files: descriptive, lowercase (e.g., `install_dependencies.sh`)
- Configuration files: lowercase with descriptive names (e.g., `logging_config.yml`)

## Best Practices

1. **Keep the Root Clean**
   - Avoid placing new files in the root directory
   - Move files to appropriate subdirectories

2. **Organize by Feature**
   - Group related files together
   - Create new subdirectories for new features

3. **Follow Conventions**
   - Use consistent naming
   - Maintain directory structure
   - Update documentation when adding new directories

4. **Documentation**
   - Keep this guide updated
   - Document new directories
   - Explain any deviations from standards
