import pytest

from conv import diffstat
from gitrepo import Repo

EXCLUDES = diffstat.DEFAULT_EXCLUDES


@pytest.fixture
def repo(tmp_path):
    return Repo(tmp_path)


def test_parse_numstat_with_rename_and_binary():
    out = "3\t1\ta.txt\0" "-\t-\timg.png\0" "2\t2\t\0old.txt\0new.txt\0"
    assert diffstat.parse_numstat(out) == [(3, 1, "a.txt"), (None, None, "img.png"), (2, 2, "new.txt")]


@pytest.mark.parametrize("path", ["package-lock.json", "web/yarn.lock", "gradlew", "gradle/wrapper/gradle-wrapper.properties", "app/gradle/wrapper/x.jar"])
def test_excluded_paths(path):
    assert diffstat.is_excluded(path, EXCLUDES)


def test_normal_paths_counted():
    assert not diffstat.is_excluded("src/main/App.java", EXCLUDES)


def test_commit_lines_skip_excluded(repo):
    sha = repo.commit("feat: 추가 (#1)", {"a.txt": 30, "package-lock.json": 500})
    assert diffstat.count_lines(diffstat.commit_rows(sha, cwd=repo.path), EXCLUDES) == 30


def test_list_commits_skips_merges(repo):
    base = repo.commit("docs: 시작 (#1)", {"README.md": 1})
    repo.git("checkout", "-q", "-b", "feat/x")
    repo.commit("feat: 하나 (#2)", {"a.txt": 5})
    repo.git("checkout", "-q", "develop")
    repo.commit("fix: 다른 작업 (#3)", {"b.txt": 5})
    repo.git("checkout", "-q", "feat/x")
    repo.git("merge", "-q", "--no-edit", "develop")
    second = repo.commit("feat: 둘\n\n본문 설명 (#9)", {"c.txt": 7})
    commits = diffstat.list_commits("develop", "feat/x", cwd=repo.path)
    assert [m.split("\n")[0] for _, m in commits] == ["feat: 하나 (#2)", "feat: 둘"]
    assert commits[-1] == (second, "feat: 둘\n\n본문 설명 (#9)")
    rows = diffstat.range_rows("develop", "feat/x", cwd=repo.path)
    assert diffstat.count_lines(rows, EXCLUDES) == 12
    assert base
