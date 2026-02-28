"""
RAG Handler — Pure Python (numpy + sentence-transformers)
Handles both static knowledge docs AND dynamically uploaded HR PDFs.
"""
import os, sys, pickle
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import EMBEDDING_MODEL, RAG_TOP_K, RAG_INDEX_PATH, HR_PDF_DIR

_embedder = None
_docs = []           # [{text, metadata, source}]
_embeddings = None
_ready = False
INDEX_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", RAG_INDEX_PATH))

def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

def _embed(texts):
    return np.array(_get_embedder().encode(texts, show_progress_bar=False), dtype=np.float32)

def _cosine_sim(q, matrix):
    q = q / (np.linalg.norm(q) + 1e-10)
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return m @ q

def _save():
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"docs": _docs, "embeddings": _embeddings}, f)

def _load():
    global _docs, _embeddings
    if not os.path.exists(INDEX_PATH):
        return False
    try:
        with open(INDEX_PATH, "rb") as f:
            d = pickle.load(f)
        _docs = d["docs"]; _embeddings = d["embeddings"]
        return len(_docs) > 0
    except:
        return False

def _seed_base_docs():
    global _docs, _embeddings
    from data.docs.knowledge_base import KNOWLEDGE_DOCS
    texts = [d["text"] for d in KNOWLEDGE_DOCS]
    metas = [d["metadata"] for d in KNOWLEDGE_DOCS]
    print(f"RAG: Indexing {len(texts)} base knowledge docs...")
    vecs = _embed(texts)
    _docs = [{"text": t, "metadata": m} for t, m in zip(texts, metas)]
    _embeddings = vecs
    _save()
    print("RAG: Base docs indexed ✅")

def init():
    global _ready
    if _ready: return True
    try:
        if _load():
            _ready = True
            print(f"RAG: Loaded {len(_docs)} docs from cache")
        else:
            _seed_base_docs()
            _ready = True
        return True
    except Exception as e:
        print(f"RAG init warning: {e}")
        _ready = False
        return False

def add_pdf(file_bytes: bytes, filename: str, source_label: str = "HR Policy") -> int:
    """Parse a PDF and add its chunks to the RAG index."""
    global _docs, _embeddings, _ready
    init()
    try:
        import io
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            full_text = "\n".join(p.extract_text() or "" for p in reader.pages)
        except ImportError:
            # Fallback: treat as text
            full_text = file_bytes.decode("utf-8", errors="ignore")

        # Chunk into ~500 char overlapping segments
        chunks = _chunk_text(full_text, chunk_size=600, overlap=100)
        if not chunks:
            return 0

        new_docs = [{"text": c, "metadata": {"type": "hr_policy", "source": filename, "label": source_label}}
                    for c in chunks]
        new_vecs = _embed([d["text"] for d in new_docs])

        _docs.extend(new_docs)
        _embeddings = np.vstack([_embeddings, new_vecs]) if _embeddings is not None else new_vecs
        _save()
        print(f"RAG: Added {len(new_docs)} chunks from {filename}")
        return len(new_docs)
    except Exception as e:
        print(f"PDF add error: {e}")
        return 0

def _chunk_text(text: str, chunk_size=600, overlap=100) -> list:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        i += chunk_size - overlap
    return chunks

def retrieve(query: str, top_k: int = RAG_TOP_K, source_filter: str = None) -> list:
    if not init() or _embeddings is None or not _docs:
        return []
    try:
        q_vec = _embed([query])[0]
        sims  = _cosine_sim(q_vec, _embeddings)
        k = min(top_k, len(_docs))
        top_idx = np.argsort(sims)[::-1][:k*2]
        results = []
        for idx in top_idx:
            sim = float(sims[idx])
            dist = 1.0 - sim
            if dist >= 0.85: continue
            doc = _docs[idx]
            if source_filter and doc["metadata"].get("type") != source_filter:
                continue
            results.append({"text": doc["text"], "metadata": doc["metadata"], "distance": round(dist, 3)})
            if len(results) >= top_k:
                break
        return results
    except Exception as e:
        print(f"RAG retrieve error: {e}")
        return []

def format_context(docs: list) -> str:
    if not docs: return ""
    parts = ["=== CONTEXT FROM KNOWLEDGE BASE ==="]
    for i, d in enumerate(docs, 1):
        m = d["metadata"]
        src = m.get("source") or m.get("table") or m.get("type","")
        parts.append(f"\n[{i}] Source: {src}\n{d['text'].strip()}")
    parts.append("=== END ===")
    return "\n".join(parts)

def get_indexed_sources() -> list:
    init()
    sources = {}
    for d in _docs:
        s = d["metadata"].get("source", "internal")
        sources[s] = sources.get(s, 0) + 1
    return [{"source": k, "chunks": v} for k, v in sources.items()]

def delete_source(filename: str) -> bool:
    global _docs, _embeddings
    before = len(_docs)
    keep_idx = [i for i, d in enumerate(_docs) if d["metadata"].get("source") != filename]
    _docs = [_docs[i] for i in keep_idx]
    _embeddings = _embeddings[keep_idx] if _embeddings is not None and len(keep_idx) > 0 else None
    _save()
    return len(_docs) < before
