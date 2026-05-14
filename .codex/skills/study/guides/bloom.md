# bloom — Quiz v2 (Bloom·자신감·힌트·재퀴즈)

Step 3 Quiz를 Bloom Taxonomy 6레벨에 매핑하고, 자신감 예측·점진적 힌트·자동 재퀴즈를 결합한다.

Codex 측은 AskUserQuestion 없이 일반 대화로 진행한다. 자신감 예측·답안·힌트 응답은 모두 텍스트 입력으로 받는다.

## Bloom 6레벨

| 레벨 | 이름 | 동사 예시 | Quiz 문항 성격 |
|---|---|---|---|
| 1 | Remember | 정의하다, 나열하다 | 용어·정의 |
| 2 | Understand | 설명하다, 요약하다 | 작동 원리 |
| 3 | Apply | 적용하다, 사용하다 | 주어진 상황에 적용 |
| 4 | Analyze | 비교하다, 구분하다 | 차이·관계·구성 |
| 5 | Evaluate | 판단하다, 정당화하다 | 장단점·트레이드오프 |
| 6 | Create | 설계하다, 조합하다 | 새로운 설계·합성 |

## Quiz 4문항 매핑

기존 `[하/중/상/최상]` 라벨을 Bloom 레벨과 함께 표기.

### 첫 사이클 (bloom_level=3 목표)
- Q1 [하·L1 Remember]
- Q2 [중·L2 Understand]
- Q3 [상·L3 Apply]
- Q4 [최상·L4 Analyze]

### 2사이클+ (bloom_level=4 이상)
사용자의 누적 도달 레벨에 따라 상위 레벨 1문항씩 강제 포함.
- bloom_achieved_max=4 → Q4를 L5 Evaluate로
- bloom_achieved_max=5 → Q3=L4, Q4=L6 Create

domain별 추천 비중:
- `tech`: L1~L4 위주, L5~L6은 점진적
- `system-design`: L4 Analyze + L5 Evaluate 비중 ↑
- `softskill`: L5 Evaluate + L6 Create
- `process`: L3 Apply + L4 Analyze

## 자신감 예측 (Quiz 시작 시)

Quiz 4문항을 보여주기 **직전** 사용자에게 묻는다:

> 이번 퀴즈에서 예상 정답률은 어느 정도일까요? 0.0~1.0 사이 숫자로 답해주세요. (예: 0.75 = 4문항 중 3문항 정도 맞힐 것 같음)

저장: `meta/{개념}.json` confidence_history에 `{date, predicted, actual: 채점 후, delta}` append.

## Quiz 진입 전 동의 (Codex 고유)

- "퀴즈 시작해도 될까요?"를 먼저 묻고 동의받는다
- 사용자가 불안/혼란을 표현하면 Step 1 또는 Step 2로 되돌린다

## 점진적 힌트 (정답 즉시 노출 금지)

각 문항당 3단계:

1. **첫 시도**: 문제만 제시, 답안 받기
2. **오답 시 1차 힌트**: 핵심 개념 1줄 단서. "X 개념을 떠올려 보세요." 형식. 재시도 받기
3. **재오답 시 2차 힌트**: 정답에 더 가까운 단서 (구체적 조건 제시). 재시도 받기
4. **3번째 시도도 오답 또는 사용자가 "포기" 선언**: 정답 공개 + 해설

힌트 단계마다 채점은 **첫 시도 기준만 정답으로 카운트**. 힌트 후 맞춰도 "부분 정답"으로 표기 (정답률 0.5점).

사용자가 "모르겠다"라고 답하면: 힌트 1개 → 미니 설명 → 난이도 낮춘 재문항 순서로 진행 (Codex 고유 패턴 유지).

## 자동 재퀴즈 (한 세션 내)

4문항 채점 후 틀린 문항만 모아 마지막에 한 번 더.
- 같은 문항이 아니라 **같은 Bloom 레벨·같은 weakness 영역**의 변형 문항 출제
- 2회째도 틀리면 해당 weakness 태그에 가중치 1.5x로 등록 (schema-v2.md 약점 점수 계산식 참조)

## 종료 처리

1. 자신감 예측값 vs 실제 정답률 비교 출력
   ```
   예측: 0.75 / 실제: 0.5 / 오차: +0.25
   → #meta/과신 후보 (3회 누적 시 등록)
   ```
2. Bloom 레벨별 정답률 출력
3. `meta/{개념}.json` 갱신 (confidence_history, bloom_history)
4. session-end로 넘김

## Interleaved review 시 Quiz 변형

- 4문항 모두 Bloom 레벨 분산 유지
- 각 문항마다 어떤 주제인지 먼저 사용자가 식별 → 답 → 채점
- 식별 자체도 채점 대상 (틀린 식별은 0점)
