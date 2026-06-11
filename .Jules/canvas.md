## 2024-05-20 - Improve Docs and Seller Dashboard UI
**Learning:** Proper separation of HTML, CSS, and JS enhances maintainability. Semantic HTML combined with custom CSS variables allows for scalable and clear dashboard and documentation layouts without relying on external frameworks.
**Action:** When redesigning simple UIs, always establish a clear structure (e.g., using sidebars for docs and semantic sections for dashboards), move inline styles to dedicated CSS files, and define custom CSS variables in the `:root` pseudo-class for consistent styling.
**Files:** dashboard_ui/index.html, dashboard_ui/css/style.css, dashboard_ui/js/script.js, docs_ui/index.html, docs_ui/css/style.css
## 2024-06-11 - Claim Page UX & Form Robustness Redesign
**Learning:** Bypassing standard form validation to inject logic immediately on `input` forces trimming that disrupts user workflow, and using label structure incorrectly creates accessibility gaps for screen readers. Using temporary CSS properties `~` also blocked correct file mounting in FastAPI.
**Action:** Always trim text input values explicitly on `blur` instead of `input`. Use `.sr-only` class text coupled with visual `aria-hidden` tags instead of simply using `aria-label` tags. Explicitly declare static routing in FastAPI and explicitly use `/` notation for css href link paths in html templates.
**Files:** `templates/index.html`, `static/style.css`, `main.py`
