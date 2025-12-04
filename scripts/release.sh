#!/bin/bash
# Release script for docu-crawler
# Usage: ./scripts/release.sh <version>
# Example: ./scripts/release.sh 1.1.0

set -e

if [ -z "$1" ]; then
    echo "Error: Version number required"
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 1.1.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

# Validate version format (basic check)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Invalid version format. Expected format: X.Y.Z (e.g., 1.1.0)"
    exit 1
fi

echo "Releasing version ${VERSION}..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Warning: You're not on the main branch (current: ${CURRENT_BRANCH})"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo "Error: Working directory is not clean. Please commit or stash changes first."
    exit 1
fi

# Verify version matches code
PYTHON_VERSION=$(python -c "import src; print(src.__version__)" 2>/dev/null || echo "")
if [ -n "$PYTHON_VERSION" ] && [ "$PYTHON_VERSION" != "$VERSION" ]; then
    echo "Error: Version mismatch!"
    echo "  Code version: ${PYTHON_VERSION}"
    echo "  Release version: ${VERSION}"
    echo "Please update version in setup.py and src/__init__.py first"
    exit 1
fi

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: Tag ${TAG} already exists"
    exit 1
fi

# Create and push tag
echo "Creating tag ${TAG}..."
git tag -a "$TAG" -m "Release ${TAG}"
git push origin "$TAG"

echo ""
echo "✓ Tag ${TAG} created and pushed"
echo "✓ GitHub Actions will automatically:"
echo "  - Run tests"
echo "  - Build the package"
echo "  - Publish to PyPI"
echo "  - Create a GitHub release"
echo ""
echo "Monitor progress at: https://github.com/dataiscool/docu-crawler/actions"

