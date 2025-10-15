from flask import Flask, request, jsonify
import pdfplumber
import re
from datetime import datetime

app = Flask(__name__)

def extract_fields(text):
    """
    Extract 5 key data points from PDF text:
    1. Card Last 4 Digits
    2. Card Type / Variant
    3. Billing Cycle / Statement Period
    4. Payment Due Date
    5. Total Amount
    """
    # Card Last 4 Digits
    card_last_4 = None
    m = re.search(r'\b\d{4}\b', text)
    if m:
        card_last_4 = m.group()

    # Card Type / Variant (Example: Platinum, Rewards, etc.)
    card_type = None
    type_match = re.search(r'(Platinum|Classic|Rewards|Gold|Silver)', text, re.IGNORECASE)
    if type_match:
        card_type = type_match.group()

    # Billing Cycle / Statement Period (Example: 01 Sep 2025 - 30 Sep 2025)
    billing_cycle = None
    cycle_match = re.search(r'(\d{2} \w+ \d{4})\s*-\s*(\d{2} \w+ \d{4})', text)
    if cycle_match:
        billing_cycle = f"{cycle_match.group(1)} - {cycle_match.group(2)}"

    # Payment Due Date
    due_date = None
    due_match = re.search(r'Due Date[:\s]*(\d{1,2} \w+ \d{4})', text)
    if due_match:
        due_date = due_match.group(1)

    # Total Amount
    total_amount = None
    total_match = re.search(r'Total Amount Due[:\s]*([\d,]+)', text)
    if total_match:
        total_amount = total_match.group(1)

    return {
        "card_last_4": card_last_4,
        "card_type": card_type,
        "billing_cycle": billing_cycle,
        "due_date": due_date,
        "total_amount": total_amount
    }

@app.route("/parse", methods=["POST"])
def parse_statement():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files['file']
    with pdfplumber.open(f) as pdf:
        text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    data = extract_fields(text)
    data['raw_preview'] = text[:800]  # first 800 chars of PDF text
    data['parsed_on'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
