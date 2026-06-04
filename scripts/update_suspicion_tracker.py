#!/usr/bin/env python3
"""suspicion_tracker.json의 suno_seen_in_reanalysis를 lexical_index 기준으로 자동 갱신.

사용:
    python3 scripts/update_suspicion_tracker.py          # 기본 실행
    python3 scripts/update_suspicion_tracker.py --dry-run # 변경 미적용, 결과만 표시

로직:
  tracker의 각 word를 lexical_index.sqlite words 테이블에서 조회.
  freq_total > 0이면 suno_seen_in_reanalysis = True로 갱신.
"""

from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "docs" / "reviews" / "suspicion_tracker.json"
LEXICAL_DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(TRACKER.read_text())
    conn = sqlite3.connect(str(LEXICAL_DB))

    updated = 0
    already_true = 0
    still_zero = 0

    for entry in data["entries"]:
        if entry["suno_seen_in_reanalysis"]:
            already_true += 1
            continue

        word = entry["word"]
        row = conn.execute(
            "SELECT freq_total FROM words WHERE word = ?", (word.lower(),)
        ).fetchone()

        if row and row[0] > 0:
            entry["suno_seen_in_reanalysis"] = True
            entry["notes"] = f"auto: freq_total={row[0]}"
            updated += 1
            print(f"  ✓ {word} → freq_total={row[0]}")
        else:
            still_zero += 1

    conn.close()

    print(f"\nSummary: {updated} updated, {already_true} already true, {still_zero} still zero")

    if not args.dry_run and updated > 0:
        TRACKER.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"Saved to {TRACKER}")
    elif args.dry_run:
        print("(dry-run — not saved)")


if __name__ == "__main__":
    main()
