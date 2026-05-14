# MC/DC (Modified Condition/Decision Coverage)

## 한 줄 정의

**"복합 조건문의 각 개별 조건이, 다른 조건을 고정한 채, 혼자서 결과를 뒤집을 수 있음을 증명하는 테스트 커버리지 기준"**

## 왜 이게 필요한가?

비행기 소프트웨어에 이런 코드가 있다고 하자:

```python
if (엔진_정상 AND 연료_충분) OR 비상_오버라이드:
    계속_비행()
```

이 조건문에는 3개의 개별 조건이 있다. 단순히 "if문이 true/false 둘 다 나왔는가?"만 확인하면, **어떤 조건이 제대로 작동 안 해도 테스트를 통과**할 수 있다. 비행기가 떨어지면 안 되니까, 각 조건이 **독립적으로 결과에 영향을 주는지** 증명해야 한다.

## 비유: 전등 스위치

```
┌─────────────────────────────────────────────────┐
│  방에 전등이 켜지려면:                              │
│                                                   │
│  (스위치A AND 스위치B) OR 비상스위치C               │
│                                                   │
│  MC/DC가 요구하는 것:                               │
│  "스위치A만 끄면 전등이 꺼지나?" ← A의 독립적 영향   │
│  "스위치B만 끄면 전등이 꺼지나?" ← B의 독립적 영향   │
│  "비상스위치C만 켜면 전등이 켜지나?" ← C의 독립적 영향 │
└─────────────────────────────────────────────────┘
```

## 커버리지 계층 (아래로 갈수록 엄격)

```
┌──────────────────────────────────────────┐
│ Level 1: Statement Coverage              │  ← "이 줄을 실행했는가?"
│   if문 안의 코드가 한 번이라도 실행됨        │     DAL C 요구
├──────────────────────────────────────────┤
│ Level 2: Decision Coverage               │  ← "if문이 T/F 둘 다 나왔는가?"
│   if문 전체가 true도 되고 false도 됨        │     DAL B 요구
├──────────────────────────────────────────┤
│ Level 3: MC/DC                           │  ← "각 조건이 독립적으로 영향?"
│   개별 조건 하나하나가 결과를 뒤집음 증명     │     DAL A 요구 ★
├──────────────────────────────────────────┤
│ Level 4: Multiple Condition Coverage     │  ← "모든 조합 테스트"
│   2^N개 전수 조사 (실용적이지 않음)          │     어떤 표준도 요구 안 함
└──────────────────────────────────────────┘
```

## 구체적 예시: `(A AND B) OR C`

### 전체 진리표 (8가지)

| # | A | B | C | A AND B | (A AND B) OR C |
|---|---|---|---|---------|----------------|
| 1 | T | T | T |    T    |       T        |
| 2 | T | T | F |    T    |       T        |
| 3 | T | F | T |    F    |       T        |
| 4 | T | F | F |    F    |       F        |
| 5 | F | T | T |    F    |       T        |
| 6 | F | T | F |    F    |       F        |
| 7 | F | F | T |    F    |       T        |
| 8 | F | F | F |    F    |       F        |

### MC/DC 독립 쌍 찾기

**조건 A의 독립적 영향** — A만 바꾸고 B, C 고정:

```
#2: A=T, B=T, C=F → T
#6: A=F, B=T, C=F → F   ← A만 바꿨더니 결과가 뒤집혔다!  ✓
```

**조건 B의 독립적 영향** — B만 바꾸고 A, C 고정:

```
#2: A=T, B=T, C=F → T
#4: A=T, B=F, C=F → F   ← B만 바꿨더니 결과가 뒤집혔다!  ✓
```

**조건 C의 독립적 영향** — C만 바꾸고 A, B 고정:

```
#4: A=T, B=F, C=F → F
#3: A=T, B=F, C=T → T   ← C만 바꿨더니 결과가 뒤집혔다!  ✓
```

### 최종 테스트 셋: 4개 (N+1 = 3+1)

| 테스트 | A | B | C | 결과 | 역할 |
|--------|---|---|---|------|------|
| #2     | T | T | F | T    | A, B 독립성 증명의 기준점 |
| #3     | T | F | T | T    | C 독립성 증명 |
| #4     | T | F | F | F    | B, C 독립성 증명 |
| #6     | F | T | F | F    | A 독립성 증명 |

8개 전수 조사 대신 **4개만으로 100% MC/DC 달성!**

## 핵심 공식: 테스트 수 = N+1

| 조건 수(N) | 전수 조사(2^N) | MC/DC(N+1) | 절감률 |
|-----------|---------------|------------|--------|
| 3         | 8             | 4          | 50%    |
| 5         | 32            | 6          | 81%    |
| 10        | 1,024         | 11         | 99%    |
| 16        | 65,536        | 17         | 99.97% |

조건이 많아질수록 MC/DC의 효율이 폭발적으로 증가한다.

## DO-178과 소프트웨어 레벨

DO-178B/C는 항공 소프트웨어를 **고장 시 영향**에 따라 5단계로 나눈다:

```
DAL A (Catastrophic)  ── 고장 → 추락 가능        ── MC/DC 100% 필수
DAL B (Hazardous)     ── 고장 → 심각한 위험       ── Decision Coverage 필수
DAL C (Major)         ── 고장 → 상당한 영향       ── Statement Coverage 필수
DAL D (Minor)         ── 고장 → 경미한 영향       ── 구조적 커버리지 불필요
DAL E (No Effect)     ── 고장 → 영향 없음         ── 소프트웨어 검증 불필요
```

## Q&A

### Q1. "결국 전수 조사하는 거 아닌가?"

아니다. MC/DC는 전수 조사(MCC)가 **아니라** 그 대안이다.

- **전수 조사 (MCC)**: 진리표의 모든 행을 테스트 → 2^N개
- **MC/DC**: 진리표에서 "독립 쌍"이 되는 행만 선별 → N+1개

조건 16개일 때: MCC는 65,536개, MC/DC는 17개. 비행기 소프트웨어에 조건 16개짜리 if문이 있으면 전수 조사는 비현실적이지만, MC/DC는 실용적이다.

### Q2. "변수를 바꿔도 결과가 같으면 동일한 거 아닌가?"

MC/DC에서 **결과가 안 바뀌는 쌍은 쓸모없다.** MC/DC가 요구하는 건:

```
"조건 X만 바꿨을 때 결과가 반드시 뒤집혀야 한다"
```

결과가 같으면 그 조건은 해당 상황에서 결과에 영향을 주지 않는 것이므로, "독립적 영향" 증명에 사용할 수 없다. 만약 어떤 조건이 **어떤 상황에서도** 결과를 안 바꾼다면, 그 조건은 죽은 코드(dead code)이거나 로직에 오류가 있다는 신호다.

## MC/DC의 세 가지 형태

DO-178B 원문은 MC/DC를 하나로 정의했지만, FAA 해석 문서에서 세 가지 변형이 인정된다:

1. **Unique-Cause MC/DC**: 가장 엄격. 독립 쌍에서 해당 조건만 값이 바뀌어야 함 (위 예시가 이것)
2. **Unique-Cause + Masking MC/DC**: 강결합(coupled) 조건에서 마스킹 허용
3. **Masking MC/DC**: 가장 유연. 다른 조건이 바뀌어도 결과에 영향이 마스킹되면 허용

## 참고 자료

- [Modified condition/decision coverage - Wikipedia](https://en.wikipedia.org/wiki/Modified_condition/decision_coverage) — MC/DC 정의, 진리표 예시, DO-178 연관 설명
- [MC/DC Coverage - Rapita Systems](https://www.rapitasystems.com/mcdc-coverage) — MC/DC와 다른 커버리지 차이, 커피 비유 예시
- [MC/DC Explained - Keploy Blog](https://keploy.io/blog/community/modified-condition-decision-coverage) — 안전 밸브 예시, 독립 쌍 찾기 실습
- [MC/DC Technique - trendig](https://trendig.com/en/blog/mcdc-technique/) — N+1 공식, AND/OR 규칙 적용법
- [A Practical Tutorial on MC/DC - NASA](https://shemesh.larc.nasa.gov/fm/papers/Hayhurst-2001-tm210876-MCDC.pdf) — MC/DC 세 가지 형태 정의 (NASA 기술 문서)
- [An Investigation of Three Forms of MC/DC - FAA](https://www.faa.gov/sites/faa.gov/files/aircraft/air_cert/design_approvals/air_software/AR-01-18_MCDC.pdf) — Unique-Cause, Masking 변형 비교 (FAA 공식 보고서)
- [DO-178C Structural Coverage Analysis - LDRA](https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/) — DAL별 구조적 커버리지 요구사항
- [RTCA DO-178B 원문 - StudyLib](https://studylib.net/doc/27132454/rtca-do-178b) — 사용자 제공 원문 문서 (접근 제한)
