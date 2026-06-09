# 브랜치 전략 (GitHub Flow 기반)

## 브랜치 구조

```
main          ─── 프로덕션 릴리즈 전용 (보호됨, force push 금지)
  └── develop ─── 통합 개발 브랜치 (보호됨, force push 금지)
        └── feature/<이름>  ── 기능 개발
        └── fix/<이름>      ── 버그 수정
        └── hotfix/<이름>   ── 긴급 수정 (main 직접 머지 가능)
        └── chore/<이름>    ── 설정·의존성·문서 등 비기능 작업
```

## 머지 흐름

```
feature/* → develop → main
```

1. `develop`에서 feature 브랜치를 생성합니다.
2. 작업 완료 후 `develop`으로 Pull Request를 올립니다.
3. 코드 리뷰 후 `develop`에 Squash Merge합니다.
4. 릴리즈 준비가 완료되면 `develop` → `main` PR을 올립니다.
5. `main` 머지 후 버전 태그를 붙이고 릴리즈를 생성합니다.

> **hotfix**는 예외적으로 `main`에서 분기해 `main`과 `develop` 양쪽에 머지합니다.

## 브랜치 보호 규칙

| 브랜치    | force push | 직접 push | PR 필수 | 리뷰 승인 |
|-----------|-----------|-----------|---------|----------|
| `main`    | 금지       | 금지       | 필수     | 1명 이상  |
| `develop` | 금지       | 금지       | 필수     | 1명 이상  |

> GitHub 저장소 → Settings → Branches → Branch protection rules에서 위 규칙을 설정하세요.

## 릴리즈

- 릴리즈 버전은 **`main` 브랜치**에서만 태그를 생성합니다.
- 버전은 [Semantic Versioning](https://semver.org/)을 따릅니다: `vMAJOR.MINOR.PATCH`
- 태그 생성 후 GitHub Releases에 변경사항을 기록합니다.

```bash
# 릴리즈 예시
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## 브랜치 네이밍 규칙

| 유형     | 형식                        | 예시                          |
|----------|-----------------------------|-------------------------------|
| feature  | `feature/<짧은-설명>`       | `feature/kafka-consumer`      |
| fix      | `fix/<짧은-설명>`           | `fix/spark-null-pointer`      |
| hotfix   | `hotfix/<짧은-설명>`        | `hotfix/auth-token-expiry`    |
| chore    | `chore/<짧은-설명>`         | `chore/update-dependencies`   |
| release  | `release/<버전>`            | `release/v1.2.0`              |

## 커밋 메시지 규칙

[Conventional Commits](https://www.conventionalcommits.org/) 형식을 사용합니다.

```
<type>(<scope>): <요약>

[본문 — 선택]
[푸터 — 선택]
```

| type     | 사용 시점                     |
|----------|-------------------------------|
| feat     | 새 기능                        |
| fix      | 버그 수정                      |
| docs     | 문서 변경                      |
| chore    | 빌드·설정·의존성               |
| refactor | 기능 변경 없는 코드 개선       |
| test     | 테스트 추가·수정               |
| perf     | 성능 개선                      |
