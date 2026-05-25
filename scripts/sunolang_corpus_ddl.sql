-- sunolang 코퍼스 독립 테이블 DDL
-- Leo 결정 2026-05-25: 같은 PostgreSQL DB 내 독립 테이블로 운영
-- admin 실행 필요 (role_sunolanguage에 CREATE TABLE 권한 없음)

BEGIN;

-- 1. 트랙 (곡 단위)
CREATE TABLE IF NOT EXISTS sunolang_tracks (
    track_id    SERIAL PRIMARY KEY,
    song_id     INT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    genre       TEXT,
    subgenre    TEXT,
    bpm         INT,
    key_signature TEXT,
    original_sp TEXT,
    original_lyrics TEXT,
    is_instrumental BOOLEAN,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 2. 클립 (재분석 단위, 트랙당 1~N개)
CREATE TABLE IF NOT EXISTS sunolang_clips (
    clip_id         SERIAL PRIMARY KEY,
    track_id        INT NOT NULL REFERENCES sunolang_tracks(track_id),
    suno_uuid       UUID,
    reanalysis_sp   TEXT,
    reanalysis_lyrics TEXT,
    reanalysis_genre TEXT,
    source_file     TEXT,
    captured_at     TIMESTAMPTZ,
    sp_length       INT GENERATED ALWAYS AS (length(reanalysis_sp)) STORED
);

-- 3. SP 엔티티 (파싱 결과)
CREATE TABLE IF NOT EXISTS sunolang_sp_entities (
    entity_id   SERIAL PRIMARY KEY,
    track_id    INT NOT NULL REFERENCES sunolang_tracks(track_id),
    slot        TEXT NOT NULL,
    entity      TEXT NOT NULL,
    modifiers   TEXT[],
    pattern     TEXT,
    effects     TEXT[],
    chords      TEXT[],
    sentence    TEXT,
    source      TEXT
);

-- 4. 브래킷 엔티티 (가사 채널 파싱 결과)
CREATE TABLE IF NOT EXISTS sunolang_bracket_entities (
    entity_id   SERIAL PRIMARY KEY,
    track_id    INT NOT NULL REFERENCES sunolang_tracks(track_id),
    slot        TEXT NOT NULL,
    entity      TEXT NOT NULL,
    modifiers   TEXT[],
    bracket     TEXT,
    source      TEXT
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_sunolang_clips_track ON sunolang_clips(track_id);
CREATE INDEX IF NOT EXISTS idx_sunolang_clips_uuid ON sunolang_clips(suno_uuid);
CREATE INDEX IF NOT EXISTS idx_sunolang_sp_ent_track ON sunolang_sp_entities(track_id);
CREATE INDEX IF NOT EXISTS idx_sunolang_sp_ent_slot ON sunolang_sp_entities(slot);
CREATE INDEX IF NOT EXISTS idx_sunolang_bracket_ent_track ON sunolang_bracket_entities(track_id);
CREATE INDEX IF NOT EXISTS idx_sunolang_bracket_ent_slot ON sunolang_bracket_entities(slot);

-- role_sunolanguage 권한
GRANT SELECT, INSERT, UPDATE ON sunolang_tracks TO role_sunolanguage;
GRANT SELECT, INSERT, UPDATE ON sunolang_clips TO role_sunolanguage;
GRANT SELECT, INSERT, UPDATE ON sunolang_sp_entities TO role_sunolanguage;
GRANT SELECT, INSERT, UPDATE ON sunolang_bracket_entities TO role_sunolanguage;
GRANT USAGE, SELECT ON SEQUENCE sunolang_tracks_track_id_seq TO role_sunolanguage;
GRANT USAGE, SELECT ON SEQUENCE sunolang_clips_clip_id_seq TO role_sunolanguage;
GRANT USAGE, SELECT ON SEQUENCE sunolang_sp_entities_entity_id_seq TO role_sunolanguage;
GRANT USAGE, SELECT ON SEQUENCE sunolang_bracket_entities_entity_id_seq TO role_sunolanguage;

COMMIT;
