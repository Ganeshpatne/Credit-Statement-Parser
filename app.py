from flask import Flask, request, jsonify
import pdfplumber, io, re
from datetime import datetime

app = Flask(__name__)

def extract_fields(text):
    card = re.search(r'([0-9]{4})\b', text)
    due = re.search(r'(Due Date[:\s]*\d{1,2}\s\w+\s\d{4})', text)
    total = re.search(r'(Total Amount Due[:\s]*[\d,]+)', text)

    return {
        "card_last_4": card.group(1) if card else None,
        "due_date": due.group(1).split(":")[-1].strip() if due else None,
        "total_amount": total.group(1).split(":")[-1].strip() if total else None
    }

@app.route("/parse", methods=["POST"])
def parse_statement():
    if 'file' not in request.files:
        return jsonify({"error": "no file"}), 400

    f = request.files['file']
    with pdfplumber.open(io.BytesIO(f.read())) as pdf:
        text = ""
        for p in pdf.pages:
            text += p.extract_text() + "\n"

    data = extract_fields(text)
    data['raw_preview'] = text[:800]
    data['parsed_on'] = datetime.utcnow().isoformat()
    return jsonify(data)

# 👇 Add this new route here (just above the app.run line or at the end)
@app.route("/", methods=["GET"])
def home():
    return "Welcome to Credit Card Statement Parser API! Use the /parse endpoint to upload a PDF."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
