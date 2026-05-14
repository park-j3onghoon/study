# fsrs — 간격 반복 스케줄러 (Codex)

FSRS(Free Spaced Repetition Scheduler) 기반 누적 학습 큐. concepts마다 `meta/{개념}.json`에 상태 저장, `log/review-queue.md`로 집계.

Codex 측은 자동 git 커밋·푸시를 수행하지 않으므로 사용자가 종료 처리를 명시 요청할 때만 review-queue.md를 갱신한다.

## FSRS 핵심 변수

| 변수 | 의미 | 범위 |
|---|---|---|
| `stability` | 다음에 잊혀지기까지의 일수 (Retention 90% 기준) | 0.1~∞ |
| `difficulty` | 이 개념의 본질 난이도 | 0.0~1.0 |
| `retrievability` | 지금 시점에서 회상 가능성 | 0.0~1.0 |
| `state` | `new` / `learning` / `review` / `relearning` | enum |
| `reps` | 누적 복습 횟수 | int |
| `lapses` | 실패(잊음) 횟수 | int |

## 첫 학습 (state: new → learning)

```
stability = 1.0
difficulty = 0.5      # 중립값, 첫 Quiz 결과로 보정
last_review = 오늘
next_due = 오늘 + 1   # 첫 복습은 1일 뒤
reps = 1
lapses = 0
state = "learning"
```

## 복습 시 업데이트

세션 종료 시 Quiz 정답률에 따라 `state`를 결정하고 stability를 조정한다.

| 결과 | 다음 state | stability 변화 |
|---|---|---|
| 4/4 (완벽) | review | stability × (2.5 - difficulty) |
| 3/4 (양호) | review | stability × (1.5 - difficulty/2) |
| 2/4 (보통) | learning | stability × 1.0 (유지) |
| 0~1/4 (실패) | relearning | stability × 0.4, lapses += 1 |

`next_due = last_review + stability` (반올림, 최소 1일).

### difficulty 조정
- 4/4: difficulty −0.05
- 3/4: difficulty −0.02
- 2/4: difficulty +0.05
- 0~1/4: difficulty +0.15

0.0~1.0 클램프.

## review-queue.md 갱신

사용자가 세션 종료 처리를 요청하면 다음 순서로 갱신:
1. 모든 concepts 디렉토리를 스캔하여 `meta/{개념}.json` 로드
2. `next_due ≤ 오늘+7일`인 항목 추출
3. 다음 섹션으로 분류:
   - **Due Today**: `next_due ≤ 오늘`
   - **Due This Week**: `오늘 < next_due ≤ 오늘+7일`
   - **Upcoming**: `오늘+7일 < next_due ≤ 오늘+30일` (옵션)
4. 각 항목당 1줄: `- {concept_id} — {next_due} 마감, stability {value}`
5. 파일 상단 "최종 업데이트" 갱신

## Step 0 진입 시 동작 (학습 모드만)

1. `log/review-queue.md` Read
2. "Due Today" 섹션이 비어 있지 않으면 사용자에게:
   - 복습 카드 {N}개 진행 / 새 주제 학습 / 둘 다 (복습 우선) 중 선택
3. 일일 1회 알림 캡 — 같은 날 두 번째 세션은 자동 스킵

Quick Explain 모드는 이 단계 스킵.

## Interleaved review (옵트인)

- 5세션마다 또는 Due Today ≥3개일 때 사용자에게 제안
- 이전 3~5개 주제를 섞어 mixed quiz 출제
- 문항당 어느 주제인지 사용자가 먼저 식별 → 답 → 채점
- 모든 주제 사전 지식이 충분할 때만 권장

## meta/{개념}.json 미존재 시

frontmatter 없는 v1 concepts에 대해서는 `migration-v1-to-v2.md` 절차 적용. 마이그레이션 전엔 stability=0, state="new"로 가상 처리하여 review-queue에서는 제외.
