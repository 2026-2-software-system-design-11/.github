<!--
이 글은 안내문이다. 아래 표에서 PR 용도에 맞는 템플릿을 골라 본문 전체를 그 템플릿 내용으로 바꾼다.
용도별 템플릿 없이 올린 PR은 CI(convention / check)가 통과시키지 않는다.
-->

## PR 템플릿을 골라 주세요

PR 만들기 화면 주소 끝에 `&template=파일이름`을 붙이면 그 템플릿으로 본문이 채워집니다.
주소에 `?`가 없으면 `?template=파일이름`을 붙입니다. 링크를 열어 내용을 복사해 붙여도 됩니다.

| 용도 | 들어가는 브랜치 | PR 제목 type | 템플릿 |
|---|---|---|---|
| 기능 | develop | feat | [feature.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/feature.md?plain=1) |
| 버그 | develop | fix, revert | [bug.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/bug.md?plain=1) |
| 리팩토링 | develop | refactor, perf, style | [refactor.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/refactor.md?plain=1) |
| 문서 | develop | docs | [docs.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/docs.md?plain=1) |
| 테스트 | develop | test | [test.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/test.md?plain=1) |
| 설정(빌드, CI) | develop | build, ci | [chore.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/chore.md?plain=1) |
| 릴리스 | main (develop에서만) | release | [release.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/.github/PULL_REQUEST_TEMPLATE/release.md?plain=1) |

규칙 전체는 [CONTRIBUTING.md](https://github.com/2026-2-software-system-design-11/.github/blob/main/CONTRIBUTING.md)에 있습니다.
