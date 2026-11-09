"""git 커밋 목록과 변경 줄 수(추가 + 삭제)를 구한다.

잠금 파일과 빌드 도구 래퍼처럼 도구가 만드는 파일, 바이너리 파일은 줄 수에서 뺀다.
"""
import fnmatch
import subprocess

DEFAULT_EXCLUDES = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock",
    "Pipfile.lock", "Cargo.lock", "go.sum", "gradle.lockfile",
    "gradlew", "gradlew.bat", "*gradle/wrapper/*", "mvnw", "mvnw.cmd", "*.mvn/wrapper/*",
)


def git(*args, cwd=None):
    result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout


def is_excluded(path, patterns):
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(name, p) for p in patterns)


def parse_numstat(output):
    """`--numstat -z` 출력을 (추가, 삭제, 경로) 목록으로 바꾼다. 바이너리는 줄 수가 None이다."""
    tokens = output.split("\0")
    rows = []
    i = 0
    while i < len(tokens):
        token = tokens[i].lstrip("\n")
        if not token:
            i += 1
            continue
        added, deleted, path = token.split("\t", 2)
        if path == "":  # 이름 바꾸기: 다음 두 토큰이 옛 경로와 새 경로다
            path = tokens[i + 2]
            i += 3
        else:
            i += 1
        if added == "-":
            rows.append((None, None, path))
        else:
            rows.append((int(added), int(deleted), path))
    return rows


def count_lines(rows, excludes):
    total = 0
    for added, deleted, path in rows:
        if added is None or is_excluded(path, excludes):
            continue
        total += added + deleted
    return total


def commit_rows(sha, cwd=None):
    out = git("diff-tree", "--no-commit-id", "--root", "-r", "-M", "--numstat", "-z", sha, cwd=cwd)
    return parse_numstat(out)


def range_rows(base, head, cwd=None):
    return parse_numstat(git("diff", "-M", "--numstat", "-z", f"{base}...{head}", cwd=cwd))


def list_commits(base, head, cwd=None):
    """base..head의 머지가 아닌 커밋을 오래된 순서로 (sha, 메시지) 목록으로 돌려준다."""
    out = git("log", "--no-merges", "--reverse", "--format=%H%x00%B%x00", f"{base}..{head}", cwd=cwd)
    parts = out.split("\0")
    return [(parts[i].strip(), parts[i + 1].strip("\n")) for i in range(0, len(parts) - 1, 2)]
