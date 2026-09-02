#!/usr/bin/env python3
"""verify_delivery.py — 발신 도달 확인 (★위음성 2종을 도구가 막는다).

왜 있나 (2026-09-02 실측 2건, encore A-164 사례집 패턴 ④ 「도구의 0/빈 출력을 대상 성질로 읽음」):
  ⑴ `git show origin/main:{루트경로}` 만 보면 **수취인이 processed/ 로 이관한 순간 「미도달」로 뜬다.**
     오늘 A-164 회보를 쓰며 인용 실물 2건이 둘 다 그렇게 「부재」로 나왔다(실제로는 도달·처리 완료).
  ⑵ 파일명 대조는 **한글 경로가 옥탈 이스케이프**로 나와 조용히 0건이 된다(`core.quotepath=false` 필요).
     같은 날 이력 대조가 「7건 전부 이력에 없음」이라는 거짓을 냈다.

⇒ 규율을 더 적지 않고 **경로를 지운다**: 루트·processed 양쪽을 보고, 본문 해시까지 대조하고,
   못 찾으면 **rc≠0** 으로 끝낸다(빈 출력이 「없음」으로 읽히지 않게).

사용:
    python3 scripts/verify_delivery.py <to> <파일명 일부> [--hash 본문sha256앞16]
    python3 scripts/verify_delivery.py leomusic3 20260902_120313 --hash 75708c0103c09aed
"""
import argparse, hashlib, json, subprocess, sys

ROOT = "/Users/purple/projects/agent-comm"   # ★통신용 클론(공유). 배선 이전 시 여기 1곳만 바꾼다.

def git(*a):
    return subprocess.run(["git", "-c", "core.quotepath=false", *a],
                          cwd=ROOT, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("to"); ap.add_argument("needle")
    ap.add_argument("--hash", dest="want")
    a = ap.parse_args()

    git("fetch", "-q", "origin")
    tree = git("ls-tree", "-r", "origin/main", "--name-only", "-z").stdout.split("\0")
    hits = [p for p in tree if p.strip()
            and p.startswith(f"projects/{a.to}/messages/") and a.needle in p]
    if not hits:
        print(f"❌ 미도달 — origin/main 트리에 없음 (루트·processed 양쪽 조회함)")
        sys.exit(1)                                   # ★rc≠0: 빈 출력이 「없음」으로 안 읽히게
    for p in hits:
        where = "processed/" if "/processed/" in p else "루트"
        line = f"✅ 도달 [{where}] {p.rsplit('/', 1)[-1][:60]}"
        if a.want:
            body = json.loads(git("show", f"origin/main:{p}").stdout).get("body")
            h = hashlib.sha256(json.dumps(body, ensure_ascii=False,
                                          sort_keys=True).encode()).hexdigest()[:16]
            line += f" · 본문해시 {'일치' if h == a.want else f'❌불일치({h})'}"
            if h != a.want:
                print(line); sys.exit(2)
        print(line)

if __name__ == "__main__":
    main()
