## 2024-05-20 - Improve Docs and Seller Dashboard UI
**Learning:** Proper separation of HTML, CSS, and JS enhances maintainability. Semantic HTML combined with custom CSS variables allows for scalable and clear dashboard and documentation layouts without relying on external frameworks.
**Action:** When redesigning simple UIs, always establish a clear structure (e.g., using sidebars for docs and semantic sections for dashboards), move inline styles to dedicated CSS files, and define custom CSS variables in the `:root` pseudo-class for consistent styling.
**Files:** dashboard_ui/index.html, dashboard_ui/css/style.css, dashboard_ui/js/script.js, docs_ui/index.html, docs_ui/css/style.css

## 2026-06-05 - Claim page redesign
**Learning:** Mobile users need large touch targets and clear trust signals when handling payment claims. Replacing static text with an animated progress timeline reduces anxiety during async operations.
**Action:** Always ensure minimum 48px touch targets for forms on mobile devices, and map async steps to visual timelines for user clarity.
**Files:** templates/index.html, static/style.css
