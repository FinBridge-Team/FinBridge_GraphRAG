#!/usr/bin/env bash
# GitHub Branch Protection 설정 스크립트
# 사전 조건: gh CLI 설치 및 로그인 (gh auth login)
# 사용법: bash .github/setup_branch_protection.sh <owner> <repo>

set -euo pipefail

OWNER="${1:?Usage: $0 <owner> <repo>}"
REPO="${2:?Usage: $0 <owner> <repo>}"

apply_protection() {
  local branch="$1"
  echo "Applying protection to $branch..."
  gh api \
    --method PUT \
    "repos/${OWNER}/${REPO}/branches/${branch}/protection" \
    --field required_status_checks=null \
    --field enforce_admins=true \
    --field 'required_pull_request_reviews[required_approving_review_count]=1' \
    --field 'required_pull_request_reviews[dismiss_stale_reviews]=true' \
    --field 'restrictions=null' \
    --field 'allow_force_pushes=false' \
    --field 'allow_deletions=false'
  echo "  $branch protection applied."
}

apply_protection "main"
apply_protection "develop"

echo ""
echo "Branch protection rules applied:"
echo "  - main    : force push 금지, PR + 리뷰 1명 필수"
echo "  - develop : force push 금지, PR + 리뷰 1명 필수"
