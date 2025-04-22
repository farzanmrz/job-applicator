# General Rules

## Docstring Format
- When generating any new file, class, function, or similar entity that requires a multiline docstring, include ONLY the single-line summary.
- Do not add any additional sections or content (such as Args, Returns, or other explanatory blocks) after the summary line, unless explicitly requested.

## ACT Mode Efficiency
- In ACT mode, prioritize executing the planned step directly and efficiently.
- For standard file operations (read_file, write_to_file, replace_in_file) or simple command executions (execute_command for non-destructive actions), perform the action promptly based on the plan.
- Avoid excessive deliberation on alternatives or edge cases for these standard operations unless the plan explicitly requires complex analysis for that specific step. Trust the plan and the iterative review process.
