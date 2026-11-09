# 협업 규칙

조직의 모든 저장소가 이 규칙을 따릅니다. 규칙 대부분은 CI(`convention / check`)가 PR마다 검사하고, 통과하지 못한 PR은 머지할 수 없습니다.

## 한 번에 보기

1. 할 일을 **이슈**로 만든다. 용도별 이슈 템플릿을 고른다.
2. **develop**에서 작업 브랜치를 만든다. 예: `feat/12-login`
3. **커밋**은 `type(범위): 요약 (#이슈번호)`로 쓰고, 커밋 하나의 변경은 100줄 이하로 한다.
4. **develop으로 PR**을 연다. 용도별 PR 템플릿을 쓰고, 본문에 `Closes #이슈번호`를 적는다. PR 전체 변경은 500줄 이하로 한다.
5. CI(`convention / check`, `test / run`)가 통과하면 머지한다. 이슈는 자동으로 닫힌다.
6. 릴리스할 때 **develop에서 main으로** 릴리스 PR을 연다.

이슈 하나를 PR 하나로 끝내는 것이 기본입니다. PR 하나에는 커밋이 여러 개 들어갑니다. 커밋마다 PR을 따로 만들지 않습니다.

## 브랜치

| 브랜치 | 역할 | 바뀌는 방법 |
|---|---|---|
| `main` | 제출, 배포용 안정 버전 | develop에서 오는 릴리스 PR만 |
| `develop` | 기본 브랜치, 개발 통합 | 작업 브랜치에서 오는 PR만 |
| 작업 브랜치 | 이슈 하나의 작업 | 자유롭게 push |

- main과 develop에는 push할 수 없고 PR로만 바뀝니다. 강제 push와 삭제도 막혀 있습니다(ruleset).
- 작업 브랜치 이름은 `type/이슈번호-설명`을 권장합니다. 예: `fix/31-token-expire`
- 머지 방식은 merge commit 하나만 켜 두었습니다. squash는 100줄 단위 커밋을 하나로 뭉쳐 커밋과 이슈의 연결이 끊기므로 쓰지 않습니다.
- 머지한 작업 브랜치는 자동으로 지워집니다.

## 이슈

빈 이슈는 만들 수 없고 아래 템플릿 중 하나를 고릅니다. 필수 칸을 비우면 그 이슈를 닫는 PR의 CI가 실패합니다.

| 템플릿 | 라벨 | PR 템플릿 | 커밋과 PR 제목 type |
|---|---|---|---|
| 기능 | feature | feature.md | feat |
| 버그 | bug | bug.md | fix, revert |
| 리팩토링 | refactor | refactor.md | refactor, perf, style |
| 문서 | docs | docs.md | docs |
| 테스트 | test | test.md | test |
| 설정 | chore | chore.md | build, ci |

할 일은 커밋 하나(100줄 이하)로 끝낼 수 있을 만큼 잘게 적습니다.

## 커밋

[Angular 커밋 컨벤션](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md)에 이슈 번호를 붙입니다.

```
type(범위): 요약 (#이슈번호)

본문(선택). 무엇을 왜 바꿨는지 쓴다.
```

| type | 쓰는 때 |
|---|---|
| feat | 새 기능 |
| fix | 버그 수정 |
| docs | 문서만 바꿈 |
| style | 동작과 상관없는 서식(공백, 줄바꿈 등) |
| refactor | 동작은 그대로 두고 구조를 바꿈 |
| perf | 성능 개선 |
| test | 테스트 추가나 수정 |
| build | 빌드 설정, 의존성 |
| ci | CI 설정 |
| revert | 앞선 커밋 되돌리기 |

- 범위는 선택입니다. 모듈이나 기능 이름을 씁니다. 예: `auth`, `order`
- 첫 줄은 100자 이하, 요약 끝에 마침표를 찍지 않습니다.
- 본문을 쓰면 첫 줄 다음에 빈 줄을 하나 둡니다.
- 이슈 번호는 반드시 붙이고, 그 PR이 `Closes`로 닫는 이슈 중 하나여야 합니다.
- 머지 커밋(develop을 작업 브랜치로 merge한 커밋 등)은 검사하지 않습니다.

예:

```
feat(auth): 로그인 API 추가 (#12)
fix(cart): 수량이 0일 때 결제되는 문제 수정 (#31)
docs: 설치 방법 정리 (#40)
```

### 커밋이 100줄을 넘을 때

줄 수는 추가와 삭제를 더한 값입니다. 잠금 파일(`package-lock.json`, `yarn.lock` 등), 빌드 래퍼(`gradlew`, `gradle/wrapper/*`, `mvnw` 등), 바이너리 파일은 세지 않습니다.
넘었다면 마지막 커밋을 풀고 나눠 담습니다.

```
git reset HEAD~1
git add -p          # 묶을 부분만 골라 담는다
git commit -m "feat(auth): 토큰 발급 추가 (#12)"
git add -p
git commit -m "feat(auth): 토큰 검증 추가 (#12)"
git push --force-with-lease
```

`git revert`의 기본 메시지는 형식에 맞지 않습니다. `git revert --no-commit <sha>` 뒤에 `git commit -m "revert: 로그인 API 되돌리기 (#12)"`처럼 씁니다.

## PR

- 기본으로 develop에 들어갑니다(develop이 기본 브랜치).
- 용도별 PR 템플릿을 씁니다. PR 만들기 화면 주소 끝에 `&template=feature.md`를 붙이거나, `gh pr create`에서 템플릿을 고릅니다. 템플릿 없이 열면 안내문이 나오고 CI가 실패합니다.
- 제목은 커밋과 같은 형식 `type(범위): 요약 (#이슈번호)`이고, type은 템플릿 용도와 맞아야 합니다(이슈 표 참고).
- 본문 '관련 이슈' 칸에 `Closes #이슈번호`를 적습니다. 제목의 이슈 번호도 이 목록에 있어야 합니다.
- "(선택)"이 붙지 않은 칸은 모두 채우고, 체크리스트는 모두 확인해 `[x]`로 표시합니다.
- PR 전체 변경은 500줄 이하입니다. 넘으면 이슈를 나누고 PR도 나눕니다.

## 릴리스 (develop에서 main)

- develop에서 main으로 PR을 열고 `release.md` 템플릿을 씁니다(`&template=release.md`).
- 제목은 `release: v0.1.0`처럼 버전을 씁니다.
- 포함된 커밋은 develop으로 들어올 때 이미 검사를 거쳤으므로 이슈 연결, 커밋, 크기 검사는 하지 않습니다. 테스트는 다시 돌립니다.
- develop이 아닌 브랜치에서 main으로 연 PR은 CI가 실패해 머지할 수 없습니다.

## CI가 검사하는 것

| 항목 | 내용 |
|---|---|
| 브랜치 흐름 | main으로 가는 PR은 develop에서만 |
| PR 제목 | 형식, type, 이슈 번호 |
| PR 본문 | 용도별 템플릿, 필수 칸, 체크리스트 |
| 이슈 연결 | `Closes #번호`가 있고, 그 이슈가 이슈 템플릿으로 쓰였고 필수 칸이 채워짐 |
| 커밋과 크기 | 모든 커밋의 형식과 이슈 번호, 커밋마다 100줄 이하, PR 전체 500줄 이하 |
| 테스트 | 빌드 파일을 보고 Gradle, Maven, npm, pytest 중 하나로 테스트 실행 |

실패하면 PR의 Checks 탭에서 `convention / check`를 열고 요약(Summary)을 봅니다. 고칠 내용이 항목별로 나옵니다.
PR 제목이나 본문을 고치면 검사가 다시 돕니다. 이슈 본문만 고쳤다면 실패한 검사에서 Re-run을 누릅니다.

## 새 프로젝트 저장소 만들기

1. 조직에 **공개** 저장소를 만들고 README로 첫 커밋을 만듭니다.
2. 이 저장소를 받아 `scripts/setup_repo.sh <저장소 이름>`을 돌립니다(관리자 권한 필요).
   라벨, CI 워크플로(`.github/workflows/ci.yml`), develop 브랜치와 기본 브랜치 지정, merge commit만 허용, main과 develop ruleset을 한 번에 겁니다.
3. 테스트 명령은 자동으로 정해집니다. 맞지 않으면 `ci.yml`의 `test-command`, `working-directory` 주석을 풉니다.

이 저장소의 템플릿과 검사 규칙을 바꿀 때도 같은 흐름(이슈, develop으로 PR, 릴리스 PR)을 따릅니다. 프로젝트 저장소는 main의 규칙을 쓰므로 릴리스해야 반영됩니다.
