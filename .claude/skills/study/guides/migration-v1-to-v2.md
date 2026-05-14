# migration-v1-to-v2 — 점진적 마이그레이션 절차

study v1 → v2 변경사항을 기존 학습 자산에 적용하는 방법. 강제 일괄 변환이 아닌 **lazy backfill** 원칙.

## 변경 요약

| 영역 | v1 | v2 |
|---|---|---|
| 단계 수 | 3 (Explain/Execute/Quiz) | 5 + 옵션 Verify |
| 약점 태그 | 6개 flat | 17개 + 도메인 prefix |
| concepts 메타 | 없음 | frontmatter (정적) + `meta/{개념}.json` (동적) |
| 누적 복습 | 없음 | FSRS + `log/review-queue.md` |
| 자신감 추적 | 없음 | confidence_history (Quiz 시작 시 예측) |
| Bloom 매핑 | `[하/중/상/최상]` 라벨만 | L1~L6 명시 매핑 |
| 영역 분류 | 디렉토리 prefix 자유 | `domain` frontmatter 필드 (tech/system-design/softskill/process) |

## 1회성 마이그레이션 (수동 또는 스킬 첫 진입 시)

다음 두 가지는 v2 첫 진입 시점에 사용자에게 확인받고 일괄 처리.

### 1-1. weakness.md 태그 prefix 추가

기존 6개 태그 → `#tech/` prefix 추가:
- `#용어혼동` → `#tech/용어혼동`
- `#실행순서` → `#tech/실행순서`
- `#엣지케이스` → `#tech/엣지케이스`
- `#문법` → `#tech/문법`
- `#개념누락` → `#tech/개념누락`
- `#응용부족` → `#tech/응용부족`

`log/weakness.md`에서 in-place 치환. 출현 횟수, 발견 주제, 보완 전략은 그대로 유지.

### 1-2. log/review-queue.md 신규 생성

빈 큐 파일 생성 (스킬이 첫 학습 세션부터 자동 갱신):

```markdown
# Review Queue
최종 업데이트: 2026-05-14

## Due Today
(none)

## Due This Week
(none)

## Upcoming
(none)
```

## Lazy backfill (concepts 파일 단위)

frontmatter 없는 기존 concepts 파일은 강제 마이그레이션하지 않는다. 다음 시점에 자동 보강:

### 트리거: 해당 주제 재학습 또는 명시적 복습
- 사용자가 같은 `{대주제}/{소주제}` 학습 요청
- review-queue에서 due 카드로 진입

### 보강 절차
1. 스킬이 `concepts/{개념}.md` Read → frontmatter 부재 감지
2. 디렉토리·내용으로 `domain` 추정:
   - `claude-code/`, `codex/`, `dev-tools/` → tech
   - `software-testing/` → tech (process일 수도 있음, 사용자 확인)
   - `ai-ml/` → tech
   - `harness-engineering/`, `observability/` → 사용자 확인 (tech 또는 process)
3. AskUserQuestion으로 사용자 확인 (추정값 1개 + 대안 2~3개)
4. 승인 시 frontmatter 주입 (`guides/schema-v2.md` §4 참조)
5. `meta/{개념}.json`을 신규 생성 — FSRS 초기값 (stability=1.0, state="new")
6. 기존 본문은 절대 수정하지 않음 — frontmatter만 추가

### 보강 안 됨 상태 처리
- frontmatter 없는 파일은 review-queue에 등록되지 않음 (stability=0 가상 처리)
- history.md의 누적 사이클 카운트는 그대로 유지 (`bloom_achieved_max`는 추정 불가하여 비워둠, 다음 세션 Quiz 결과로 채워짐)

## history.md 처리

기존 history.md 엔트리는 **수정하지 않는다.** v1 형식 그대로 보존. v2 항목부터 새 확장 컬럼(`guides/logging.md` 참조) 적용.

## 충돌 처리

### v1 `[하/중/상/최상]`과 v2 Bloom 레벨 매칭
재학습 시점에 자동 변환 (참고만, 기록 변경 X):
- 하 → L1 Remember
- 중 → L2 Understand 또는 L3 Apply
- 상 → L3 Apply 또는 L4 Analyze
- 최상 → L4 Analyze 이상

### Q&A 섹션 누락
일부 v1 concepts 파일에 `## Q&A` 섹션이 없는 경우 — v2에서 Q&A 발생 시 자동 추가, 기존 본문 유지.

### Step 모드 누락
`session_modes_used` 추정 불가능하면 빈 배열 `[]` 또는 추측 가능한 경우 추정값 (예: 실습 파일 `.py`가 있으면 모드 B).

## 검증

마이그레이션 후 다음 확인:
- `git diff log/weakness.md` — 태그 prefix만 변경, 출현 횟수 등 보존
- `cat log/review-queue.md` — 빈 섹션 3개 (Due Today / Due This Week / Upcoming)
- 첫 학습 세션 실행 후 `meta/{개념}.json` 정상 생성 여부

## 롤백 (필요 시)

`git revert` 가능. `meta/*.json` 파일은 git에 추가했다면 같이 revert. lazy backfill로 추가된 frontmatter는 개별 파일 단위로 수정.
