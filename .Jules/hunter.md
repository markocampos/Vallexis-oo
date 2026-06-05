## 2024-05-19 - Strict Validation Trimming and Double Submit Flag

**Learning:** When native HTML constraint validation (e.g., `pattern` attributes) runs, it blocks form submission before Javascript `submit` event listeners are fired. Therefore, trimming input values to strip accidental spacing within the `submit` handler fails. Trimming must occur on `input` and `blur` events so the clean value exists in the DOM when native validation is evaluated. Relying only on `button.disabled = true` is fragile against rapid double-clicks due to slight DOM delays; always implement an explicit JavaScript boolean state lock for async form handling.

**Action:** When validating forms, trim user inputs on `blur` or `input` to keep validation states accurate. Wrap async submit handlers with explicit state flags like `isSubmitting` using try/finally blocks.
