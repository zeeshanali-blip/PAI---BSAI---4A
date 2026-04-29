
from flask import Flask, render_template, request
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = Flask(__name__)

df = pd.read_csv("dataset.csv")

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

embeddings = model.encode(df["question"].tolist())

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype("float32"))

def search(query):
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb).astype("float32"), 3)
    results = []
    for i in I[0]:
        results.append(df.iloc[i]["answer"])
    return results

@app.route("/", methods=["GET", "POST"])
def home():
    answers = []
    if request.method == "POST":
        q = request.form["question"]
        answers = search(q)
    return render_template("index.html", answers=answers)

if __name__ == "__main__":
    app.run(debug=True)
