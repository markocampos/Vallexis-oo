## 2024-05-20 - Improve Docs and Seller Dashboard UI
**Learning:** Proper separation of HTML, CSS, and JS enhances maintainability. Semantic HTML combined with custom CSS variables allows for scalable and clear dashboard and documentation layouts without relying on external frameworks.
**Action:** When redesigning simple UIs, always establish a clear structure (e.g., using sidebars for docs and semantic sections for dashboards), move inline styles to dedicated CSS files, and define custom CSS variables in the `:root` pseudo-class for consistent styling.
**Files:** dashboard_ui/index.html, dashboard_ui/css/style.css, dashboard_ui/js/script.js, docs_ui/index.html, docs_ui/css/style.css

## 2024-06-14 - Claim page redesign
**Learning:** Buyers need clear visual confirmation and progress tracking after submission, especially when wait times (like background matching) occur. Without it, they wonder if the claim worked.
**Action:** Always provide an explicit success state that explains what happens next. A step-by-step timeline is highly effective for setting expectations about background processing. Ensure mobile interfaces use bottom-sheet style layouts for better reachability and larger touch targets (48px) for mobile users.
**Files:** templates/index.html, static/style.css
