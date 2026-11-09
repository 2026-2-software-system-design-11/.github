"""PR 규칙 검사 진입점. GitHub Actions의 pull_request 이벤트에서 돌린다.

검사 항목은 conv/checks.py 맨 위 설명을 본다.
환경 변수: GITHUB_EVENT_PATH, GITHUB_REPOSITORY, GITHUB_TOKEN, GITHUB_STEP_SUMMARY(선택)
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from conv import checks, diffstat, issue_forms, templates  # noqa: E402
from conv.github_api import GitHub  # noqa: E402


def run(pr, conv_dir, repo_dir, fetch_issue, limits):
    """[(항목 이름, 오류 목록)]과 참고 메모를 돌려준다."""
    pr_templates = templates.load_pr_templates(conv_dir / ".github/PULL_REQUEST_TEMPLATE")
    title_errors, body_errors, title_issue = checks.check_title_and_body(pr, pr_templates)
    results = [("브랜치 흐름", checks.check_flow(pr)), ("PR 제목", title_errors), ("PR 본문", body_errors)]
    if pr["base"]["ref"] == "main":
        return results, "릴리스 PR이라 이슈 연결, 커밋, 크기 검사는 건너뛴다(develop에서 이미 검사함)"
    issues = checks.linked_issues(pr.get("body"))
    forms = issue_forms.load_issue_forms(conv_dir / ".github/ISSUE_TEMPLATE")
    results.append(("이슈 연결", checks.check_issues(issues, title_issue, fetch_issue, forms)))
    base = f"origin/{pr['base']['ref']}"
    commit_errors, count, total = checks.check_commits(base, pr["head"]["sha"], issues, limits, repo_dir)
    results.append(("커밋과 크기", commit_errors))
    return results, f"커밋 {count}개, PR 전체 변경 {total}줄(한도 {limits[1]}줄), 연결된 이슈 {issues}"


def summary_markdown(results, note):
    lines = ["## 컨벤션 검사 결과", "", "| 항목 | 결과 |", "|---|---|"]
    lines += [f"| {name} | {'통과' if not errors else f'실패 {len(errors)}건'} |" for name, errors in results]
    lines += ["", note, ""]
    for name, errors in results:
        if errors:
            lines += [f"### {name}", ""] + [f"- {e}" for e in errors] + [""]
    lines.append("규칙 전체: https://github.com/2026-2-software-system-design-11/.github/blob/main/CONTRIBUTING.md")
    return "\n".join(lines)


def parse_excludes(values):
    patterns = list(diffstat.DEFAULT_EXCLUDES)
    for value in values:
        patterns += [p.strip() for p in value.replace(",", "\n").split("\n") if p.strip()]
    return tuple(patterns)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--convention-dir", type=Path, required=True)
    parser.add_argument("--repo-dir", type=Path, default=Path("."))
    parser.add_argument("--commit-max-lines", type=int, default=100)
    parser.add_argument("--pr-max-lines", type=int, default=500)
    parser.add_argument("--exclude", action="append", default=[], help="줄 수에서 뺄 경로 패턴(쉼표나 줄바꿈으로 구분)")
    args = parser.parse_args()

    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    github = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
    pr = dict(event["pull_request"])
    # 다시 돌리기(re-run)에서도 최신 제목과 본문을 쓰도록 새로 읽는다. 커밋 범위는 체크아웃한 이벤트 기준을 쓴다
    fresh = github.pull(pr["number"])
    if fresh:
        pr["title"], pr["body"] = fresh["title"], fresh["body"]
    limits = (args.commit_max_lines, args.pr_max_lines, parse_excludes(args.exclude))
    results, note = run(pr, args.convention_dir, args.repo_dir, github.issue, limits)

    report = summary_markdown(results, note)
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    for name, errors in results:
        for error in errors:
            print(f"::error title={name}::{error}")
    return 1 if any(errors for _, errors in results) else 0


if __name__ == "__main__":
    sys.exit(main())
