"""PR 본문이 PR 템플릿대로 채워졌는지 검사한다.

규칙은 템플릿 파일에서 읽는다. 템플릿을 고치면 검사도 함께 바뀐다.
첫 줄의 `<!-- template: 이름 -->`으로 템플릿을 구분하고, 제목에 "(선택)"이 없는 `##` 칸은 모두 채워야 한다.
"""
import re
from pathlib import Path

COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MARKER_RE = re.compile(r"<!--\s*template:\s*([a-z-]+)\s*-->")
OPTIONAL = "(선택)"
CHECKLIST = "체크리스트"
NO_RESPONSE = "_No response_"


def split_sections(body, level):
    """`##`(level=2) 같은 제목을 기준으로 {제목: 내용}을 돌려준다."""
    prefix = "#" * level + " "
    sections, current = {}, None
    for line in (body or "").replace("\r\n", "\n").split("\n"):
        if line.startswith(prefix):
            current = line[len(prefix):].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {title: "\n".join(lines) for title, lines in sections.items()}


def content_lines(text):
    return [line.strip() for line in COMMENT_RE.sub("", text or "").split("\n") if line.strip()]


def filled_lines(text, template_text):
    """템플릿에 원래 있던 줄(자리 표시)을 빼고 남은 줄."""
    placeholder = set(content_lines(template_text)) | {NO_RESPONSE}
    return [line for line in content_lines(text) if line not in placeholder]


def load_pr_templates(directory):
    templates = {}
    for path in sorted(Path(directory).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        marker = MARKER_RE.search(text)
        if marker:
            templates[marker.group(1)] = split_sections(text, 2)
    return templates


def check_checklist(text, template_text):
    lines = content_lines(text)
    expected = sum(1 for line in content_lines(template_text) if line.startswith("- [ ]"))
    checked = sum(1 for line in lines if line.lower().startswith("- [x]"))
    if any(line.startswith("- [ ]") for line in lines) or checked < expected:
        return ["체크리스트 항목을 지우지 말고 모두 확인한 뒤 [x]로 표시한다"]
    return []


def check_pr_body(body, templates):
    """(템플릿 이름 또는 None, 오류 목록)을 돌려준다."""
    marker = MARKER_RE.search(body or "")
    if not marker or marker.group(1) not in templates:
        return None, ["용도별 PR 템플릿으로 쓰지 않았다(템플릿 표시 주석이 없다). 기본 안내문의 표에서 템플릿을 골라 본문을 바꾼다"]
    name = marker.group(1)
    got = split_sections(body, 2)
    errors = []
    for title, template_text in templates[name].items():
        if OPTIONAL in title:
            continue
        if title not in got:
            errors.append(f"'## {title}' 칸이 없다")
        elif title == CHECKLIST:
            errors += check_checklist(got[title], template_text)
        elif not filled_lines(got[title], template_text):
            errors.append(f"'## {title}' 칸이 비어 있다")
    return name, errors
