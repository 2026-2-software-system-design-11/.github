"""PR 하나에 대한 규칙 검사를 모아 돌린다.

1. 브랜치 흐름: main으로 가는 PR은 develop에서만 연다.
2. PR 제목: 일반 PR은 `type(범위): 요약 (#이슈번호)`, 릴리스 PR은 `release: 버전`.
3. PR 본문: 용도별 템플릿으로 쓰고 필수 칸을 채운다. 제목 type이 템플릿 용도와 맞는다.
4. 이슈 연결: 본문에 `Closes #번호`로 이슈를 잇고, 그 이슈는 이슈 템플릿으로 쓰여 있다.
5. 커밋: 모든 커밋이 규칙을 지키고 이 PR이 닫는 이슈 번호를 단다. 커밋마다 변경 한도 이하.
6. PR 크기: 전체 변경 한도 이하.
릴리스 PR은 이미 검사를 거친 커밋을 모으는 PR이라 1, 2, 3만 검사한다.
"""
import re

from . import diffstat, issue_forms, rules, templates

CLOSING_RE = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b", re.I)


def linked_issues(body):
    return sorted({int(n) for n in CLOSING_RE.findall(templates.COMMENT_RE.sub("", body or ""))})


def check_flow(pr):
    base, head = pr["base"]["ref"], pr["head"]["ref"]
    head_repo = (pr["head"].get("repo") or {}).get("full_name")
    errors = []
    if base == "main" and (head != "develop" or head_repo != pr["base"]["repo"]["full_name"]):
        errors.append(f"main으로 가는 PR은 develop에서만 연다(지금: {head}). 작업 브랜치의 PR은 develop으로 보낸다")
    if head == "main":
        errors.append("main에서 다른 브랜치로 PR을 열지 않는다")
    return errors


def check_title_and_body(pr, pr_templates):
    """(제목 오류, 본문 오류, 제목의 이슈 번호)."""
    release = pr["base"]["ref"] == "main"
    title = pr["title"].strip()
    name, body_errors = templates.check_pr_body(pr.get("body"), pr_templates)
    if release:
        title_errors = [] if rules.RELEASE_TITLE_RE.match(title) else ["릴리스 PR 제목은 `release: 버전` 형식이다. 예: release: v0.1.0"]
        if name and name != "release":
            body_errors.append("main으로 가는 PR은 release.md 템플릿을 쓴다")
        return title_errors, body_errors, None
    title_errors, title_issue = rules.check_header(title)
    if name == "release":
        body_errors.append("release.md 템플릿은 develop에서 main으로 가는 PR에만 쓴다")
    elif name:
        kind, allowed = rules.header_type(title), rules.TEMPLATE_TYPES.get(name, ())
        if kind and kind not in allowed:
            title_errors.append(f"{name}.md 템플릿 PR의 제목 type은 {', '.join(allowed)} 중 하나다(지금: {kind})")
    return title_errors, body_errors, title_issue


def check_issues(issues, title_issue, fetch_issue, forms):
    if not issues:
        return ["PR 본문 '관련 이슈' 칸에 `Closes #이슈번호`로 이 PR이 닫을 이슈를 적는다"]
    errors = []
    if title_issue is not None and title_issue not in issues:
        errors.append(f"PR 제목의 #{title_issue}가 본문의 Closes 목록에 없다")
    for number in issues:
        issue = fetch_issue(number)
        if issue is None:
            errors.append(f"#{number} 이슈를 찾을 수 없다")
        elif "pull_request" in issue:
            errors.append(f"#{number}는 이슈가 아니라 PR이다")
        else:
            errors += [f"#{number}: {e}" for e in issue_forms.check_issue_body(issue.get("body"), forms)[1]]
    return errors


def check_commits(base, head, issues, limits, repo_dir):
    """(오류 목록, 커밋 수, PR 전체 변경 줄 수)."""
    commit_max, pr_max, excludes = limits
    errors = []
    commits = diffstat.list_commits(base, head, cwd=repo_dir)
    for sha, message in commits:
        problems, number = rules.check_commit_message(message)
        if number is not None and issues and number not in issues:
            problems.append(f"#{number}가 이 PR의 Closes 목록에 없다")
        lines = diffstat.count_lines(diffstat.commit_rows(sha, cwd=repo_dir), excludes)
        if lines > commit_max:
            problems.append(f"변경이 {lines}줄로 커밋 한도 {commit_max}줄을 넘는다. 커밋을 나눈다")
        header = message.split("\n")[0]
        errors += [f"{sha[:7]} \"{header}\": {p}" for p in problems]
    total = diffstat.count_lines(diffstat.range_rows(base, head, cwd=repo_dir), excludes)
    if total > pr_max:
        errors.append(f"PR 전체 변경이 {total}줄로 한도 {pr_max}줄을 넘는다. PR을 나눈다")
    return errors, len(commits), total
