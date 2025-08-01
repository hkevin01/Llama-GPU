# Llama-GPU Project Reorganization Plan

## New Directory Structure

```
Llama-GPU/
├── README.md                          # Main project README
├── LICENSE                            # Project license
├── .gitignore                         # Git ignore rules
├── pyproject.toml                     # Modern Python project config
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Container orchestration
├── Dockerfile                         # Container definition
│
├── core/                              # Main Python package
│   ├── src/
│   │   └── llama_gpu/                 # Main package
│   │       ├── __init__.py
│   │       ├── api/                   # API modules
│   │       ├── backend/               # Backend implementations
│   │       ├── models/                # Model management
│   │       ├── inference/             # Inference engines
│   │       ├── monitoring/            # System monitoring
│   │       ├── utils/                 # Utility functions
│   │       └── config/                # Configuration management
│   ├── tests/                         # All Python tests
│   ├── examples/                      # Usage examples
│   └── scripts/                       # Helper scripts
│
├── frontend/                          # All GUI applications
│   ├── main-interface/                # Primary Llama-GPU Interface
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── README.md
│   └── archive/                       # Legacy/unused GUIs
│       └── project-tracker/           # Old project tracker
│
├── tools/                             # Development and deployment tools
│   ├── scripts/                       # Build/deployment scripts
│   ├── benchmarks/                    # Performance benchmarking
│   ├── deployment/                    # Deployment configurations
│   └── ci/                           # CI/CD configurations
│
├── docs/                              # All documentation
│   ├── api/                          # API documentation
│   ├── guides/                       # User guides
│   ├── development/                   # Developer documentation
│   ├── deployment/                    # Deployment guides
│   └── archive/                       # Historical documentation
│
└── archive/                           # Deprecated/legacy files
    ├── old-tests/                     # Deprecated test files
    ├── temp-files/                    # Temporary development files
    └── legacy-configs/                # Old configuration files
```

## Key Improvements

### 1. Clear Separation of Concerns
- **core/**: Pure Python package with clear module structure
- **frontend/**: All UI applications centralized
- **tools/**: Development and operational tooling
- **docs/**: Comprehensive documentation hub

### 2. Modern Python Structure
- Use `pyproject.toml` for modern Python packaging
- Clean package hierarchy under `core/src/llama_gpu/`
- Consolidated test suite in `core/tests/`
- Examples and scripts properly organized

### 3. Frontend Consolidation
- Active GUI in `frontend/main-interface/`
- Legacy GUIs archived but preserved
- Clear distinction between active and archived projects

### 4. Documentation Organization
- API docs separated from user guides
- Development documentation for contributors
- Deployment guides for operations
- Historical docs preserved in archive

### 5. Tooling and CI/CD
- Build scripts in dedicated location
- Benchmarking tools organized
- CI/CD configurations centralized
- Deployment templates structured

## Migration Strategy

1. **Phase 1**: Create new structure and move core Python package
2. **Phase 2**: Consolidate and organize frontend applications
3. **Phase 3**: Organize documentation and remove duplicates
4. **Phase 4**: Clean up tools, scripts, and CI/CD
5. **Phase 5**: Archive deprecated files and clean root directory
6. **Phase 6**: Update all import paths and references
7. **Phase 7**: Verify functionality and create migration notes
