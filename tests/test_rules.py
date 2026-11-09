import pytest

from conv import rules


@pytest.mark.parametrize("header", [
    "feat: 로그인 API 추가 (#12)",
    "fix(auth): 토큰 만료 처리 (#3)",
    "refactor(order-service)!: 결제 모듈 분리 (#40)",
    "docs: add setup guide (#1)",
])
def test_valid_header(header):
    assert rules.check_header(header)[0] == []


def test_header_returns_issue_number():
    assert rules.check_header("test(cart): 수량 경계값 테스트 (#27)")[1] == 27


@pytest.mark.parametrize("header", [
    "로그인 API 추가",
    "feat: 로그인 API 추가",          # 이슈 번호 없음
    "feat: 로그인 API 추가 #12",      # 괄호 없음
    "feat 로그인 API 추가 (#12)",     # 콜론 없음
    "Feat: 로그인 API 추가 (#12)",    # 대문자 type
    "feat:로그인 API 추가 (#12)",     # 콜론 뒤 공백 없음
    "Merge branch 'develop' into feat/login",
])
def test_invalid_format(header):
    errors, issue = rules.check_header(header)
    assert errors and issue is None


def test_unknown_type():
    errors, issue = rules.check_header("chore: 의존성 정리 (#5)")
    assert any("쓸 수 없는 type" in e for e in errors)
    assert issue == 5


def test_subject_rules():
    assert any("마침표" in e for e in rules.check_header("feat: 로그인 추가. (#1)")[0])
    assert any("비어" in e for e in rules.check_header("feat:  (#1)")[0])


def test_header_length():
    header = "feat: " + "가" * 100 + " (#1)"
    assert any("100자" in e for e in rules.check_header(header)[0])


def test_commit_body_needs_blank_line():
    assert rules.check_commit_message("feat: 추가 (#1)\n\n본문\n")[0] == []
    assert any("빈 줄" in e for e in rules.check_commit_message("feat: 추가 (#1)\n본문")[0])


def test_header_type():
    assert rules.header_type("perf(db): 쿼리 개선 (#9)") == "perf"
    assert rules.header_type("아무 제목") is None
