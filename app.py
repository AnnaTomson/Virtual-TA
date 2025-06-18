from flask import Flask, request, jsonify
import base64
from sentence_transformers import SentenceTransformer, util
import json

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load discourse data
with open("data/discourse_posts.json", "r") as f:
    discourse_data = json.load(f)
texts = [p["post"] for p in discourse_data]
embeddings = model.encode(texts, convert_to_tensor=True)

@app.route("/api/", methods=["POST"])
def answer_question():
    req = request.json
    query = req.get("question", "")
    query_embedding = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, embeddings)[0]
    top_k = scores.argsort(descending=True)[:2]

    response = {
        "answer": texts[int(top_k[0])],
        "links": [
            {"url": discourse_data[int(top_k[i])]["url"], "text": texts[int(top_k[i])][:80]}
            for i in range(2)
        ]
    }
    return jsonify(response)
