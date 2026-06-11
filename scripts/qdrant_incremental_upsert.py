#!/usr/bin/env python3
"""
qdrant_incremental_upsert.py — Qdrant 증분 적재 (DROP+REBUILD 없이 신규 청크만)

전제(현 빌드 구조): point_id = 청크파일 내 순번(0..N-1). 코퍼스 병합은 항상
append라 신규 곡 청크는 청크파일 말미에 추가됨 → 컬렉션 K개 / 파일 N개(K<N)면
chunks[K:]를 id K..N-1로 upsert하면 전체 rebuild와 동일 결과.

안전 가드: 기존 구간 정렬 검증 — 위치 0/중간/K-1의 라이브 payload chunk_id가
파일과 일치해야 진행. 불일치=기존 구간이 변했다는 뜻 → 증분 불가, rebuild 안내.

사용법:
  # 코퍼스 병합 후 청크 재빌드(chunk_builder/lyrics_chunk_builder) 먼저, 그 다음:
  python3 scripts/qdrant_incremental_upsert.py --target presets            # dry-run
  python3 scripts/qdrant_incremental_upsert.py --target presets --execute
  python3 scripts/qdrant_incremental_upsert.py --target lyrics --execute
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TARGETS = {
    # target: (모듈명) — COLLECTION_NAME/CHUNKS_FILE/클라이언트/모델 재사용(단일 진실원)
    "presets": "embed_pipeline",
    "lyrics": "lyrics_embed_pipeline",
}


def load_target(name: str):
    import importlib
    mod = importlib.import_module(TARGETS[name])
    return mod


def verify_alignment(client, collection: str, chunks: list[dict], k: int) -> bool:
    """라이브 0..K-1 구간이 청크파일과 정렬돼 있는지 표본 검증."""
    if k == 0:
        return True
    probes = sorted({0, k // 2, k - 1})
    points = client.retrieve(collection_name=collection, ids=list(probes),
                             with_payload=True, with_vectors=False)
    live = {p.id: (p.payload or {}).get("chunk_id") for p in points}
    for p in probes:
        expected = chunks[p]["chunk_id"]
        got = live.get(p)
        if got != expected:
            print(f"❌ 정렬 불일치 @point {p}: live={got!r} file={expected!r}")
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Qdrant 증분 적재")
    ap.add_argument("--target", required=True, choices=list(TARGETS))
    ap.add_argument("--execute", action="store_true", help="실적재 (기본 dry-run)")
    ap.add_argument("--batch-size", type=int, default=500)
    args = ap.parse_args()

    mod = load_target(args.target)
    collection = mod.COLLECTION_NAME
    chunks = mod.load_chunks()
    client = mod.get_qdrant_client()

    info = client.get_collection(collection)
    k = info.points_count
    n = len(chunks)
    print(f"[incr] {collection}: live {k} points / 청크파일 {n} chunks")

    if n == k:
        if verify_alignment(client, collection, chunks, k):
            print("[incr] 추가분 없음 — 이미 동기화 상태 ✅")
        sys.exit(0)
    if n < k:
        print("❌ 청크파일이 라이브보다 작음 — 청크 재빌드 누락이거나 코퍼스 축소. "
              "증분 불가, 의도된 축소라면 rebuild 사용.")
        sys.exit(1)

    if not verify_alignment(client, collection, chunks, k):
        print("❌ 기존 구간 변경 감지 — 증분 불가. "
              f"`{TARGETS[args.target]}.py rebuild` 필요 (Leo 승인 후).")
        sys.exit(1)

    new_chunks = chunks[k:]
    print(f"[incr] 신규 {len(new_chunks)} chunks → point_id {k}..{n - 1}")
    sample_ids = [c["chunk_id"] for c in new_chunks[:3]]
    print(f"[incr] 선두 표본: {sample_ids}")

    if not args.execute:
        print("[incr] dry-run — 적재 없음. 적재 시 --execute")
        return

    from qdrant_client.models import PointStruct
    model = mod.get_embedding_model()
    t0 = time.time()
    done = 0
    for i in range(0, len(new_chunks), args.batch_size):
        batch = new_chunks[i:i + args.batch_size]
        embeddings = model.encode([c["embed_text"] for c in batch],
                                  show_progress_bar=False)
        points = []
        for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
            payload = chunk["payload"].copy()
            payload["chunk_id"] = chunk["chunk_id"]
            payload["text"] = chunk["text"]
            payload["embed_text"] = chunk["embed_text"]
            points.append(PointStruct(id=k + i + j, vector=emb.tolist(),
                                      payload=payload))
        client.upsert(collection_name=collection, points=points)
        done += len(batch)
        print(f"  upserted {done}/{len(new_chunks)}")

    info = client.get_collection(collection)
    print(f"[incr] 완료 {time.time() - t0:.1f}s — live {info.points_count} points "
          f"(기대 {n}) {'✅' if info.points_count == n else '❌ 불일치!'}")
    if info.points_count != n:
        sys.exit(1)


if __name__ == "__main__":
    main()
