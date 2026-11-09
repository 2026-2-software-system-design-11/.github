"""이슈 본문이 이슈 템플릿(이슈 폼 yml)대로 쓰였는지 검사한다.

이슈 폼으로 만든 이슈는 칸마다 `### 칸 이름` 제목이 붙는다. 필수 칸이 모두 있고 비어 있지 않아야 한다.
"""
from pathlib import Path

import yaml

from .templates import filled_lines, split_sections


def load_issue_forms(directory):
    forms = {}
    for path in sorted(Path(directory).glob("*.yml")):
        if path.name == "config.yml":
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        fields = []
        for element in data.get("body", []):
            if element.get("type") == "markdown":
                continue
            attrs = element.get("attributes", {})
            required = bool((element.get("validations") or {}).get("required"))
            fields.append((attrs["label"], required, str(attrs.get("value", ""))))
        forms[data["name"]] = fields
    return forms


def check_issue_body(body, forms):
    """본문이 어느 이슈 템플릿으로 쓰였는지 찾고 필수 칸을 검사한다. (템플릿 이름 또는 None, 오류 목록)."""
    got = split_sections(body, 3)
    for name, fields in forms.items():
        required = [(label, default) for label, req, default in fields if req]
        if required and all(label in got for label, _ in required):
            empty = [label for label, default in required if not filled_lines(got[label], default)]
            return name, [f"'{name}' 템플릿의 필수 칸 '{label}'이 비어 있다" for label in empty]
    return None, ["이슈 템플릿으로 쓴 이슈가 아니다. 이슈 만들기에서 용도별 템플릿을 골라 다시 쓴다"]
