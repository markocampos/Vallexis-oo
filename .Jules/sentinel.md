## 2024-06-04 - Fix Path Traversal in match_and_fulfill
**Vulnerability:** Path Traversal via `reference_number` used in `output_filename` and `output_path`.
**Learning:** `reference_number` in `main.py:match_and_fulfill` was taken directly from user input (claim or webhook) and used to construct a file path without sanitization, leading to a path traversal vulnerability.
**Prevention:** Sanitize user input (e.g., using `re.sub(r"[^a-zA-Z0-9_-]", "", input)`) before using it to construct file paths or other sensitive operations.
