from flask import Flask, request, jsonify
import json
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load discourse data
with open("data/discourse_posts.json", "r") as f:
    discourse_data = json.load(f)

texts = [post["post"] for post in discourse_data]
embeddings = model.encode(texts, convert_to_tensor=True)

@app.route("/api/", methods=["POST"])
def answer():
    data = request.get_json()
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Encode the question
    question_embedding = model.encode(question, convert_to_tensor=True)

    # Calculate similarity
    cos_scores = util.cos_sim(question_embedding, embeddings)[0]
    top_results = torch.topk(cos_scores, k=2)

    top_answers = []
    for idx in top_results.indices:
        post = discourse_data[int(idx)]
        top_answers.append({
            "url": post["url"],
            "text": post["post"][:120].replace("\n", " ") + "..."
        })

    response = {
        "answer": texts[int(top_results.indices[0])],
        "links": top_answers
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
