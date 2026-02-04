# Contributing to AnyCam2Ros

Thank you for your interest in contributing to AnyCam2Ros! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Provide detailed information including:
  - Python version (`python3 --version`)
  - ROS2 distribution
  - OS and version
  - Steps to reproduce
  - Expected vs actual behavior

### Submitting Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Test** your changes thoroughly
5. **Commit** with clear, descriptive messages:
   ```bash
   git commit -m "feat: add support for USB camera hot-plug detection"
   ```
6. **Push** to your fork and create a Pull Request

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `style:` — Code style changes (formatting, etc.)
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [ruff](https://github.com/astral-sh/ruff) for linting:
  ```bash
  ruff check scripts/
  ruff format scripts/
  ```
- Add type hints where practical
- Document functions with docstrings

### Shell Scripts

- Use `#!/bin/bash` shebang
- Include `set -euo pipefail` for safety
- Quote all variables: `"$VAR"` not `$VAR`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/AnyCam2Ros.git
cd AnyCam2Ros

# Install development dependencies
pip install ruff

# Run linter
ruff check scripts/
```

## Testing

Before submitting:

1. Test interactive mode on a system with cameras
2. Test `--from-config` with the example config
3. Verify generated scripts work with ROS2

## Questions?

Feel free to open an issue for questions or discussions. We're happy to help!
