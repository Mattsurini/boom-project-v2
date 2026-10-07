---
name: python-git-package-install
description: Use when installing git Python package. Install into venv.
---
# Python Git Package Installation Skill

## Purpose
Install Python packages from git repositories (local or remote) into a project's virtual environment with verification.

## When to Use
- Installing astrology libraries like flatlib, stellium
- Installing development dependencies from source
- Testing packages before they are published

## Procedure

### 1. Environment Preparation
```bash
# Check if venv exists, create if needed
if [ ! -d "/e/Boom Project/.venv" ]; then
    /e/Boom Project/.venv/Scripts/python.exe -m venv /e/Boom Project/.venv
fi
```

### 2. Use Explicit Venv Paths
Always use the virtual environment's Python and pip executables directly:
- Python: `/e/Boom Project/.venv/Scripts/python.exe`
- Pip: `/e/Boom Project/.venv/Scripts/pip.exe`

**Why**: Avoids PATH issues and ensures packages install in the correct environment.

### 3. Installing from Remote Git
```bash
/e/Boom Project/.venv/Scripts/pip install git+https://github.com/username/repo.git
```

### 4. Installing from Local Clone
```bash
# After cloning the repository
/e/Boom Project/.venv/Scripts/pip install /e/Boom Project/package-directory
# or for editable install
/e/Boom Project/.venv/Scripts/pip install -e /e/Boom Project/package-directory
```

### 5. Verification
After installation, verify the package works:
```python
/e/Boom Project/.venv/Scripts/python.exe -c "import package_name; print(package_name.__version__)"
```

### 6. Handling Paths with Spaces
When paths contain spaces:
- Use quoted paths in execute_code calls
- Prefer using execute_code over terminal for paths with spaces
- Use short 8.3 paths if available

**Pitfall**: Terminal tool fails with "too many arguments" on paths with spaces - **Always** use execute_code with explicit venv paths when paths contain spaces.

### 7. Fixing Venv Issues
If pip fails with "No Python at" errors pointing to wrong python:
1. Delete the venv: `rm -rf /e/Boom Project/.venv`
2. Recreate: `/e/Boom Project/.venv/Scripts/python.exe -m venv /e/Boom Project/.venv`
3. Retry installation

**Why**: Venv configuration can become corrupted or point to wrong Python interpreter.

## Verification Steps
After installation, always verify:
1. Package imports without error
2. Version can be retrieved
3. Basic functionality works (for astrology packages: create a chart, calculate positions)

## Example: Installing flatlib
```bash
/e/Boom Project/.venv/Scripts/pip install git+https://github.com/flatangle/flatlib.git
```
Then verify:
```bash
/e/Boom Project/.venv/Scripts/python.exe -c "import flatlib; print(flatlib.__version__)"
```

## Example: Installing stellium
```bash
/e/Boom Project/.venv/Scripts/pip install git+https://github.com/katelouie/stellium.git
```
Then verify:
```bash
/e/Boom Project/.venv/Scripts/python.exe -c "import stellium; print(stellium.__version__)"
```
# Then test chart calculation
```
```
```
```
```python
from stellium import ChartBuilder, Native
import pytz
from datetime import datetime
# ... chart calculation code
```
```
```
```

## References
- See .hermes.md for project-specific environment details
- Refer to venv troubleshooting in project setup documentation
- Check pyproject.toml/setup.py for package-specific installation notes
