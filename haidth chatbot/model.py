# model.py
# This file handles all the AI/ML logic:
# Loading data → Cleaning text → Creating embeddings → FAISS indexing → Retrieval

import os
import re
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ─── Constants ────────────────────────────────────────────────────────────────
DATASET_PATH  = "dataset/hadith.csv"    # where our Hadith CSV lives
INDEX_PATH    = "hadith_faiss.index"    # where we save/load the FAISS index
MODEL_NAME    = "paraphrase-MiniLM-L6-v2"  # lightweight but powerful model
TOP_K         = 5                        # number of results to return

# ─── Step 1: Load & Combine Dataset ──────────────────────────────────────────
def load_hadiths(dataset_dir=None):
    """
    Reads all CSV files in the dataset folder and combines them into one
    DataFrame. This makes it easy to add more Hadith files later.
    """
    if dataset_dir is None:
        # Use the directory where this script is located
        dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    
    all_frames = []

    # Loop through every file in the dataset folder
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(dataset_dir, filename)
            try:
                df = pd.read_csv(filepath)
                all_frames.append(df)
                print(f"  [✓] Loaded '{filename}' → {len(df)} rows")
            except Exception as e:
                print(f"  [!] Could not read '{filename}': {e}")

    if not all_frames:
        raise FileNotFoundError("No CSV files found in the dataset folder.")

    # Combine all dataframes into one big dataframe
    combined = pd.concat(all_frames, ignore_index=True)
    return combined


# ─── Step 2: Preprocessing ───────────────────────────────────────────────────
def clean_text(text):
    """
    Cleans a single string:
      - Removes special characters (keeps letters, digits, spaces)
      - Converts to lowercase
      - Strips leading/trailing whitespace
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)   # keep only alphanumeric + spaces
    text = text.lower().strip()                     # lowercase and trim
    return text


def preprocess(df):
    """
    Prepares the DataFrame for embedding:
      1. Picks the column that contains Hadith text
      2. Drops empty/null rows
      3. Cleans each row with clean_text()
      4. Returns the cleaned Series and original texts
    """
    # Detect which column holds the Hadith text
    text_col = None
    for col in df.columns:
        if col.lower() in ("text", "hadith", "content", "body", "english"):
            text_col = col
            break
    if text_col is None:
        # Fall back to the first string column
        text_col = df.select_dtypes(include="object").columns[0]

    print(f"  [✓] Using column '{text_col}' as Hadith text")

    raw_texts  = df[text_col].dropna().astype(str)
    raw_texts  = raw_texts[raw_texts.str.strip() != ""].reset_index(drop=True)

    # Apply cleaning to every row
    clean_texts = raw_texts.apply(clean_text)
    # Drop rows that became empty after cleaning
    valid_mask  = clean_texts.str.strip() != ""
    clean_texts = clean_texts[valid_mask].reset_index(drop=True)
    raw_texts   = raw_texts[valid_mask].reset_index(drop=True)

    print(f"  [✓] {len(raw_texts)} valid Hadiths after preprocessing")
    return clean_texts, raw_texts


# ─── Step 3: Embedding ───────────────────────────────────────────────────────
def create_embeddings(texts, model):
    """
    Converts a list of cleaned Hadith texts into dense numeric vectors
    (embeddings). Each embedding captures the *meaning* of a sentence.

    paraphrase-MiniLM-L6-v2 outputs 384-dimensional vectors, which is
    small enough to be fast but rich enough for good semantic search.
    """
    print(f"  [✓] Encoding {len(texts)} Hadiths...")
    # encode() returns a numpy array of shape (N, 384)
    embeddings = model.encode(
        texts.tolist(),
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=32
    )
    return embeddings.astype("float32")  # FAISS needs float32


# ─── Step 4: FAISS Index ─────────────────────────────────────────────────────
def build_faiss_index(embeddings):
    """
    Builds a FAISS IndexFlatL2 index.

    IndexFlatL2 = brute-force exact search using Euclidean (L2) distance.
    Smaller L2 distance → vectors are more similar → Hadith is more relevant.

    How similarity search works:
      1. User query is turned into an embedding vector Q.
      2. FAISS computes L2 distance between Q and every stored embedding.
      3. The K nearest neighbours (smallest distances) are returned.
    """
    dim = embeddings.shape[1]       # 384 for MiniLM
    index = faiss.IndexFlatL2(dim)  # create the index
    index.add(embeddings)           # add all Hadith embeddings
    print(f"  [✓] FAISS index built with {index.ntotal} vectors (dim={dim})")
    return index


def save_index(index, path=INDEX_PATH):
    """Saves the FAISS index to disk so we don't have to rebuild on every start."""
    faiss.write_index(index, path)
    print(f"  [✓] Index saved → '{path}'")


def load_index(path=INDEX_PATH):
    """Loads a previously saved FAISS index from disk."""
    index = faiss.read_index(path)
    print(f"  [✓] Index loaded from '{path}' ({index.ntotal} vectors)")
    return index


# ─── Step 5: Retrieval Function ───────────────────────────────────────
def retrieve(query, model, index, raw_texts, top_k=TOP_K):
    """
    Full retrieval pipeline for one user query:
      1. Clean the query text
      2. Encode it into an embedding
      3. Search FAISS for the closest Hadith embeddings
      4. Return top_k results with their distances
    """
    # Clean the user's query the same way we cleaned training data
    cleaned_query = clean_text(query)
    if not cleaned_query:
        return []

    # Encode query → shape (1, 384)
    query_embedding = model.encode([cleaned_query], convert_to_numpy=True).astype("float32")

    # FAISS search: returns distances and indices of top_k neighbours
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
        if idx == -1:           # FAISS returns -1 when there aren't enough results
            continue
        results.append({
            "rank":     rank,
            "hadith":   raw_texts.iloc[idx],   # original (un-cleaned) text
            "distance": round(float(dist), 4),  # L2 distance (lower = more similar)
        })
    return results


# ─── Initialisation Helper ────────────────────────────────────────────────────
def initialise():
    """
    Called once at Flask startup:
      - Loads the sentence-transformer model
      - Either loads an existing FAISS index or builds a fresh one
      - Returns (model, index, raw_texts) ready for queries
    """
    print("\n=== Hadith QA Bot Initialisation ===")

    # Load the embedding model (downloads on first run, ~80 MB)
    print("[1/4] Loading SentenceTransformer model...")
    model = SentenceTransformer(MODEL_NAME)

    # Load and preprocess the dataset
    print("[2/4] Loading dataset...")
    df = load_hadiths()
    clean_texts, raw_texts = preprocess(df)

    # Build or load FAISS index
    if os.path.exists(INDEX_PATH):
        print("[3/4] FAISS index found on disk — loading...")
        index = load_index()
        # If dataset grew, rebuild the index
        if index.ntotal != len(raw_texts):
            print("  [!] Index size mismatch — rebuilding...")
            embeddings = create_embeddings(clean_texts, model)
            index = build_faiss_index(embeddings)
            save_index(index)
    else:
        print("[3/4] No saved index — building from scratch...")
        embeddings = create_embeddings(clean_texts, model)
        index = build_faiss_index(embeddings)
        save_index(index)

    print("[4/4] Ready!\n")
    return model, index, raw_texts
