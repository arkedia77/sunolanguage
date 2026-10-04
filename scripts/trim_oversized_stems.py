#!/usr/bin/env python3
"""50MB 초과 스템을 15초 중심부로 잘라서 mushin에 전송"""

import subprocess
import json
import os
import sys
import shlex

# ★2026-10-04 경로 이동(sunomusic `20261004_221628` 고지 · LEO 「수노뮤직 하드에서 니꺼는 다 지워」):
#   옛 `/Volumes/sunomusic/…` 은 **지워졌다** — 「없음」이 아니라 「옮겨졌다」. 같은 하위 구조로 Leombank 에 있다.
#   ⛔옛 경로로 두면 이 스크립트는 「대상 0건」을 조용히 찍는다(실패가 아니라 침묵이라 더 나쁘다).
STEMS_BASE = os.environ.get("SUNOMUSIC_BASE", "/Volumes/Leombank/sunomusic1/sunolanguage")
STEMS_REMOTE = f"{STEMS_BASE}/stems"
TRIMMED_REMOTE = f"{STEMS_BASE}/stems_trimmed"
# 08-23 실측: 172.30.1.77(DHCP 사설IP)은 ping 불통 — 죽은 주소.
# sunomusic 회신(08-23 21:35) = mukl·mushin 동일 머신, 고정 주소는 tailscale.
# ⛔2026-10-04 경고 — 이 주소로의 ssh 는 **다른 머신에서 금지**일 수 있다.
#   sunomusic `20261004_222913` 정정: `mushin@100.75.69.61` 경유는 **mukl 이 자기 자신에 접속할 때만** 맞고,
#   다른 머신의 키는 **Slack 발신 전용**이라 셸이 안 열린다 — leomusic3 에서 **Slack 채널이 생기는 사고**가 났다(admin 수리).
#   ★이 스크립트는 그 정정 이전(08-23)에 쓰였고 purple 에서 그 주소를 쓴다 ⇒ **돌리기 전에 sunomusic 에 확인할 것.**
#   자료가 필요하면 sunomusic 에 요청해 mukl 안에서 꺼내는 쪽이 안전하다.
MUSHIN = "mushin@100.75.69.61"  # tailscale 고정 (구: mushin@172.30.1.77)
LOCAL_TMP = "/tmp/stems_trim"
TRIM_DURATION = 15  # seconds
SIZE_LIMIT = 50 * 1024 * 1024  # 50MB
STEM_NAMES = ["drums", "bass", "other", "vocals"]

def get_oversized_stems():
    """50MB 초과 스템 파일 목록 (id 19~100만)"""
    cmd = f'ssh {MUSHIN} \'find {STEMS_REMOTE} -name "*.wav" -size +50M\''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    files = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        # extract id from path
        basename = os.path.basename(os.path.dirname(line))
        try:
            track_id = int(basename.split('_')[0])
        except ValueError:
            continue
        if 19 <= track_id <= 100:
            files.append(line)
    return files

def get_duration(local_path):
    """WAV 파일 길이(초)"""
    cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
           '-of', 'csv=p=0', local_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def trim_center(local_in, local_out, duration=TRIM_DURATION):
    """중심부 15초 추출"""
    total = get_duration(local_in)
    start = max(0, (total - duration) / 2)
    cmd = ['ffmpeg', '-y', '-i', local_in, '-ss', str(start), '-t', str(duration),
           '-c', 'copy', local_out]
    subprocess.run(cmd, capture_output=True, check=True)

def main():
    os.makedirs(LOCAL_TMP, exist_ok=True)

    # 리모트에 trimmed 폴더 생성
    subprocess.run(['ssh', MUSHIN, f'mkdir -p "{TRIMMED_REMOTE}"'], check=True)

    files = get_oversized_stems()
    # group by folder
    folders = {}
    for f in files:
        folder = os.path.basename(os.path.dirname(f))
        folders.setdefault(folder, []).append(f)

    print(f"총 {len(folders)}곡, {len(files)}개 스템 트리밍 예정")

    # check already done folders on remote
    done_check = subprocess.run(['ssh', MUSHIN, f'ls "{TRIMMED_REMOTE}/" 2>/dev/null'],
                                capture_output=True, text=True)
    done_folders = set(done_check.stdout.strip().split('\n')) if done_check.returncode == 0 else set()

    for i, (folder, stem_files) in enumerate(sorted(folders.items()), 1):
        if folder in done_folders:
            print(f"\n[{i}/{len(folders)}] {folder} — already done, skip")
            continue
        print(f"\n[{i}/{len(folders)}] {folder}")
        local_folder = os.path.join(LOCAL_TMP, folder)
        os.makedirs(local_folder, exist_ok=True)

        for remote_path in stem_files:
            stem_name = os.path.basename(remote_path)
            local_in = os.path.join(local_folder, f"orig_{stem_name}")
            local_out = os.path.join(local_folder, stem_name)

            # download via ssh cat (avoids all shell escaping issues with rsync/scp)
            print(f"  ↓ {stem_name}", end="", flush=True)
            with open(local_in, 'wb') as out:
                subprocess.run(['ssh', MUSHIN, f'cat "{remote_path}"'], stdout=out, check=True)

            # trim
            trim_center(local_in, local_out)
            size_mb = os.path.getsize(local_out) / (1024*1024)
            print(f" → {size_mb:.1f}MB ✓")

            # cleanup original
            os.remove(local_in)

        # upload trimmed folder via ssh cat (avoids shell escaping)
        remote_dest = f"{TRIMMED_REMOTE}/{folder}"
        subprocess.run(['ssh', MUSHIN, f'mkdir -p "{remote_dest}"'], check=True)
        wav_files = [f for f in os.listdir(local_folder) if f.endswith('.wav')]
        for wf in wav_files:
            local_wf = os.path.join(local_folder, wf)
            remote_wf = f"{remote_dest}/{wf}"
            with open(local_wf, 'rb') as inp:
                subprocess.run(['ssh', MUSHIN, f'cat > "{remote_wf}"'], stdin=inp, check=True)
        print(f"  ↑ uploaded to {remote_dest}")

        # cleanup local
        for f in os.listdir(local_folder):
            os.remove(os.path.join(local_folder, f))

    print(f"\n완료! {TRIMMED_REMOTE}/ 에 트리밍된 스템 저장됨")
    print("sunomusic은 50MB 초과 곡에 대해 stems_trimmed/ 폴더 사용")

if __name__ == "__main__":
    main()
