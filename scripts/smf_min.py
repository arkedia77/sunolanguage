"""smf_min.py — 표준 MIDI 파일 최소 읽개(의존 0). read(path) → {ticks_per_beat, tracks:[{name, notes:[(tick, ch, pitch, vel)]}], tempos:[(tick, us_per_beat)]}."""
import struct


def _vlq(b, i):
    v = 0
    while True:
        c = b[i]; i += 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return v, i


def read(path):
    b = open(path, "rb").read()
    assert b[:4] == b"MThd"
    _, fmt, ntr, div = struct.unpack(">IHHH", b[4:14])
    i, tracks, tempos = 14, [], []
    for _ in range(ntr):
        assert b[i:i + 4] == b"MTrk"
        ln = struct.unpack(">I", b[i + 4:i + 8])[0]
        j, end, t, run, name, notes = i + 8, i + 8 + ln, 0, None, "", []
        while j < end:
            d, j = _vlq(b, j); t += d
            st = b[j]
            if st == 0xFF:
                typ = b[j + 1]; l, k = _vlq(b, j + 2); data = b[k:k + l]; j = k + l
                if typ == 0x03: name = data.decode("utf-8", "replace")
                if typ == 0x51: tempos.append((t, int.from_bytes(data, "big")))
                continue
            if st in (0xF0, 0xF7):
                l, k = _vlq(b, j + 1); j = k + l; continue
            if st & 0x80:
                run = st; j += 1
            hi = run & 0xF0
            n = 1 if hi in (0xC0, 0xD0) else 2
            p = b[j:j + n]; j += n
            if hi == 0x90 and p[1] > 0:
                notes.append((t, run & 0x0F, p[0], p[1]))
        tracks.append({"name": name, "notes": notes})
        i = end
    return {"ticks_per_beat": div, "tracks": tracks, "tempos": tempos}
