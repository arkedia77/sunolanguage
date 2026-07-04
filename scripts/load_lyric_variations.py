#!/usr/bin/env python3
"""lyric_variations 적재 — 게이트 통과분(V_PILOT_gated 형식) → DB INSERT.
사용: python3 scripts/load_lyric_variations.py data/lyric_variations/X_gated.json"""
import json,os,sys,psycopg2
def conn():
    conf={}
    for line in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1);conf[k.strip()]=v.strip()
    return psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),
        dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
def main(path):
    g=json.load(open(path)); rows=g["accepted"]; c=conn(); cur=c.cursor(); ins=0
    for r in rows:
        # 중복 방지: 동일 (original, variant) 스킵
        cur.execute("SELECT 1 FROM lyric_variations WHERE original_text=%s AND variant_text=%s",
                    (r["original"],r["variant"]))
        if cur.fetchone(): continue
        cur.execute("""INSERT INTO lyric_variations
          (source_type,source_song_id,source_chunk_id,original_text,variant_text,variant_rank,
           lang,section_tag,cosine_to_src,gate_status,harvested_by)
          VALUES ('variations',%s,%s,%s,%s,%s,%s,%s,%s,'accepted','sunomusic')""",
          (r.get("source_song_id"),r.get("source_chunk_id"),r["original"],r["variant"],
           r.get("variant_rank"),r.get("lang","ko"),r.get("section_tag"),r.get("cosine_to_src")))
        ins+=1
    c.commit()
    cur.execute("SELECT count(*) FROM lyric_variations WHERE gate_status='accepted'")
    print(f"적재 {ins} (누적 accepted {cur.fetchone()[0]})"); c.close()
if __name__=="__main__": main(sys.argv[1])
