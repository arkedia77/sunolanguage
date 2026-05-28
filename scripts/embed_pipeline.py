#!/usr/bin/env python3
"""
embed_pipeline.py — Embed chunks and upsert to Qdrant.

Reads chunks.json (from chunk_builder.py), generates embeddings with
sentence-transformers, and upserts to Qdrant collection.

Usage:
    python scripts/embed_pipeline.py build              # full build
    python scripts/embed_pipeline.py build --batch=500  # custom batch size
    python scripts/embed_pipeline.py rebuild            # drop + rebuild
    python scripts/embed_pipeline.py stats              # collection stats
    python scripts/embed_pipeline.py test               # test query

Environment:
    QDRANT_HOST     default: 100.90.35.121
    QDRANT_PORT     default: 6333
    QDRANT_API_KEY  default: (none)
"""

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks.json"

COLLECTION_NAME = "sunolang_presets"
VECTOR_DIM = 384
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)


def get_qdrant_client():
    from qdrant_client import QdrantClient
    return QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        api_key=QDRANT_API_KEY,
    )


def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def ensure_collection(client):
    from qdrant_client.models import Distance, VectorParams
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        print(f"Created collection '{COLLECTION_NAME}' ({VECTOR_DIM}dim, Cosine)")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")


def load_chunks() -> list[dict]:
    with open(CHUNKS_FILE) as f:
        return json.load(f)


def cmd_build(batch_size: int = 500):
    client = get_qdrant_client()
    ensure_collection(client)
    model = get_embedding_model()
    chunks = load_chunks()

    from qdrant_client.models import PointStruct

    print(f"Embedding {len(chunks)} chunks with {EMBEDDING_MODEL}...")
    t0 = time.time()

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["embed_text"] for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False)

        points = []
        for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
            point_id = i + j
            payload = chunk["payload"].copy()
            payload["chunk_id"] = chunk["chunk_id"]
            payload["text"] = chunk["text"]
            payload["embed_text"] = chunk["embed_text"]
            points.append(PointStruct(
                id=point_id,
                vector=emb.tolist(),
                payload=payload,
            ))

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  Upserted {i + len(batch)}/{len(chunks)}")

    elapsed = time.time() - t0
    print(f"\nDone: {len(chunks)} chunks embedded and upserted in {elapsed:.1f}s")


def cmd_rebuild(batch_size: int = 500):
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted collection '{COLLECTION_NAME}'")
    cmd_build(batch_size=batch_size)


def cmd_stats():
    client = get_qdrant_client()
    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"  Points: {info.points_count}")
    print(f"  Status: {info.status}")
    if hasattr(info, "vectors_count") and info.vectors_count is not None:
        print(f"  Vectors: {info.vectors_count}")
    if hasattr(info, "disk_data_size") and info.disk_data_size is not None:
        print(f"  Disk: {info.disk_data_size} bytes")


def cmd_test():
    client = get_qdrant_client()
    model = get_embedding_model()

    test_query = "acoustic guitar fingerpicked"
    print(f"Test query: '{test_query}'")
    embedding = model.encode(test_query).tolist()

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        query_filter=Filter(must=[
            FieldCondition(key="slot", match=MatchValue(value="instrument")),
        ]),
        limit=5,
    )

    for i, hit in enumerate(response.points):
        print(f"\n  [{i+1}] score={hit.score:.4f}")
        print(f"      text: {hit.payload.get('text', '')[:100]}")
        print(f"      genre: {hit.payload.get('genre', '')}")
        print(f"      kit: {hit.payload.get('kit', '')}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "build":
        bs = 500
        for a in args:
            if a.startswith("--batch="):
                bs = int(a.split("=")[1])
        cmd_build(batch_size=bs)
    elif args[0] == "rebuild":
        bs = 500
        for a in args:
            if a.startswith("--batch="):
                bs = int(a.split("=")[1])
        cmd_rebuild(batch_size=bs)
    elif args[0] == "stats":
        cmd_stats()
    elif args[0] == "test":
        cmd_test()
    else:
        print(f"Usage: python {__file__} [build|rebuild|stats|test] [--batch=N]")
