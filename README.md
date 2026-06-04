# Automated Digital Rights Management (DRM) and Asset Delivery API

Welcome to the Automated Digital Rights Management (DRM) and Asset Delivery API. This project provides a robust solution for managing digital assets, applying dynamic watermarks, and delivering them securely to buyers based on validated claims and payment notifications.

## Tech Stack

This project is built using modern and reliable technologies:

*   **FastAPI (Python 3.12)**: The core backend framework, providing high performance and rapid development of RESTful APIs.
*   **PyPDF**: Used for dynamic watermarking, allowing us to stamp buyer information securely onto digital assets before delivery.
*   **Tesseract**: Leveraged for Optical Character Recognition (OCR), providing fallback parsing capabilities for payment screenshot uploads.
*   **SQLite**: A localized database solution used for data storage and managing the delivery queuing system.
*   **Resend API**: Handles reliable and fast email delivery of the watermarked assets to the end-users.

## Features

*   **Product Management**: Manage digital products available for delivery.
*   **Claim Processing**: Users can submit claims for purchased assets with an associated reference number.
*   **Payment Webhooks**: The system listens for payment webhooks and validates them against submitted claims.
*   **Dynamic DRM**: Watermarks are applied dynamically with buyer details, ensuring asset traceability and security.
*   **OCR Fallback**: Provides a mechanism to parse transaction details directly from user-uploaded screenshots if automated payment matching fails.
*   **Asynchronous Delivery**: Assets are processed and dispatched asynchronously via an internal queue and background workers.
