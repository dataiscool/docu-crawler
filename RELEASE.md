# Release Process

This document describes how to release a new version of docu-crawler.

## Automated Release (Recommended)

The release process is fully automated via GitHub Actions. You have two options:

### Option 1: Tag-Based Release (Recommended)

1. **Update version numbers** in:
   - `setup.py` (line 11)
   - `src/__init__.py` (line 10)

2. **Update CHANGELOG.md** with the new version's changes

3. **Commit and push** to main:
   ```bash
   git add setup.py src/__init__.py CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

4. **Create and push a version tag**:
   ```bash
   # On Linux/Mac:
   ./scripts/release.sh 1.1.0
   
   # On Windows (PowerShell):
   .\scripts\release.ps1 1.1.0
   
   # Or manually:
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

5. **GitHub Actions will automatically**:
   - Run tests across Python 3.9-3.12
   - Build the package (sdist + wheel)
   - Verify version matches code
   - Publish to PyPI
   - Create a GitHub release with changelog

### Option 2: Manual Workflow Dispatch

1. Go to: https://github.com/dataiscool/docu-crawler/actions/workflows/release.yml
2. Click "Run workflow"
3. Enter the version number (e.g., `1.1.0`)
4. Click "Run workflow"

The workflow will verify the version matches your code and proceed with the release.

## Manual Release (Fallback)

If automation fails, you can release manually:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Required Secrets

For automated releases, ensure these GitHub Secrets are configured:

- `PYPI_API_TOKEN`: Your PyPI API token (get from https://pypi.org/manage/account/token/)

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Pre-Release Checklist

- [ ] Version numbers updated in `setup.py` and `src/__init__.py`
- [ ] CHANGELOG.md updated with new version entry
- [ ] All tests passing locally
- [ ] Code reviewed and merged to main
- [ ] Working directory clean (no uncommitted changes)
- [ ] PyPI token configured in GitHub Secrets

