## 2024-05-27 - Claim page full redesign
**Learning:** Mobile users need large touch targets and easily scannable feedback. A generic success message without a clear timeline leaves users confused about the next steps. Improper ARIA labels reduce accessibility for form components.
**Action:** Use CSS variables for a consistent mobile-first bottom-sheet design. Establish 48px min-heights for touch targets. Implement visual timelines for multi-step async processes. Use explicit `<span class="sr-only">` with `aria-hidden="true"` visual indicators rather than relying solely on `aria-label="required"`.
**Files:** `templates/index.html`, `static/style.css`, `main.py`
