#!/usr/bin/env python3
"""
lyrics_sanitizer.py — 가사 노이즈 정리 (코퍼스 인제스트 게이트, Leo 지시 2026-05-29)

Suno 재분석 회신 가사의 노이즈를 인제스트 전에 정규화한다.
corpus_quality_gate.py(시맨틱 게이트)와 상보 — 이쪽은 문자/표기 수준.

처리(자동 수정):
  - 유니코드 NFC 정규화 (자모 분해형 → 완성형)
  - BOM/zero-width/제어문자 제거 (\\n, \\t 보존)
  - 전각 ASCII·전각 공백 → 반각
  - 스마트쿼트/대시/말줄임 → 표준형 (' " - …)
  - 행 끝 공백 제거, 행 내 다중 공백 압축, 3+연속 빈 줄 → 1 빈 줄

리포트(자동 수정 안 함 — 검수 대상):
  - 외국어 혼입: 한국어 가사 행 안의 한중일 외 이질 스크립트(키릴/아랍/태국 등)
  - 비표준 기호 잔존 (음표/이모지 등)

사용법:
  # 라이브러리:  clean, issues = sanitize_text(text)
  # CLI 단건:
  python3 scripts/lyrics_sanitizer.py --text "가사..."
  # CLI 파일(JSON 배열 내 가사 필드 일괄):
  python3 scripts/lyrics_sanitizer.py file.json --field lyrics [--out out.json]
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# 보존할 제어문자
_KEEP_CTRL = {"\n", "\t"}

# 스마트 문자 → 표준형
_CHAR_MAP = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "―": "-",
    "…": "…",  # 말줄임은 단일 코드포인트로 통일
    " ": " ",  # nbsp
    "　": " ",  # 전각 공백
}

_ZERO_WIDTH = re.compile(r"[​‌‍⁠﻿]")

# 허용 스크립트: 한글/한자/가나(일본곡 가사 존재)/라틴/숫자/일반 문장부호
_FOREIGN_SCRIPT = re.compile(
    r"[Ѐ-ӿ؀-ۿ฀-๿֐-׿"   # 키릴/아랍/태국/히브리
    r"ऀ-ॿἀ-῿]"                              # 데바나가리/그리스확장
)

# 이모지·기호 블록 (리포트만)
_SYMBOL = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿]")


def _fold_fullwidth(ch: str) -> str:
    """전각 ASCII(！-～) → 반각."""
    o = ord(ch)
    if 0xFF01 <= o <= 0xFF5E:
        return chr(o - 0xFEE0)
    return ch


def sanitize_text(text: str) -> tuple[str, list[dict]]:
    """노이즈 정리된 텍스트와 issue 리스트 반환. 멱등."""
    issues = []
    if not text:
        return text, issues

    original = text

    # 1) NFC 정규화
    text = unicodedata.normalize("NFC", text)

    # 2) zero-width/BOM 제거
    text = _ZERO_WIDTH.sub("", text)

    # 3) 문자 매핑(스마트쿼트 등) + 전각 ASCII 반각화 + 제어문자 제거
    out_chars = []
    for ch in text:
        if ch in _CHAR_MAP:
            out_chars.append(_CHAR_MAP[ch])
            continue
        ch = _fold_fullwidth(ch)
        if unicodedata.category(ch) in ("Cc", "Cf") and ch not in _KEEP_CTRL:
            continue
        out_chars.append(ch)
    text = "".join(out_chars)

    # 4) 공백 정리: 행끝 공백 / 행내 다중 공백 / 탭→공백
    lines = []
    for line in text.split("\n"):
        line = line.replace("\t", " ")
        line = re.sub(r" {2,}", " ", line).rstrip()
        lines.append(line)
    text = "\n".join(lines)

    # 5) 3+연속 빈 줄 → 1 빈 줄, 선두/말미 빈 줄 제거
    text = re.sub(r"\n{3,}", "\n\n", text).strip("\n")

    if text != original:
        issues.append({"type": "normalized", "detail": "문자/공백 정규화 적용"})

    # 6) 리포트 전용 검출 (수정 안 함)
    for i, line in enumerate(text.split("\n"), 1):
        foreign = _FOREIGN_SCRIPT.findall(line)
        if foreign:
            issues.append({"type": "foreign_script", "line": i,
                           "chars": "".join(sorted(set(foreign))),
                           "text": line[:60]})
        symbols = _SYMBOL.findall(line)
        if symbols:
            issues.append({"type": "symbol", "line": i,
                           "chars": "".join(sorted(set(symbols))),
                           "text": line[:60]})

    return text, issues


def sanitize_record(record: dict, field: str = "lyrics") -> list[dict]:
    """dict 내 field를 제자리 정리. issue 리스트 반환."""
    if field not in record or not isinstance(record[field], str):
        return []
    clean, issues = sanitize_text(record[field])
    record[field] = clean
    return issues


def main():
    ap = argparse.ArgumentParser(description="가사 노이즈 정리")
    ap.add_argument("file", nargs="?", type=Path, help="JSON 배열 파일")
    ap.add_argument("--field", default="lyrics", help="정리할 필드명 (기본 lyrics)")
    ap.add_argument("--out", type=Path, help="출력 경로 (기본: 미저장 리포트만)")
    ap.add_argument("--text", help="단건 텍스트 직접 정리")
    args = ap.parse_args()

    if args.text is not None:
        clean, issues = sanitize_text(args.text)
        print(clean)
        for iss in issues:
            print(f"  ⚠️ {iss}", file=sys.stderr)
        return

    if not args.file:
        ap.error("file 또는 --text 필요")

    records = json.loads(args.file.read_text())
    if not isinstance(records, list):
        records = [records]

    total_issues = 0
    changed = 0
    for idx, rec in enumerate(records):
        before = rec.get(args.field)
        issues = sanitize_record(rec, args.field)
        if rec.get(args.field) != before:
            changed += 1
        for iss in issues:
            if iss["type"] != "normalized":
                total_issues += 1
                print(f"  ⚠️ [{idx}] {iss}")

    print(f"📋 {len(records)}건 처리 — 정규화 변경 {changed}건, 검수대상 {total_issues}건")
    if args.out:
        args.out.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        print(f"  💾 {args.out}")
    elif changed:
        print("  (저장 안 함 — --out 으로 출력 경로 지정)")


if __name__ == "__main__":
    main()
