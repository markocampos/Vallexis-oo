## 2024-06-04 - Fix Path Traversal in match_and_fulfill
**Vulnerability:** Path Traversal via `reference_number` used in `output_filename` and `output_path`.
**Learning:** `reference_number` in `main.py:match_and_fulfill` was taken directly from user input (claim or webhook) and used to construct a file path without sanitization, leading to a path traversal vulnerability.
**Prevention:** Sanitize user input (e.g., using `re.sub(r"[^a-zA-Z0-9_-]", "", input)`) before using it to construct file paths or other sensitive operations.
## 2024-06-04 - Unbounded File Upload in OCR Fallback
**Vulnerability:** The `/api/ocr/fallback` endpoint accepted file uploads without checking the file size before loading it entirely into memory using `await file.read()`.
**Learning:** This could lead to a memory exhaustion Denial of Service (DoS) attack if a malicious user uploads extremely large files. The fallback OCR mechanism was missing a basic safety guard.
**Prevention:** Always implement size limits for user-uploaded files, either at the proxy level (e.g., Caddy/Nginx), globally in the framework, or specifically within the endpoint logic before or during the read process.
## 2024-06-04 - HTML Injection in Email Service
**Vulnerability:** HTML injection in `email_service.py:19` because user input `buyer_name` was directly embedded inside an f-string for generating an email HTML payload.
**Learning:** Raw user input should never be interpolated into HTML payloads without escaping. It allows attackers to run scripts or distort content structure in the client.
**Prevention:** Always use `html.escape()` or dedicated templating engines (like Jinja2 with autoescaping) to sanitize user input prior to rendering HTML.
## 2026-06-04 - Hardcoded Credentials in Resend Setup\n**Vulnerability:** A hardcoded dummy API key fallback was used for Resend initialization.\n**Learning:** Relying on default fallback strings for API keys hides missing configuration errors and could be abused or cause runtime type errors when used blindly.\n**Prevention:** Rely strictly on environment variables for sensitive tokens and handle their absence explicitly using proper branching (e.g. `if api_key:`) to enable mock fallbacks in testing environments.
## 2024-06-04 - Fix Unvalidated File Upload in OCR Fallback
**Vulnerability:** The `/api/ocr/fallback` endpoint allowed uploading files of any type and content because it lacked validation on `file.content_type` and didn't verify file magic bytes, allowing for potential malicious file uploads.
**Learning:** Checking the `content_type` of a request is not enough, as it can be easily spoofed. Ensuring that the file content's magic bytes actually match the claimed image format provides an additional and necessary layer of defense.
**Prevention:** Always validate both the `content_type` header and the internal file signature (magic bytes) against an allowed list when handling file uploads.
