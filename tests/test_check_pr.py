from pathlib import Path

import check_pr
from gitrepo import Repo
from test_templates import ISSUE_BODY, fill

ROOT = Path(__file__).resolve().parents[1]
LIMITS = (100, 500, check_pr.parse_excludes([]))
ISSUES = {12: {"number": 12, "body": ISSUE_BODY}, 13: {"number": 13, "body": "자유 형식"}, 14: {"pull_request": {}}}


def make_pr(repo, head="feat/login", base="develop", title="feat(auth): 로그인 추가 (#12)", body=None):
    full = "org/app"
    sha = repo.git("rev-parse", head)
    return {"title": title, "body": fill("feature") if body is None else body,
            "base": {"ref": base, "repo": {"full_name": full}},
            "head": {"ref": head, "sha": sha, "repo": {"full_name": full}}}


def setup(tmp_path, commits):
    repo = Repo(tmp_path)
    repo.commit("docs: 시작 (#1)", {"README.md": 1})
    repo.git("update-ref", "refs/remotes/origin/develop", "develop")
    repo.git("checkout", "-q", "-b", "feat/login")
    for message, files in commits:
        repo.commit(message, files)
    return repo


def errors_of(repo, pr):
    results, _ = check_pr.run(pr, ROOT, repo.path, ISSUES.get, LIMITS)
    return {name: errs for name, errs in results if errs}


def test_good_pr_passes(tmp_path):
    repo = setup(tmp_path, [("feat(auth): 로그인 API (#12)", {"a.py": 80}), ("test(auth): 로그인 테스트 (#12)", {"b.py": 90})])
    assert errors_of(repo, make_pr(repo)) == {}


def test_commit_problems(tmp_path):
    repo = setup(tmp_path, [("로그인 작업", {"a.py": 10}), ("feat: 큰 커밋 (#12)", {"b.py": 101}), ("feat: 다른 이슈 (#99)", {"c.py": 1})])
    errors = errors_of(repo, make_pr(repo))["커밋과 크기"]
    assert len(errors) == 3
    assert any("101줄" in e for e in errors) and any("#99" in e for e in errors)


def test_pr_too_large(tmp_path):
    commits = [(f"feat: 조각 {i} (#12)", {f"f{i}.py": 100}) for i in range(6)]
    repo = setup(tmp_path, commits)
    assert any("600줄" in e for e in errors_of(repo, make_pr(repo))["커밋과 크기"])


def test_issue_problems(tmp_path):
    repo = setup(tmp_path, [("feat: 추가 (#12)", {"a.py": 1})])
    assert "이슈 연결" in errors_of(repo, make_pr(repo, body=fill("feature").replace("Closes #12", "이슈 없음")))
    body = fill("feature").replace("Closes #12", "Closes #12\nCloses #13\nCloses #14\nCloses #15")
    errors = errors_of(repo, make_pr(repo, body=body))["이슈 연결"]
    assert [e[:3] for e in errors] == ["#13", "#14", "#15"]


def test_title_must_match_template(tmp_path):
    repo = setup(tmp_path, [("fix: 고침 (#12)", {"a.py": 1})])
    errors = errors_of(repo, make_pr(repo, title="fix: 고침 (#12)"))
    assert any("feat" in e for e in errors["PR 제목"])


def test_feature_branch_to_main_is_blocked(tmp_path):
    repo = setup(tmp_path, [("feat: 추가 (#12)", {"a.py": 1})])
    errors = errors_of(repo, make_pr(repo, base="main", title="release: v0.1.0", body=fill("release")))
    assert list(errors) == ["브랜치 흐름"]


def test_release_pr_from_develop(tmp_path):
    repo = setup(tmp_path, [])
    pr = make_pr(repo, head="develop", base="main", title="release: v0.1.0", body=fill("release"))
    assert errors_of(repo, pr) == {}
    pr = make_pr(repo, head="develop", base="main", title="feat: 기능 (#12)", body=fill("feature"))
    assert set(errors_of(repo, pr)) == {"PR 제목", "PR 본문"}


def test_summary_markdown():
    text = check_pr.summary_markdown([("PR 제목", []), ("커밋과 크기", ["너무 크다"])], "메모")
    assert "| PR 제목 | 통과 |" in text and "실패 1건" in text and "- 너무 크다" in text
