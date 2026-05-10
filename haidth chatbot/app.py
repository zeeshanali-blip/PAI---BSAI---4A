# app.py
# Flask web application entry point.
# Starts the server, loads the AI model once, and handles user queries.

from flask import Flask, render_template, request
from model import initialise, retrieve

# ─── Create Flask App ─────────────────────────────────────────────────────────
app = Flask(__name__)

# Load model + FAISS index at startup (runs once, not on every request)
print("Starting Hadith QA Bot...")
model, index, raw_texts = initialise()


# ─── Main Route ───────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def home():
    """
    GET  /  → show the search form (empty)
    POST /  → run retrieval and show results
    """
    results = []
    query   = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if query:
            # Call our retrieval pipeline from model.py
            results = retrieve(query, model, index, raw_texts)

    # Render the HTML template with results
    return render_template("index.html", query=query, results=results)


# ─── Run Server ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # debug=False for production; set to True during development
    app.run(debug=False, host="0.0.0.0", port=5000)