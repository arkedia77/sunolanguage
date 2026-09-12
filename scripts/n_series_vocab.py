#!/usr/bin/env python3
"""n_series_vocab.py — 출력층 코퍼스에서 「관측된 어휘」 집합을 뽑아 둔다(게이트 G2 자료).

★왜 필요한가: 2026-09-11 N021~N040 라인에서 **미관측 악기 4종**(Hammond organ·slide guitar·
tenor saxophone·post-rock)이 내 손버릇으로 SP에 들어갔다. 사전은 관측이지 화이트리스트가
아니지만, **내가 코퍼스 밖으로 나갔다는 사실 자체는 발주 전에 알아야 한다.**

자 = `data/reanalysis_v2/lexical_index.sqlite`(Suno 재분석 SP 20,456행) + `rag/suno_dictionary_v3.json`.
⛔이건 **출력층**(Suno가 우리 렌더를 그렇게 서술한 문장)이다. 입력층(우리가 써넣은 SP)이 아니다.
"""
import json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
DICT = ROOT / "rag/suno_dictionary_v3.json"
OUT = ROOT / "data/n_series_attested_vocab.json"


def _as_list(v):
    if not v:
        return []
    v = v.strip()
    if v.startswith("["):
        try:
            return json.loads(v)
        except Exception:
            return []
    return [v]


def build():
    con = sqlite3.connect(IDX)
    cur = con.cursor()
    ents, mods, genres = set(), set(), set()
    cur.execute("SELECT slot, entity, modifiers, genre FROM entries")
    for slot, entity, modifiers, genre in cur.fetchall():
        for e in _as_list(entity):
            ents.add(e.lower().strip())
        for m in _as_list(modifiers):
            mods.add(m.lower().strip())
        if genre:
            genres.add(genre.strip())
    cur.execute("SELECT lower(phrase) FROM phrases")
    phrases = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT word FROM words WHERE freq_sp > 0 OR freq_total > 0")
    words_out = {r[0] for r in cur.fetchall()}
    con.close()

    d = json.loads(DICT.read_text(encoding="utf-8"))
    for k in ("instrument_phrases", "mood_emotion", "tempo_rhythm", "timbre_texture",
              "technique_patterns"):
        ents.update(x.lower() for x in d.get(k, {}))
    for k in ("drum_vocab", "production_vocab", "harmony_vocab", "dynamics_structure",
              "vocal_expressions", "vocal_chorus"):
        for key in d.get(k, {}):
            for x in _as_list(key):
                ents.add(x.lower())
    genres.update(d.get("genre_vocabulary_map", {}))

    out = {
        "★층": "출력층(Suno 재분석 SP) — 입력층 아님. 사전은 관측이지 화이트리스트가 아니다.",
        "자": {"lexical_index": str(IDX.relative_to(ROOT)), "dictionary": d.get("version")},
        "entities": sorted(e for e in ents if e),
        "modifiers": sorted(m for m in mods if m),
        "phrases": sorted(phrases),
        "words_output_layer": sorted(words_out),
        "genres": sorted(g for g in genres if g),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {OUT.relative_to(ROOT)} — entity {len(out['entities'])} · modifier {len(out['modifiers'])} "
          f"· phrase {len(out['phrases'])} · word {len(out['words_output_layer'])} · genre {len(out['genres'])}")


if __name__ == "__main__":
    build()
