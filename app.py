from flask import Flask, render_template, request, jsonify
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load FAQs
with open("data/faqs.json", "r") as file:
    faqs = json.load(file)


# Text preprocessing
def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


# Prepare FAQ questions
faq_questions = [
    preprocess(faq["question"])
    for faq in faqs
]

# Create TF-IDF vectors
vectorizer = TfidfVectorizer()
faq_vectors = vectorizer.fit_transform(faq_questions)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json["question"]

    # Preprocess user question
    user_question = preprocess(user_question)

    # Convert user question into TF-IDF vector
    user_vector = vectorizer.transform([user_question])

    # Calculate cosine similarity
    similarities = cosine_similarity(
        user_vector,
        faq_vectors
    )[0]

    # Find best matching FAQ
    best_index = similarities.argmax()
    best_score = similarities[best_index]

    # Confidence threshold
    if best_score >= 0.25:
        return jsonify({
            "answer": faqs[best_index]["answer"]
        })

    return jsonify({
        "answer": "Sorry, I don't know the answer to that question."
    })


if __name__ == "__main__":
    app.run(debug=True)