#!/usr/bin/env python3
"""ingest_suno_sp_emissions.py — ★수노 «산출» SP층을 코퍼스 DB에 적재한다.

왜 이 스크립트가 2026-09-14에야 생겼나 (적어 둔다):
  ⛔**값은 12일째 와 있었는데 내가 층을 잘못 읽어 안 넣고 있었다.**
  결과통의 칸 이름이 `렌더입력SP`(=「입력」)라서 나는 그걸 「우리가 넣은 것이
  되돌아온 칸」으로 읽었다. 실제로는 **수노가 돌려준 값**(API `metadata.tags`와
  바이트 동일 — sunomusic 2026-09-14 실측)이다.
  ★내가 속은 기전 = **Variety 0에서는 수노가 우리 SP를 «그대로» 돌려준다** ⇒
    V0 1,020클립이 전부 우리 것과 같아 보였다.
  ★교훈 = **층은 «이름»이 아니라 «대조»로 정한다.** 대조는 3분 걸렸다.

무엇을 담나:
  · `emitted_sp`  = 결과통 `렌더입력SP` = 수노 산출( layer='suno_out' 고정 )
  · `ordered_sp`  = 내 설계 파일 `sp`   = 우리 발주( 같은 행에 둬야 쌍이 성립 )
  ⛔정규화·번역·트림을 «적재 단계»에서 하지 않는다. 파생은 전부 재현기에서.
  ⛔`expr_*`·사전에 직행 금지 — 신어는 후보 선반(격리)을 경유한다.

사용: .venv/bin/python scripts/ingest_suno_sp_emissions.py [--apply]
      (기본 dry-run — 수만 찍고 쓰지 않는다)
"""
import json, glob, sqlite3, sys, hashlib, os

DB = 'sunolang.db'
INBOX = '/Users/purple/projects/agent-comm/projects/sunolanguage/messages'

DDL = """
CREATE TABLE IF NOT EXISTS suno_sp_emissions (
  clip_uuid      TEXT PRIMARY KEY,
  gid            INTEGER,
  batch          TEXT,
  title          TEXT,
  account        TEXT,
  aug_creativity INTEGER,          -- 클립에 적힌 «실제»값. 판정은 항상 이 칸
  pair_variety   INTEGER,          -- 그쪽 «의도». 어긋나면 클립 기록이 이긴다(09-12 확정)
  layer          TEXT NOT NULL CHECK(layer='suno_out'),
  source_field   TEXT NOT NULL,    -- 그쪽 원래 칸 이름을 축자 보존
  emitted_sp     TEXT NOT NULL,    -- 수노 산출(가공 0)
  ordered_sp     TEXT,             -- 우리 발주(설계 파일)
  rewritten      INTEGER NOT NULL, -- emitted != ordered
  length_ratio   REAL,
  duration_sec   REAL,
  model          TEXT,
  emitted_sha256 TEXT NOT NULL,
  ingested_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sse_aug   ON suno_sp_emissions(aug_creativity);
CREATE INDEX IF NOT EXISTS ix_sse_batch ON suno_sp_emissions(batch);
CREATE INDEX IF NOT EXISTS ix_sse_gid   ON suno_sp_emissions(gid);
"""


def ordered_map():
    """제목 → 발주 SP. ⛔설계 파일이 정본이다(통의 `발주SP_길이`와 2,040/2,040 일치 확인함)."""
    m = {}
    for f in glob.glob('data/n0*/N0*_design.json'):
        for s in json.load(open(f))['songs']:
            m[s['title']] = (s.get('sp') or '').strip()
    return m


def rows():
    om = ordered_map()
    seen, out, nodesign = set(), [], set()
    for f in sorted(glob.glob(f'{INBOX}/**/sunolanguage_sunomusic_*_생성결과.json', recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        b = d.get('body', d)
        batch = b.get('batch')
        for s in (b.get('songs') or []):
            title = s.get('title')
            osp = om.get(title)
            if osp is None:
                nodesign.add(title)
            groups = [(s.get('rendered_sp') or [], None)]
            pc = s.get('pair_clips')
            pc = pc[0] if isinstance(pc, list) and pc else pc
            if isinstance(pc, dict):
                groups.append((pc.get('rendered_sp') or [], pc.get('pair_variety')))
            for g, intent in groups:
                for r in g:
                    if not isinstance(r, dict):
                        continue
                    u = r.get('uuid')
                    sp = (r.get('렌더입력SP') or '').strip()
                    if not u or not sp or u in seen:
                        continue
                    seen.add(u)
                    out.append({
                        'clip_uuid': u, 'gid': s.get('id'), 'batch': batch or (pc or {}).get('batch'),
                        'title': title, 'account': s.get('suno_account') or (pc or {}).get('account'),
                        'aug_creativity': r.get('aug_creativity'), 'pair_variety': intent,
                        'layer': 'suno_out', 'source_field': 'metadata.tags',
                        'emitted_sp': sp, 'ordered_sp': osp,
                        'rewritten': 0 if (osp is not None and sp == osp) else 1,
                        'length_ratio': r.get('길이비'), 'duration_sec': r.get('duration_sec'),
                        'model': s.get('model'),
                        'emitted_sha256': hashlib.sha256(sp.encode()).hexdigest()[:16],
                    })
    return out, nodesign


def main():
    apply = '--apply' in sys.argv
    rs, nodesign = rows()
    by = {}
    for r in rs:
        by.setdefault(f"V{r['aug_creativity']}", [0, 0])
        by[f"V{r['aug_creativity']}"][0] += 1
        by[f"V{r['aug_creativity']}"][1] += r['rewritten']
    print(f"■ 결과통에서 읽은 고유 클립 {len(rs)}")
    for k in sorted(by):
        print(f"   {k}: 클립 {by[k][0]} · ★수노 재작성 {by[k][1]}")
    print(f"   ★재작성 합계 {sum(v[1] for v in by.values())}  ※★단위=«고유 클립»(uuid). "
          f"결과통 «출현»은 {len(rs)}행보다 많다 — 같은 클립이 두 통에 실리는 일이 있다(중복 120건 실측)")
    # ⛔2026-09-14 수리(자적발) — 이 경고가 «제목»을 세어 「304건」을 찍었는데
    #   그 제목들은 **SP 실린 클립이 0**이라 실제 담기는 행은 0이었다.
    #   ★세는 단위를 안 적으면 경고 자체가 거짓 규모를 만든다 ⇒ «행»으로 센다.
    nd_rows = [r for r in rs if r['ordered_sp'] is None]
    if nd_rows:
        print(f"   ⚠발주 SP 대조 불가 {len(nd_rows)}행 — `ordered_sp`=NULL. "
              f"⛔이 행의 `rewritten`=1은 「재작성」이 아니라 «미대조»다")
    else:
        print("   ✅발주 SP 대조 불가 0행 — 담기는 전 행이 설계 파일과 대조된다")
    unk = [r for r in rs if r['aug_creativity'] is None]
    if unk:
        print(f"   ⛔aug_creativity 결손 {len(unk)}건 — 담지 않는다(버킷 미상)")
        rs = [r for r in rs if r['aug_creativity'] is not None]
    if not apply:
        print("\n(dry-run — 쓰지 않았습니다. `--apply`로 집행)")
        return
    if not os.path.exists(DB):
        sys.exit('⛔DB 없음')
    c = sqlite3.connect(DB)
    c.executescript(DDL)
    from datetime import datetime
    now = datetime.now().astimezone().isoformat()
    cols = ['clip_uuid', 'gid', 'batch', 'title', 'account', 'aug_creativity', 'pair_variety',
            'layer', 'source_field', 'emitted_sp', 'ordered_sp', 'rewritten', 'length_ratio',
            'duration_sec', 'model', 'emitted_sha256']
    c.executemany(
        f"INSERT OR REPLACE INTO suno_sp_emissions ({','.join(cols)},ingested_at) "
        f"VALUES ({','.join('?' * len(cols))},?)",
        [[r[k] for k in cols] + [now] for r in rs])
    c.commit()
    n = c.execute('select count(*) from suno_sp_emissions').fetchone()[0]
    print(f"\n✅적재 {n}행")
    # ★양성통제 — 쓰고 나서 «다시 읽어» 왕복을 확인한다(쓴 수를 그대로 믿지 않는다)
    probe = rs[0]
    got = c.execute('select emitted_sp,layer from suno_sp_emissions where clip_uuid=?',
                    (probe['clip_uuid'],)).fetchone()
    ok = got and got[0] == probe['emitted_sp'] and got[1] == 'suno_out'
    print(f"   양성통제(왕복 1건 {probe['clip_uuid'][:8]}): {'✅원문 동일·layer 고정' if ok else '⛔불일치'}")
    miss = c.execute('select count(*) from suno_sp_emissions where clip_uuid=?', ('없는-uuid',)).fetchone()[0]
    print(f"   음성통제(없는 uuid 조회): {miss}건 {'✅' if miss == 0 else '⛔'}")
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
