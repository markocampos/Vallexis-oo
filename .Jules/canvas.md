## 2024-06-03 - Claim Page Redesign
**Learning:** When handling API errors in UI using FastAPI, standard 422 validation errors return a list for `detail`, and custom HTTPExceptions might return a dictionary. Directly using `errorData.detail` in JavaScript can lead to `[object Object]` displaying in the UI. Also, dynamically updated status regions need `tabindex="-1"` to receive focus programmatically for accessibility.
**Action:** Ensure error responses are correctly parsed based on their type (`string`, `array`, or `object`). Add `tabindex="-1"` to any element that needs programmatic focus but is not naturally focusable.
**Files affected:** `templates/index.html`
