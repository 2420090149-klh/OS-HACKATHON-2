import os
import sys
from flask import Flask, render_template, request, jsonify

# Ensure the project root is first on sys.path so our local `src` package is used
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import analyzer

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    # Accept JSON or form-encoded POSTs
    data = request.get_json(silent=True) or request.form
    text = data.get("text", "")

    basic = analyzer.analyze_text(text)
    nlp = analyzer.analyze_text_nlp(text)
    findings = []
    try:
        findings = analyzer.summarize_findings(text)
    except Exception:
        findings = []

    # Normalize top_words for JSON-friendly output
    top_words = nlp.get("top_words", [])
    top_words_out = [
        {"word": w, "count": c} if isinstance(w, str) else {"word": w[0], "count": w[1]}
        for w, c in (top_words if isinstance(top_words, list) and all(isinstance(x, tuple) for x in top_words) else [(t["word"], t["count"]) for t in top_words] if isinstance(top_words, list) else [])
    ]

    # If analyzer returned already-normalized list (word,count tuples), convert
    if not top_words_out and isinstance(top_words, list) and all(isinstance(x, tuple) for x in top_words):
        top_words_out = [{"word": w, "count": c} for w, c in top_words]

    # If analyzer returned list of tuples already, override
    if isinstance(top_words, list) and top_words and isinstance(top_words[0], tuple):
        top_words_out = [{"word": w, "count": c} for w, c in top_words]

    # Build output
    result = {
        "basic": basic,
        "nlp": {
            "sentences": nlp.get("sentences"),
            "tokens": nlp.get("tokens"),
            "words": nlp.get("words"),
            "pos_tags": nlp.get("pos_tags", {}),
            "top_words": top_words_out,
        },
        "findings": findings,
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
