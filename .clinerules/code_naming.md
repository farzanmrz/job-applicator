# Naming Conventions

## Identifier Naming (Variables, Functions, etc.)
- Identifiers must follow this rule: a single underscore may be used after a short descriptive prefix (e.g., `simple_setup`).
- If the name continues beyond that point, further words must be added using camelCase, not additional underscores (e.g., `simple_setupConfig` is valid, `simple_setup_config` is not).
- Under no circumstance should more than one underscore appear in an identifier, unless explicitly allowed.

## Single-Class File Naming
- If a `.py` file contains only a single defined class, the filename must exactly match the class name, including its casing (e.g., class `BaseClassExample` requires filename `BaseClassExample.py`).
