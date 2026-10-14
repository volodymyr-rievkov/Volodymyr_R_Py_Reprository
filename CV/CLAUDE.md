## Code style

- Comments/docstrings: brief, ~3 lines max — orientation, not rationale. Never hardcode volatile specifics
  (table/schema names, PRD decision numbers, config values) in them; point to the relevant `.specs/*/PRD.md`
  instead. Those values change, and hunting down every comment that quoted them is wasted churn.

## Student variant

The student number is in the `STUDENT_NUMBER` file at the repo root (17). Lab variant = number mod 15 (0 → 15), so
17 → variant 2. See each `Lab_N/LAB_N_CONTEXT.md` for the task list. Lab 1: no OpenCV/PIL/scikit-image for the
algorithm itself; `matplotlib` only for reading, showing and saving images.

# Python Environment & Package Management with uv

Use uv exclusively for all Python actions in this project. 

## Strict Rules
- Never use pip, pip-tools, poetry, virtualenv, or conda.
- Always check for a `uv.lock` before performing operations.
- Do not attempt to manually source `.venv/bin/activate`.

## Approved Commands
- Install dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Synchronize environment: `uv sync`
- Running scripts/tools: `uv run <script.py>` or `uv run pytest`