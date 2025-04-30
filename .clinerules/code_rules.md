# Core Coding Rules

## Error Handling
- Never generate a `try-except` block under any circumstance unless explicitly requested by the user.

## Python File Headers
- All `.py` files must begin directly with import statements.
- Do not include a shebang line (e.g., `#!/usr/bin/env python3`) at the top unless explicitly instructed.
- Do not place a file-level docstring or any module-level documentation block above the imports.
- No content (comments, docstrings, or otherwise) should precede the imports unless specifically requested.
