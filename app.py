from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pdfplumber
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

def extract_fields(text):
    """Extract key fields from credit card statement text"""
    
    # Card Last 4 Digits
    card_last_4 = None
    card_patterns = [
        r'Card\s+(?:Number|ending|ending in)[:\s]*\*+(\d{4})',
        r'Account\s+ending\s+in[:\s]*(\d{4})',
        r'xxxx\s*xxxx\s*xxxx\s*(\d{4})',
        r'\*{4}\s*(\d{4})'
    ]
    for pattern in card_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            card_last_4 = match.group(1)
            break
    
    # Card Type
    card_type = None
    card_type_patterns = [
        (r'\b(Visa)\b', 'Visa'),
        (r'\b(MasterCard|Master Card)\b', 'MasterCard'),
        (r'\b(American Express|Amex)\b', 'American Express'),
        (r'\b(Discover)\b', 'Discover'),
        (r'\b(RuPay)\b', 'RuPay')
    ]
    for pattern, name in card_type_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            card_type = name
            break
    
    # Billing Cycle
    billing_cycle = None
    billing_patterns = [
        r'Billing\s+(?:Cycle|Period)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:to|-)\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Statement\s+Period[:\s]*(\d{1,2}\s+\w+\s+\d{4}\s*(?:to|-)\s*\d{1,2}\s+\w+\s+\d{4})',
        r'Statement\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in billing_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            billing_cycle = match.group(1)
            break
    
    # Payment Due Date
    due_date = None
    due_patterns = [
        r'(?:Payment\s+)?Due\s+Date[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
        r'(?:Payment\s+)?Due\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Pay\s+by[:\s]*(\d{1,2}\s+\w+\s+\d{4})'
    ]
    for pattern in due_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            due_date = match.group(1)
            break
    
    # Total Amount Due
    total_amount = None
    amount_patterns = [
        r'Total\s+Amount\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        r'Amount\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        r'Total\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        r'Minimum\s+Amount\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            total_amount = match.group(1)
            break
    
    # Minimum Payment
    minimum_payment = None
    min_patterns = [
        r'Minimum\s+(?:Payment|Amount)\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
        r'Minimum\s+Due[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)'
    ]
    for pattern in min_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            minimum_payment = match.group(1)
            break
    
    return {
        "card_last_4": card_last_4,
        "card_type": card_type,
        "billing_cycle": billing_cycle,
        "due_date": due_date,
        "total_amount": total_amount,
        "minimum_payment": minimum_payment
    }

@app.route("/parse", methods=["POST"])
def parse_statement():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Extract text from PDF
        text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500
        
        # Check if text was extracted
        if not text.strip():
            return jsonify({"error": "No text could be extracted from the PDF"}), 400
        
        # Extract fields
        data = extract_fields(text)
        data['raw_preview'] = text[:1000]  # First 1000 chars
        data['parsed_on'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        data['success'] = True
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
