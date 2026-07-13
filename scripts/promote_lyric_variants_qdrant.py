#!/usr/bin/env python3
"""
promote_lyric_variants_qdrant.py — lyric_variations(PG accepted) → Qdrant 승격.

별도 계보(본코퍼스 불혼입) 가사변형 코퍼스를 Qdrant 컬렉션
`sunolang_lyric_variants`로 임베드·업서트. lyrics_retriever가 옵션 참조하여
풀고갈(exclude-history 고갈) 완화의 패러프레이즈 다양성 소스로 사용.

소스   : PostgreSQL leofamily_music.lyric_variations WHERE gate_status='accepted'
타깃   : Qdrant sunolang_lyric_variants (384dim, Cosine)
모델   : paraphrase-multilingual-MiniLM-L12-v2 (sunolang_lyrics와 동일 — 형제 공간)
포인트 : id=var_id (PG PK, idempotent 재실행)

사용:
    python3 scripts/promote_lyric_variants_qdrant.py build     # 없으면 생성 후 업서트
    python3 scripts/promote_lyric_variants_qdrant.py rebuild   # 컬렉션 삭제 후 재빌드
    python3 scripts/promote_lyric_variants_qdrant.py stats
    python3 scripts/promote_lyric_variants_qdrant.py test

환경:
    QDRANT_HOST  default 100.90.35.121   QDRANT_PORT default 6333   QDRANT_API_KEY
"""
import os
import sys
import time

COLLECTION_NAME = "sunolang_lyric_variants"
VECTOR_DIM = 384
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

QDRANT_HOST = os.environ.get("QDRANT_HOST", "100.90.35.121")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", None)


def get_qdrant_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY,
                        check_compatibility=False)


def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def _pg_conn():
    # load_lyric_variations와 동일 설정 소스 (단일 기재)
    import scripts.load_lyric_variations as L  # noqa
    return L.conn()


def load_accepted() -> list[dict]:
    """accepted 변형 전건 로드 (변형문=임베드 대상)."""
    conn = _pg_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT var_id, original_text, variant_text, source_song_id, source_chunk_id,
               variant_rank, lang, section_tag, cosine_to_src
        FROM lyric_variations
        WHERE gate_status='accepted'
        ORDER BY var_id
    """)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def ensure_collection(client):
    from qdrant_client.models import Distance, VectorParams
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        print(f"Created collection '{COLLECTION_NAME}' ({VECTOR_DIM}dim, Cosine)")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")


def cmd_build(batch_size: int = 500):
    from qdrant_client.models import PointStruct
    client = get_qdrant_client()
    ensure_collection(client)
    rows = load_accepted()
    print(f"Loaded {len(rows)} accepted variations from PG")
    model = get_embedding_model()
    t0 = time.time()
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        texts = [r["variant_text"] for r in batch]
        embeddings = model.encode(texts, show_progress_bar=False)
        points = []
        for r, emb in zip(batch, embeddings):
            points.append(PointStruct(
                id=int(r["var_id"]),
                vector=emb.tolist(),
                payload={
                    "source_type": "variations",
                    "variant_text": r["variant_text"],
                    "original_text": r["original_text"],
                    "source_song_id": r["source_song_id"],
                    "source_chunk_id": r["source_chunk_id"],
                    "variant_rank": r["variant_rank"],
                    "lang": r["lang"],
                    "section_tag": r["section_tag"],
                    "cosine_to_src": r["cosine_to_src"],
                },
            ))
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  Upserted {i + len(batch)}/{len(rows)}")
    print(f"\nDone: {len(rows)} variations embedded in {time.time() - t0:.1f}s")
    cmd_stats()


def cmd_rebuild(batch_size: int = 500):
    client = get_qdrant_client()
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in names:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted collection '{COLLECTION_NAME}'")
    cmd_build(batch_size=batch_size)


def cmd_stats():
    client = get_qdrant_client()
    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"  Points: {info.points_count}")
    print(f"  Status: {info.status}")


def cmd_test():
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client = get_qdrant_client()
    model = get_embedding_model()
    queries = [
        ("밤하늘 아래 혼자 걷는 길", None),
        ("이별의 아쉬움", "verse"),
        ("사랑한다 말하고 싶어", "chorus"),
    ]
    for q, section in queries:
        print(f"\nQuery: '{q}'" + (f" [section={section}]" if section else ""))
        emb = model.encode(q).tolist()
        cond = [FieldCondition(key="section_tag", match=MatchValue(value=section))] if section else []
        resp = client.query_points(
            collection_name=COLLECTION_NAME, query=emb,
            query_filter=Filter(must=cond) if cond else None, limit=3,
        )
        for p in resp.points:
            pl = p.payload
            print(f"  {p.score:.3f} [{pl.get('section_tag')}] {pl.get('variant_text','')[:42]}"
                  f"  (src_song={pl.get('source_song_id')})")


CMDS = {"build": cmd_build, "rebuild": cmd_rebuild, "stats": cmd_stats, "test": cmd_test}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd not in CMDS:
        print(f"unknown command: {cmd}\nusage: {', '.join(CMDS)}")
        sys.exit(1)
    CMDS[cmd]()
