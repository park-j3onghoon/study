# schema-v2 — 메타데이터·도메인·약점 카탈로그

study v2의 데이터 스펙. 다른 guide에서 이 파일을 참조하여 일관성을 유지한다.

## 1. 도메인 4분류

| domain | 디렉토리 예 | Step 2 기본 모드 | 추가 자산 폴더 |
|---|---|---|---|
| `tech` | claude-code, ai-ml, dev-tools, software-testing | A(CLI) / B(코드) | `practice/` |
| `system-design` | system-design, observability 일부 | C + Mermaid 강조 | `diagrams/*.mmd` |
| `softskill` | softskill | C — 시나리오·롤플레이 | `scenarios/*.md` |
| `process` | harness-engineering, process | C — 체크리스트 시뮬레이션 | `checklists/*.md` |

- domain은 frontmatter `domain:` 필드로 명시
- 디렉토리 prefix는 자유 (기존 그대로 유지)
- 빈 자산 폴더는 만들지 않음 (YAGNI)
- 1개 디렉토리에 여러 domain 혼재 가능 (개별 파일 frontmatter로 구분)

## 2. 약점 태그 카탈로그 (총 17개)

### tech (6개, 기존 + prefix)
```
#tech/용어혼동       비슷한 이름·역할 개념 혼동
#tech/실행순서       단계·의존성 순서 실수
#tech/엣지케이스     경계·예외 처리 누락
#tech/문법           구문·괄호·세미콜론 등 표면 실수
#tech/개념누락       전제 개념 빠짐
#tech/응용부족       기본은 알지만 변형·조합 실패
```

### design (4개, 신설)
```
#design/트레이드오프누락        장단점 중 한 면만 봄
#design/스케일성무시            부하·증분 시나리오 누락
#design/일관성결여              CAP·트랜잭션 경계 혼동
#design/추상화레벨미스매치      너무 추상 / 너무 구체
```

### softskill (4개, 신설)
```
#soft/의도전달부족      결론·요구가 모호
#soft/구조화부족        SCQA·MECE 깨짐
#soft/공감결여          청자 입장 누락
#soft/피드백톤          평가-관찰 분리 실패
```

### meta (3개, 자신감·메타인지)
```
#meta/과신              예측 자신감 > 실제 정답률 +20%
#meta/저신              예측 자신감 < 실제 정답률 -20%
#meta/일관성결여        같은 개념 정답률 변동 큼
```

## 3. 도메인 가중치 & 해소 조건

### 가중치 (다음 주제 추천 시 약점 점수 계산용)
- `#tech/*` 1.0
- `#design/*` 1.2
- `#soft/*` 1.2
- `#meta/*` 0.8

### 해소 조건
- **일반 태그**: 3회 연속 정답 **AND** 같거나 더 높은 Bloom 레벨에서 (낮은 레벨로 해소하는 부정행위 방지)
- **`#meta/과신|저신`**: 최근 3회 confidence delta 평균이 ±10% 이내가 3회 연속
- **`#meta/일관성결여`**: 같은 개념을 3회 연속 동일 정답률(±10%)로 통과

### 다음 주제 추천 점수 공식
```
score = 도메인가중치 × (출현 횟수 − 해소 카운트) + FSRS 만기 페널티
FSRS 만기 페널티 = max(0, 오늘 - next_due) × 0.1
```
점수 상위 3개 주제를 Step 0 직전에 사용자에게 제안.

## 4. concepts/{개념}.md frontmatter (정적 메타)

```yaml
---
concept_id: claude-code/rules-vs-skills
title: "Claude Code: Rules vs Skills"
domain: tech                     # tech | system-design | softskill | process
bloom_level: 3                   # 이번 학습 목표 레벨 (1-6)
bloom_achieved_max: 4            # 누적 도달 최고 레벨
prerequisites:
  - claude-code/basics
  - claude-code/settings-hierarchy
weakness_tags:
  - "#tech/용어혼동"
references:
  - url: https://docs.claude.com/...
    note: "Skills 공식 문서"
    lines: "L100-L120"
session_modes_used: [B, C]       # Step 2에서 사용한 모드 누적
quick_explain_only: false        # Quick Explain만 했는지
created: 2026-02-21
updated: 2026-05-14
---
```

### 필드 규칙
- `concept_id`: 디렉토리 경로 그대로 (`{대주제}/{소주제}`)
- `domain`: 4분류 중 하나, 필수
- `bloom_level`: 1=Remember, 2=Understand, 3=Apply, 4=Analyze, 5=Evaluate, 6=Create
- `prerequisites`: 선행 concept_id 목록 (없으면 빈 배열 또는 생략)
- `weakness_tags`: 이 개념 학습 중 발견된 약점 태그
- `references`: 공식 문서 등 참고 자료. `lines` 필드는 줄 범위 가능 시 포함
- `session_modes_used`: 이 개념을 학습할 때 사용된 Step 2 모드 (중복 제거)

## 5. meta/{개념}.json (동적 메타: FSRS + 자신감)

```json
{
  "concept_id": "claude-code/rules-vs-skills",
  "fsrs": {
    "stability": 4.8,
    "difficulty": 0.32,
    "last_review": "2026-05-14",
    "next_due": "2026-05-19",
    "reps": 3,
    "lapses": 0,
    "state": "review"
  },
  "confidence_history": [
    {"date": "2026-02-21", "predicted": 0.70, "actual": 1.00, "delta": 0.30},
    {"date": "2026-05-14", "predicted": 0.90, "actual": 0.75, "delta": -0.15}
  ],
  "bloom_history": [
    {"date": "2026-02-21", "target": 3, "correct_by_level": {"1":1,"2":1,"3":1,"4":1}},
    {"date": "2026-05-14", "target": 4, "correct_by_level": {"3":1,"4":0,"5":1,"6":0}}
  ]
}
```

### 위치
- 경로: `{대주제}/{소주제}/meta/{개념}.json`
- concepts/{개념}.md와 같은 디렉토리 안의 `meta/` 하위
- 옵시디언 export 대상에서 제외 (Codex 측은 옵시디언 export 미제공이므로 N/A)

### 필드 규칙
- `fsrs.state`: `new` | `learning` | `review` | `relearning`
- `confidence_history.predicted`: Quiz 시작 시 사용자가 입력한 자신감 (0.0~1.0)
- `confidence_history.actual`: 실제 정답률 (맞은 문항 수 / 4)
- `confidence_history.delta`: predicted - actual
- `bloom_history.correct_by_level`: 각 Bloom 레벨에서 맞은 문항 수
- 상세 FSRS 공식은 `guides/fsrs.md` 참조

## 6. log/review-queue.md (신규 데이터)

```markdown
# Review Queue
최종 업데이트: 2026-05-14

## Due Today (2026-05-14)
- claude-code/rules-vs-skills — 2026-05-14 마감, stability 4.8

## Due This Week
- ai-ml/next-token-prediction — 2026-05-17, stability 7.2

## Upcoming
- software-testing/mc-dc — 2026-06-02, stability 12.4
```

- 스킬이 세션 종료 시 자동 갱신 (Codex는 사용자 명시 요청 시만)
- Step 0에서 학습 모드 진입 시 자동 Read
- 일일 1회 사용자 알림 캡 (같은 날 두 번째 세션은 알림 스킵)

## 7. log/history.md 확장 컬럼

기존 컬럼 유지 + 다음 추가:

```markdown
## 2026-05-14 | claude-code > rules-vs-skills | domain=tech | bloom_target=4

- 학습 내용: ...
- 퀴즈 결과: 3/4
  - 레벨별 정답률: L3=1/1, L4=0/1, L5=1/1, L6=1/1
- 자신감 예측: 0.90 / 실제 정답률: 0.75 / 오차: -0.15 → #meta/과신 후보
- 커버리지: 실습 80% / 퀴즈 100% / 총 90% (누적 2사이클)
- FSRS: stability 4.8→6.1, next_due 2026-05-19
- 약점 태그: #tech/용어혼동 (해소 카운트 2/3), #meta/과신 (신규)
- 글로서리 추가: [SKILL.md], [allowed-tools]
- 추천 다음 주제: 1) claude-code/hooks 2) claude-code/agent-teams
```

## 8. 마이그레이션 (v1 → v2)

상세: `guides/migration-v1-to-v2.md`

요지:
- frontmatter 없는 기존 concepts 파일은 **lazy backfill** — 해당 주제 재학습 시 자동 보강
- 기존 weakness.md 태그(`#용어혼동` 등)는 `#tech/` prefix 일괄 추가 (1회성, 사용자 승인 후)
- 기존 history.md 항목은 그대로 두고 v2 항목부터 새 포맷 적용
