# Contributing to Docu Crawler

Thank you for considering contributing to Docu Crawler! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dataiscool/docu-crawler.git
   cd docu-crawler
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install pytest flake8 mypy types-requests types-beautifulsoup4
   ```

## Running Tests

Run tests using pytest:
```bash
pytest
```

## Code Quality

This project follows PEP 8 style guidelines and uses type hints.

Check code style:
```bash
flake8 src
```

Check type hints:
```bash
mypy src
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