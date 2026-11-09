# 조직 공통 컨벤션

2026-2 소프트웨어시스템설계 11조의 협업 규칙을 모아 둔 저장소입니다.
이 저장소의 이슈 템플릿과 PR 템플릿은 조직의 모든 저장소에 자동으로 적용됩니다.

## 흐름

```
이슈 (용도별 템플릿) → 작업 브랜치 → develop으로 PR → 릴리스 PR (develop → main)
```

- 커밋: `type(범위): 요약 (#이슈번호)`, 커밋마다 변경 100줄 이하
- PR: 용도별 템플릿, 본문에 `Closes #이슈번호`, PR마다 변경 500줄 이하
- main은 develop에서 오는 PR로만 바뀝니다.

규칙 전체는 [CONTRIBUTING.md](CONTRIBUTING.md)를 봅니다.

## 구성

| 경로 | 내용 |
|---|---|
| `.github/ISSUE_TEMPLATE/` | 용도별 이슈 템플릿(기능, 버그, 리팩토링, 문서, 테스트, 설정) |
| `.github/PULL_REQUEST_TEMPLATE/` | 용도별 PR 템플릿과 릴리스 PR 템플릿 |
| `.github/workflows/convention.yml` | 규칙 검사 재사용 워크플로 |
| `.github/workflows/test.yml` | 테스트 실행 재사용 워크플로 |
| `workflow-templates/` | 프로젝트 저장소에 넣을 CI 워크플로 |
| `scripts/check_pr.py` | 규칙 검사 스크립트 |
| `scripts/setup_repo.sh` | 프로젝트 저장소에 규칙(ruleset, develop 기본 브랜치, 라벨)을 거는 스크립트 |
| `tests/` | 검사 스크립트 테스트(`pytest`) |
