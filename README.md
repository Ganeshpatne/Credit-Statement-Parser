# Credit Card Statement Parser

A Flask-based web application that extracts and displays key financial information from credit card statement PDFs.  
It uses `pdfplumber` for text extraction and regular expressions to identify important details such as card number, billing cycle, payment due date, and total amount.

---

## Features

- Upload PDF credit card statements directly through the web interface.
- Automatically extracts five key data points:
  - Card Last 4 Digits
  - Card Type or Variant
  - Billing Cycle or Statement Period
  - Payment Due Date
  - Total Amount Due
- Displays extracted data in a formatted HTML table.
- Provides a collapsible raw preview of the PDF text.
- Includes a timestamp indicating when the statement was parsed.

---

## Technology Stack

- Backend: Python (Flask)
- Frontend: HTML, CSS, JavaScript (Fetch API)
- PDF Processing: pdfplumber
- Regex Matching: re
- Date Handling: datetime

---

## Project Structure

