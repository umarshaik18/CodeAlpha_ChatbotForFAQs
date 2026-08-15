from flask import Flask, render_template, request, jsonify
import json
import re
from difflib import SequenceMatcher

app = Flask(__name__)

# Load FAQs
with open("data/faqs.json", "r") as file:
    faqs = json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json["question"].lower()

    # Remove punctuation
    user_question = re.sub(r"[^\w\s]", "", user_question)

    best_match = None
    best_score = 0

    for faq in faqs:
        faq_question = faq["question"].lower()
        faq_question = re.sub(r"[^\w\s]", "", faq_question)

        # Similarity score
        similarity = SequenceMatcher(
            None,
            user_question,
            faq_question
        ).ratio()

        # Compare common words
        user_words = set(user_question.split())
        faq_words = set(faq_question.split())

        common_words = user_words.intersection(faq_words)

        if len(user_words) > 0:
            word_score = len(common_words) / len(user_words)
        else:
            word_score = 0

        # Combined score
        score = (similarity * 0.5) + (word_score * 0.5)

        if score > best_score:
            best_score = score
            best_match = faq

    # Accept the best match if confidence is good enough
    if best_match and best_score >= 0.35:
        return jsonify({
            "answer": best_match["answer"]
        })

    return jsonify({
        "answer": "Sorry, I don't know the answer to that question."
    })


if __name__=="__main__":
    app.run(debug=True)