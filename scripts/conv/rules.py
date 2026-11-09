"""커밋 메시지와 PR 제목 규칙: Angular 커밋 컨벤션에 이슈 번호를 붙인다.

형식: type(범위): 요약 (#이슈번호)
예:   feat(auth): 로그인 API 추가 (#12)
"""
import re

TYPES = ("build", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test")
HEADER_MAX = 100
FORMAT_HINT = "형식은 `type(범위): 요약 (#이슈번호)`다. 예: feat(auth): 로그인 API 추가 (#12)"

HEADER_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[^()\s]+)\))?(?P<breaking>!)?: "
    r"(?P<subject>.*?) \(#(?P<issue>\d+)\)$"
)
RELEASE_TITLE_RE = re.compile(r"^release: \S.*$")

# PR 템플릿마다 PR 제목에 쓸 수 있는 type
TEMPLATE_TYPES = {
    "feature": ("feat",),
    "bug": ("fix", "revert"),
    "refactor": ("refactor", "perf", "style"),
    "docs": ("docs",),
    "test": ("test",),
    "chore": ("build", "ci"),
}


def check_header(header):
    """첫 줄을 검사해 (오류 목록, 이슈 번호 또는 None)을 돌려준다."""
    errors = []
    if len(header) > HEADER_MAX:
        errors.append(f"첫 줄이 {HEADER_MAX}자를 넘는다({len(header)}자)")
    match = HEADER_RE.match(header)
    if not match:
        errors.append(FORMAT_HINT)
        return errors, None
    if match["type"] not in TYPES:
        errors.append(f"'{match['type']}'는 쓸 수 없는 type이다. 쓸 수 있는 type: {', '.join(TYPES)}")
    subject = match["subject"].strip()
    if not subject:
        errors.append("요약이 비어 있다")
    elif subject.endswith("."):
        errors.append("요약 끝에 마침표를 찍지 않는다")
    return errors, int(match["issue"])


def check_commit_message(message):
    """커밋 메시지 전체를 검사해 (오류 목록, 이슈 번호 또는 None)을 돌려준다."""
    lines = message.strip("\n").split("\n")
    errors, issue = check_header(lines[0].rstrip())
    if len(lines) > 1 and lines[1].strip():
        errors.append("첫 줄과 본문 사이에 빈 줄을 둔다")
    return errors, issue


def header_type(header):
    match = HEADER_RE.match(header)
    return match["type"] if match else None
