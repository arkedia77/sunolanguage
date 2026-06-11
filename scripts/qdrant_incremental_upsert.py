#!/usr/bin/env python3
"""
qdrant_incremental_upsert.py — Qdrant 증분 적재 (DROP+REBUILD 없이 신규 청크만)

방식: chunk_id 집합 diff (순서 무관 — v1의 '파일 순번=point_id' 전제는
chunk_builder의 [SP 전곡][bracket 전곡] 2단 구조 때문에 신규 곡이 중간 삽입되어
폐기. 2026-06-11 Batch C 실전에서 확인).

  1. 라이브 전체 scroll → {chunk_id: point_id} 인덱스
  2. 파일 청크 중 라이브에 없는 chunk_id = 신규 → max(point_id)+1 부터 채번 upsert
  3. 라이브에만 있고 파일에 없는 chunk_id 발견 시 중단 (코퍼스 축소/드리프트
     의심 — 의도된 축소라면 rebuild 사용)

전제: chunk_id는 파일 내 고유 + 결정적(`{source}_{slot}_{song_id}_{seq}`).
검색은 point_id에 의존하지 않으므로 채번 순서는 무관.

사용법:
  # 코퍼스 병합 후 청크 재빌드(chunk_builder/lyrics_chunk_builder) 먼저, 그 다음:
  python3 scripts/qdrant_incremental_upsert.py --target presets            # dry-run
  python3 scripts/qdrant_incremental_upsert.py --target presets --execute
  python3 scripts/qdrant_incremental_upsert.py --target lyrics --execute
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TARGETS = {
    # target: 모듈명 — COLLECTION_NAME/CHUNKS_FILE/클라이언트/모델 재사용(단일 진실원)
    "presets": "embed_pipeline",
    "lyrics": "lyrics_embed_pipeline",
}


def load_target(name: str):
    import importlib
    return importlib.import_module(TARGETS[name])


def scroll_live_index(client, collection: str) -> dict:
    """라이브 전체 {chunk_id: point_id}."""
    index = {}
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection, limit=1000, offset=offset,
            with_payload=["chunk_id"], with_vectors=False)
        for p in points:
            cid = (p.payload or {}).get("chunk_id")
            if cid is not None:
                index[cid] = p.id
        if offset is None:
            break
    return index


def main():
    ap = argparse.ArgumentParser(description="Qdrant 증분 적재 (chunk_id diff)")
    ap.add_argument("--target", required=True, choices=list(TARGETS))
    ap.add_argument("--execute", action="store_true", help="실적재 (기본 dry-run)")
    ap.add_argument("--batch-size", type=int, default=500)
    args = ap.parse_args()

    mod = load_target(args.target)
    collection = mod.COLLECTION_NAME
    chunks = mod.load_chunks()
    client = mod.get_qdrant_client()

    file_ids = [c["chunk_id"] for c in chunks]
    if len(file_ids) != len(set(file_ids)):
        print("❌ 청크파일 내 chunk_id 중복 — 빌더 점검 필요")
        sys.exit(1)

    print(f"[incr] {collection}: 라이브 인덱스 scroll 중...")
    live = scroll_live_index(client, collection)
    print(f"[incr] live {len(live)} points / 청크파일 {len(chunks)} chunks")

    file_set = set(file_ids)
    live_only = set(live) - file_set
    if live_only:
        print(f"❌ 라이브에만 존재하는 chunk_id {len(live_only)}개 "
              f"(표본 {sorted(live_only)[:3]}) — 코퍼스 축소/드리프트 의심. "
              "증분 불가, 의도된 변경이면 rebuild 사용.")
        sys.exit(1)

    new_chunks = [c for c in chunks if c["chunk_id"] not in live]
    if not new_chunks:
        print("[incr] 추가분 없음 — 이미 동기화 상태 ✅")
        return

    next_id = (max(live.values()) + 1) if live else 0
    print(f"[incr] 신규 {len(new_chunks)} chunks → point_id {next_id}.."
          f"{next_id + len(new_chunks) - 1}")
    print(f"[incr] 선두 표본: {[c['chunk_id'] for c in new_chunks[:3]]}")

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
            points.append(PointStruct(id=next_id + i + j, vector=emb.tolist(),
                                      payload=payload))
        client.upsert(collection_name=collection, points=points)
        done += len(batch)
        print(f"  upserted {done}/{len(new_chunks)}")

    expected = len(chunks)
    info = client.get_collection(collection)
    ok = info.points_count == expected
    print(f"[incr] 완료 {time.time() - t0:.1f}s — live {info.points_count} points "
          f"(기대 {expected}) {'✅' if ok else '❌ 불일치!'}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
