# Contributing to Doc Crawler

Thank you for considering contributing to Doc Crawler! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dataiscool/doc-crawler.git
   cd doc-crawler
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install pytest flake8
   ```

## Running Tests

Run tests using pytest:
```bash
pytest
```

## Code Style

This project follows PEP 8 style guidelines. You can check your code with:
```bash
flake8 src
```

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test thoroughly

3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```

4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a pull request

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. The GitHub Action will automatically build and publish to PyPI

## Questions?

Feel free to open an issue if you have any questions or need help.