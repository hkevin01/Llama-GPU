# Project Structure

This document outlines the organization of the Llama-GPU project.

## Directory Structure

```plaintext
llama-gpu/
├── config/                 # Configuration files
│   ├── env/               # Environment-specific configurations
│   └── default.yml        # Default configuration
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── guides/           # User guides
│   └── development/      # Development documentation
├── scripts/              # Utility scripts
│   ├── setup/           # Setup and installation scripts
│   └── tools/           # Development tools
├── src/                  # Source code
│   ├── backends/        # GPU backend implementations
│   ├── models/          # Model implementations
│   ├── server/          # Server implementation
│   └── utils/           # Utility functions
│       └── amd/         # AMD-specific utilities
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── performance/    # Performance tests
└── examples/            # Example implementations
```

## Key Components

### Source Code (`src/`)

- `backends/`: GPU backend implementations (ROCm, CUDA)
- `models/`: Core model implementations
- `server/`: WebSocket server and API implementations
- `utils/`: Utility functions and helpers

### Configuration (`config/`)

- Environment-specific configurations
- Default settings
- Logging configurations

### Documentation (`docs/`)

- API documentation
- User guides
- Development guides
- Architecture documentation

### Scripts (`scripts/`)

- Setup and installation scripts
- Development utilities
- Deployment scripts

### Tests (`tests/`)

- Unit tests
- Integration tests
- Performance benchmarks

## File Naming Conventions

- Python files: lowercase with underscores (e.g., `file_name.py`)
- Test files: prefix with `test_` (e.g., `test_model.py`)
- Configuration files: lowercase with descriptive names (e.g., `logging_config.yml`)
- Documentation: uppercase with underscores (e.g., `API_REFERENCE.md`)
