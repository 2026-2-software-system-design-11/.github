#!/usr/bin/env bash
# 프로젝트 저장소에 조직 규칙을 건다. 여러 번 돌려도 같은 결과가 된다.
#   사용법: scripts/setup_repo.sh <저장소 이름>      예: scripts/setup_repo.sh backend
#   필요: gh 로그인, 저장소 관리자 권한, 공개 저장소, main에 커밋이 하나 이상 있음
# 하는 일: 라벨 만들기, CI 연결(없을 때만), develop 만들기와 기본 브랜치 지정,
#          머지 방식을 merge commit 하나로 제한, main과 develop ruleset 걸기
set -euo pipefail

ORG=2026-2-software-system-design-11
REPO="$ORG/${1:?저장소 이름을 주세요. 예: scripts/setup_repo.sh backend}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKS='[{"context":"convention / check"},{"context":"test / run"}]'

[ "$(gh api "repos/$REPO" --jq .visibility)" = public ] || { echo "공개 저장소만 ruleset을 무료로 걸 수 있습니다: $REPO" >&2; exit 1; }
gh api "repos/$REPO/branches/main" --silent || { echo "main 브랜치가 없습니다. README로 첫 커밋을 먼저 만드세요" >&2; exit 1; }

echo "1. 라벨"
while IFS='|' read -r name color desc; do
  gh label create "$name" -R "$REPO" --color "$color" --description "$desc" --force
done <<'EOF'
feature|0E8A16|새 기능
bug|D73A4A|버그 수정
refactor|5319E7|동작 변화 없는 구조 개선
docs|0075CA|문서
test|FBCA04|테스트
chore|BFD4F2|빌드, CI, 설정
EOF

echo "2. CI 연결"
if gh api "repos/$REPO/contents/.github/workflows/ci.yml?ref=main" --silent 2>/dev/null; then
  echo "   이미 있음"
else
  issue_url=$(gh issue create -R "$REPO" --label chore --title "[chore] 조직 공통 CI 연결" --body "$(printf '%s\n' \
    '### 작업 요약' '' '조직 공통 CI(.github/workflows/ci.yml)를 연결한다.' '' \
    '### 필요한 이유' '' 'PR마다 브랜치 흐름, 템플릿, 커밋 규칙, 테스트를 자동으로 검사하기 위해서다.' '' \
    '### 할 일' '' '- [x] ci.yml 추가' '' '### 영향 범위' '' '_No response_')")
  number="${issue_url##*/}"
  gh api -X PUT "repos/$REPO/contents/.github/workflows/ci.yml" \
    -f message="ci: 조직 공통 CI 연결 (#$number)" -f branch=main \
    -f content="$(base64 < "$HERE/../workflow-templates/convention-ci.yml" | tr -d '\n')" --silent
  gh issue close "$number" -R "$REPO" --comment "main에 ci.yml을 넣었습니다."
fi

echo "3. develop 브랜치"
if ! gh api "repos/$REPO/branches/develop" --silent 2>/dev/null; then
  sha=$(gh api "repos/$REPO/git/ref/heads/main" --jq .object.sha)
  gh api "repos/$REPO/git/refs" -f ref=refs/heads/develop -f sha="$sha" --silent
fi

echo "4. 저장소 설정 (기본 브랜치 develop, merge commit만 허용)"
gh api -X PATCH "repos/$REPO" --silent \
  -f default_branch=develop -F allow_merge_commit=true -F allow_squash_merge=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true \
  -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY

echo "5. ruleset"
ruleset() {  # $1: 브랜치 이름
  cat <<EOF
{"name":"$1 보호","target":"branch","enforcement":"active","bypass_actors":[],
 "conditions":{"ref_name":{"include":["refs/heads/$1"],"exclude":[]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"},
  {"type":"pull_request","parameters":{"required_approving_review_count":0,
   "dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,
   "require_last_push_approval":false,"required_review_thread_resolution":false,
   "allowed_merge_methods":["merge"]}},
  {"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":false,
   "required_status_checks":$CHECKS}}]}
EOF
}
for branch in main develop; do
  id=$(gh api "repos/$REPO/rulesets" --jq ".[] | select(.name == \"$branch 보호\") | .id")
  if [ -n "$id" ]; then
    ruleset "$branch" | gh api -X PUT "repos/$REPO/rulesets/$id" --input - --silent
  else
    ruleset "$branch" | gh api -X POST "repos/$REPO/rulesets" --input - --silent
  fi
  echo "   $branch 보호 적용"
done
echo "완료: https://github.com/$REPO"
