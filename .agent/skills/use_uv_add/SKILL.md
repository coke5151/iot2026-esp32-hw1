---
name: Use uv add for Python packages
description: 確保在安裝 Python 套件時使用 uv add 而不是 pip install，以同步更新 pyproject.toml
---

# Instructions
When you need to install Python packages in this workspace, follow these rules:

1. **ALWAYS use `uv add <package_name>`** to install packages.
2. **NEVER use `pip install <package_name>`**.
3. **NEVER use `uv pip install <package_name>`**.

Using `uv add` ensures that the `pyproject.toml` (`c:\Users\user\Desktop\4112064214\iot2026-esp32-hw1\pyproject.toml`) file is updated synchronously with the installation of dependencies.

Example:
If the user asks "install requests", you should run:
`uv add requests`
