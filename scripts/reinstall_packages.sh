#!/bin/bash

# Script to uninstall and reinstall all packages in the monorepo
# This helps refresh dependencies and resolve installation issues

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGES_DIR="$PROJECT_ROOT/packages"

echo "=================================="
echo "Uninstalling all local packages..."
echo "=================================="

# List of packages in dependency order (dependencies first)
PACKAGES=(
    "job-agent-platform-contracts"
    "cvs-repository"
    "jobs-repository"
    "essay-repository"
    "job-agent-backend"
    "telegram_bot"
)

# Uninstall all packages
for package in "${PACKAGES[@]}"; do
    echo ""
    echo "Uninstalling: $package"
    pip uninstall -y "$package" 2>/dev/null || echo "  (not installed, skipping)"
done

echo ""
echo "=================================="
echo "Reinstalling all local packages..."
echo "=================================="

# Reinstall all packages in editable mode with dev dependencies
for package in "${PACKAGES[@]}"; do
    package_path="$PACKAGES_DIR/$package"
    if [ -d "$package_path" ]; then
        echo ""
        echo "Installing: $package"
        pip install -e "$package_path[dev]"
    else
        echo "  Warning: Package directory not found: $package_path"
    fi
done

echo ""
echo "=================================="
echo "Done! All packages reinstalled."
echo "=================================="
