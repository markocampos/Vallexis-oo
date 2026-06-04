# CONTRIBUTING

First off, thank you for considering contributing to the Automated DRM and Asset Delivery API! It's people like you that make this tool better for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible.

*   **Use a clear and descriptive title** for the issue to identify the problem.
*   **Describe the exact steps which reproduce the problem** in as many details as possible.
*   **Provide specific examples to demonstrate the steps.**
*   **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
*   **Explain which behavior you expected to see instead and why.**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When you are creating an enhancement suggestion, please include as many details as possible.

*   **Use a clear and descriptive title** for the issue to identify the suggestion.
*   **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
*   **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
*   **Explain why this enhancement would be useful** to most users.

### Pull Requests

*   Fill in the required template.
*   Do not include issue numbers in the PR title.
*   Follow the Python styleguide (`ruff` is used for linting).
*   Document new code based on the Docstring Conventions.
*   End all files with a newline.

## Development Setup

To set up the project locally for development:

1.  Clone the repository.
2.  Install dependencies using `pip install -r requirements.txt`.
3.  Run tests using `python -m pytest`.
4.  Run the application using the provided `start.sh` script or via `uvicorn main:app --reload`.
