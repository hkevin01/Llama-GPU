# CI/CD Setup and Usage Guide

This document explains the continuous integration and deployment (CI/CD) workflow for the Llama-GPU project, including how contributors can use, extend, and troubleshoot the pipeline.

## Overview
- The CI/CD pipeline is managed via GitHub Actions (`.github/workflows/ci.yml`).
- It runs automated tests, linting, and builds for both CPU and GPU backends.
- Node.js lint/test jobs are included for frontend or utility scripts.
- All changes and test outputs are logged for traceability.

## Workflow Steps
1. **Trigger**: On push, pull request, or manual dispatch.
2. **Matrix Build**: Runs jobs for CPU and GPU (CUDA, ROCm) environments.
3. **Linting**: Python and Node.js code style checks.
4. **Testing**: Automated tests for all major modules and utilities.
5. **Coverage**: Reports code coverage for Python modules.
6. **Artifacts**: Test logs and coverage reports are uploaded as artifacts.

## How to Use
- **Local Testing**: Run `pytest` and `flake8` locally before pushing.
- **Manual Dispatch**: Trigger workflows from the GitHub Actions tab.
- **Debugging Failures**: Review logs in the Actions tab; check `logs/test_output.log` and `logs/CHANGELOG.md`.
- **Extending the Pipeline**: Edit `.github/workflows/ci.yml` to add new jobs or steps.

## Troubleshooting
- Ensure all dependencies are listed in `requirements.txt` and `package.json`.
- For GPU jobs, verify runner supports CUDA/ROCm (see workflow matrix).
- Check `.gitignore` to avoid committing logs, artifacts, or environment files.

## Contributor Notes
- All contributors should review this guide before submitting PRs.
- For questions, open an issue or consult the `CONTRIBUTING.md` file.

---
_Last updated: July 21, 2025_
