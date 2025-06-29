"""
Vector Indexer (with local embedding support)
- Uses MiniLM or compatible model for embedding/query.
"""

import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

VECTOR_INDEX_PATH = Path("./knowledge/system_reference/vector_store/gaia_rescue_index/index_store.json")
EMBED_MODEL_PATH = "/models/all-MiniLM-L6-v2"

def load_vector_index():
    if VECTOR_INDEX_PATH.exists():
        with open(VECTOR_INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"docs": [], "embeddings": []}

def save_vector_index(index):
    with open(VECTOR_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f)

def embed_gaia_reference():
    model = SentenceTransformer(EMBED_MODEL_PATH)
    docs = []
    embeddings = []
    # Walk core docs (update as needed)
    for doc_file in Path("./knowledge/system_reference/GAIA_Function_Map").glob("*.*"):
        with open(doc_file, "r", encoding="utf-8") as f:
            text = f.read()
            docs.append({"filename": doc_file.name, "text": text})
            embeddings.append(model.encode(text))
    index = {"docs": docs, "embeddings": [e.tolist() for e in embeddings]}
    save_vector_index(index)
    print("✅ GAIA core reference embedded.")
    return True

def vector_query(query):
    model = SentenceTransformer(EMBED_MODEL_PATH)
    index = load_vector_index()
    if not index["docs"]:
        return "No knowledge indexed."
    query_emb = model.encode(query)
    # Compute cosine similarity (using util.pytorch_cos_sim if available)
    import numpy as np
    similarities = [float(util.pytorch_cos_sim(query_emb, np.array(e))[0][0]) for e in index["embeddings"]]
    top_idx = int(np.argmax(similarities))
    doc = index["docs"][top_idx]
    return f"Top match: {doc['filename']}\n\n{doc['text'][:500]}..."
