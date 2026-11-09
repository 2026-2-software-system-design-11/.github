from pathlib import Path

import pytest

from conv import issue_forms, templates

ROOT = Path(__file__).resolve().parents[1]
PR_TEMPLATES = templates.load_pr_templates(ROOT / ".github/PULL_REQUEST_TEMPLATE")
ISSUE_FORMS = issue_forms.load_issue_forms(ROOT / ".github/ISSUE_TEMPLATE")


def fill(name):
    """템플릿을 제대로 채운 본문을 만든다."""
    text = (ROOT / ".github/PULL_REQUEST_TEMPLATE" / f"{name}.md").read_text(encoding="utf-8")
    text = text.replace("Closes #\n", "Closes #12\n").replace("- #\n", "- #12 로그인\n")
    text = text.replace("- [ ]", "- [x]")
    lines = []
    for line in text.split("\n"):
        lines.append(line)
        if line.startswith("## ") and "(선택)" not in line and "체크리스트" not in line:
            lines.append("채운 내용")
    return "\n".join(lines)


def test_all_templates_loaded():
    assert set(PR_TEMPLATES) == {"feature", "bug", "refactor", "docs", "test", "chore", "release"}
    assert len(ISSUE_FORMS) == 6


@pytest.mark.parametrize("name", ["feature", "bug", "refactor", "docs", "test", "chore", "release"])
def test_filled_template_passes(name):
    assert templates.check_pr_body(fill(name), PR_TEMPLATES) == (name, [])


def test_raw_template_fails():
    raw = (ROOT / ".github/PULL_REQUEST_TEMPLATE/feature.md").read_text(encoding="utf-8")
    name, errors = templates.check_pr_body(raw, PR_TEMPLATES)
    assert name == "feature"
    assert any("작업 내용" in e for e in errors)
    assert any("체크리스트" in e for e in errors)


def test_default_guide_or_free_text_fails():
    guide = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
    for body in (guide, "로그인 만들었음", None):
        name, errors = templates.check_pr_body(body, PR_TEMPLATES)
        assert name is None and errors


def test_removed_section_and_checklist_item():
    body = fill("feature").replace("## 테스트 방법", "## 다른 제목")
    assert any("테스트 방법" in e for e in templates.check_pr_body(body, PR_TEMPLATES)[1])
    body = fill("feature").replace("- [x] 테스트를 추가했고 로컬에서 통과했다\n", "")
    assert any("체크리스트" in e for e in templates.check_pr_body(body, PR_TEMPLATES)[1])


def test_optional_section_may_be_empty():
    body = fill("feature").replace("## 스크린샷 (선택)\n", "")
    assert templates.check_pr_body(body, PR_TEMPLATES)[1] == []


ISSUE_BODY = """### 작업 요약

CI 연결

### 필요한 이유

검사 자동화

### 할 일

- [ ] 워크플로 추가

### 영향 범위

_No response_
"""


def test_issue_form_passes():
    assert issue_forms.check_issue_body(ISSUE_BODY, ISSUE_FORMS) == ("설정", [])


def test_issue_form_required_empty():
    body = ISSUE_BODY.replace("검사 자동화", "_No response_").replace("- [ ] 워크플로 추가", "- [ ]")
    name, errors = issue_forms.check_issue_body(body, ISSUE_FORMS)
    assert name == "설정" and len(errors) == 2


def test_issue_without_form_fails():
    name, errors = issue_forms.check_issue_body("로그인 기능 만들어야 함", ISSUE_FORMS)
    assert name is None and errors
