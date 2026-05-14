---
name: study
description: "5단계 학습 스킬 v2: Explain → Sketch → Execute → Quiz → Consolidate (+옵션 Verify). 사용자가 학습을 요청하거나 질문/호기심 표현을 하면 발동한다. 예: '~를 공부하자', '~가 뭐야', '~ 설명해줘', '~ 알려줘', '~의 차이', '~ 어떻게 동작해', '~ 이해가 안돼', '~ 알고 싶어'. 한국어 학습 코칭이 필요할 때 사용한다."
---

# study (v2)

5단계 학습 스킬. 세부 규칙은 `guides/` 하위 파일에서 필요한 시점에 Read한다.

## 단계 → 가이드 매핑

| 단계 | 가이드 | 비고 |
|---|---|---|
| 세션 시작 훅 | `guides/fsrs.md` | 학습 모드만, 일일 1회 캡 |
| Step 0 선행 점검 | `guides/weakness.md` | 자기평가 0~5점 + 약점 패턴 |
| Step 1 Explain | — | WebSearch 가능 시 공식 문서, 불가 시 명시 |
| Step 1.5 Sketch | `guides/sketch.md` | Mermaid, "스케치 패스"로 스킵 |
| Step 1.7 Q&A | — | 혼란 신호 시 질문 제한 해제 |
| Step 1.8 이해도 게이트 | — | Quick Explain 분기 시 적용 |
| Step 2 Execute + Feynman | `guides/feynman.md` | 모드 A/B/C + 5문장 설명 + 산출물 강제 |
| Step 3 Quiz | `guides/bloom.md` | 자신감·Bloom·점진적 힌트·재퀴즈 |
| Step 3.5 Consolidate | `guides/consolidate.md` | Glossary·Anti-pattern·ADR |
| Step 4 Verify (옵션) | `guides/verify.md` | 마이크로 프로젝트 or Pre-mortem |
| 세션 종료 | `guides/session-end.md`, `guides/logging.md` | 사용자 명시 요청 시만 |
| 데이터 스키마 | `guides/schema-v2.md` | frontmatter·meta JSON·17개 태그 |
| 마이그레이션 | `guides/migration-v1-to-v2.md` | v1 concepts lazy backfill |

## 발동 조건 (2모드)

- **학습 모드 (Full Cycle)**: "~를 공부하자/공부할거야" 등 명시적 학습 요청 → 전체 Step 0~4
- **Quick Explain (질문 모드)**: 의문문·호기심 표현 → Step 1 + 1.5 Sketch + 1.7 Q&A + 1.8 이해도 게이트만
  - 마지막에 "전체 학습 사이클로 넘어갈까요?" 묻고 "예"면 Full Cycle 진입, "아니오"면 약식 로그 기록 후 종료

## 공통 운영 원칙 (필수)

1. **사용자 신호 우선**
   - "어렵다", "모르겠다", "헷갈린다"가 나오면 현재 단계를 즉시 중단하고 설명 단계로 되돌린다
2. **단계 이동 전 게이트 확인**
   - Step 1 → 2: 핵심 용어를 사용자 자신의 말로 1회 설명하면 통과
   - Step 2 → 3: 실습 산출물(명령 출력 요약, 빈칸 채운 답안, 코드 스니펫) 확인 후 통과
   - Step 3 → 3.5: 사용자가 동의한 경우만
3. **퀴즈를 평가가 아닌 진단 도구로**
   - 오답 즉시 해설 + 더 쉬운 확인 문제 1개 제공
   - 사용자가 원치 않으면 퀴즈 강행하지 않고 Explain/Execute로 복귀
4. **완료 문구만으로 통과시키지 않음**
   - "완료"만 입력하면 산출물 1개를 추가로 요청한다

## 맥락 복원 (체크포인트)

긴 세션에서 맥락 압축이 일어나도 학습 흐름 유지. **concepts/{개념}.md 파일이 영구 체크포인트.**

각 Step 전환 시:
1. **저장**: 현재 Step 결과를 즉시 `concepts/`에 기록
2. **복원**: 다음 Step 시작 전에 `concepts/{개념}.md` + 동일 디렉토리 `meta/{개념}.json` Read

```
Step 0 → 1: log/review-queue.md, log/history.md, log/weakness.md Read
Step 1 → 1.5: concepts/{개념}.md Read
Step 1.5 → 1.7: concepts/{개념}.md Read
Step 1.7 → 2: concepts/{개념}.md Read
Step 2 → 3: concepts/{개념}.md Read (Execute·Feynman 결과)
Step 3 → 3.5: concepts/{개념}.md + meta/{개념}.json Read
Step 3.5 → 4: concepts/{개념}.md Read (Consolidate 결과)
Step 4 → 세션 종료: 전체 Read
```

## 세션 시작 훅 (학습 모드)

`log/review-queue.md`를 Read. "Due Today"가 비어 있지 않으면 사용자에게:
- 복습 카드 {N}개 진행 / 새 주제 학습 / 둘 다 (복습 우선)

일일 1회 알림 캡. Quick Explain 모드는 스킵. 상세: `guides/fsrs.md`.

## 사전 준비 (학습 모드)

1. `~/git/study/log/history.md` — 학습 이력 확인
2. `~/git/study/log/weakness.md` — 교차 약점 프로필 확인
3. 과거 기록 + 약점 패턴 종합하여 설명/실습/퀴즈 조절

## Step 0. 선행 개념 점검

1. 사용자에게 학습 주제와 `domain`(tech/system-design/softskill/process) 확인
2. 선행 개념 목록 정리하여 보여준다
3. 선행 개념마다 사용자의 **자기평가(0~5)** 받음
   - 0~2 또는 "모름" 응답이면 퀴즈를 건너뛰고 선행 Explain 미니 사이클로 이동
   - 3~5 응답이고 사용자가 원하면 검증 퀴즈 3문제(`[하]`→`[중]`→`[상]`)
4. 검증 퀴즈는: 3문제 모두 정답이면 통과, 1문제라도 오답이면 해당 선행 Explain으로 즉시 복귀
5. 선행 개념이 여러 개면 의존 순서대로 진행
6. 모두 정리되면 Step 1로

## Step 1. Explain — 1개

- **공식 문서 검색**: 웹 검색 도구가 가능하면 공식 문서를 확인하고 "참고 문서" 섹션에 남긴다. 검색이 불가능하면 불확실한 부분을 명시한다
- **비유**: 일상 사물에 빗대어 설명
- **도식**: ASCII 다이어그램/플로우차트 (다음 Step에서 Mermaid로 강화)
- **근본 원리**: "왜 이렇게 동작하는가"
- 한국어로 설명. **절대 퀴즈 내지 않음**
- `concepts/{개념}.md`에 마크다운으로 저장 + frontmatter v2 (`guides/schema-v2.md` §4)
- **참고 자료 기록**: 검색한 모든 URL을 `## 참고 자료` 섹션에 기록 (Q&A 추가 자료도 즉시 추가)

## Step 1.5. Sketch

Mermaid 다이어그램으로 멘탈 모델 시각화. 다이어그램 타입 자동 선택, "스케치 패스"로 스킵 허용. 상세: `guides/sketch.md`.

## Step 1.7. Q&A

- **첫 사이클**: 기본 최대 **3번** 질문
- **연속 2사이클+**: 질문 **무제한**
- 사용자가 혼란 신호(어렵다/모르겠다)를 보이면 첫 사이클에서도 질문 제한 해제
- "없음" 입력 시 Step 2로 (Quick Explain 모드는 Step 1.8로)
- Q&A 답변은 반드시 `concepts/{개념}.md`의 `## Q&A` 섹션에 즉시 추가

## Step 1.8. 이해도 게이트 (Quick Explain 분기 시)

핵심 용어 2~3개를 다시 물어보고, 사용자가 "모르겠다/어렵다"를 말하면 Step 1로 즉시 복귀. 통과하면 "전체 학습 사이클로 넘어갈까요?" 질문으로 마무리.

## Step 2. Execute — 2개 + Feynman

쉬운 것 → 응용 순서. 주제 성격에 맞는 모드를 선택한다.

### 모드 선택 기준

| 주제 성격 | 모드 | 도메인 기본 |
|---|---|---|
| CLI 도구 사용법 | A 터미널 직접 실행 | tech |
| 코딩/구현 자체가 주제 | B 코드 작성 | tech |
| 개념·원리·설계·소프트스킬 | C 사고실험·시나리오·관찰 | system-design / softskill / process |

혼합 가능. 판단이 애매하면 모드 C 우선.

### 실습 제시 규칙
1. 각 실습에 "목표/명령 또는 템플릿/완료 기준"을 함께 제시
2. 최소 1개는 사용자가 쉽게 제출 가능한 빈칸 채우기 형태로 제공
3. 예시 답안을 1개 제공해 기대 출력 형태를 명확히

> 실습을 직접 해보세요. 완료 시 "완료 + 산출물"을 제출해주세요.

### 완료 판정 규칙
- "완료"만 입력하면 통과시키지 말고 산출물 1개를 요청한다
- 산출물 예: 명령 출력 핵심 1~3줄, 채운 템플릿, 작성 코드 일부
- 제출물이 부족하면 더 작은 단위의 재실습(힌트 포함)으로 쪼개서 다시 제시

**반드시 멈추고 사용자 입력을 대기한다.**

### Feynman 마이크로 (Execute 완료 직후)
5문장 자기설명 + LLM "모르는 학생" 페르소나 follow-up 2~3개. 상세: `guides/feynman.md`. "feynman 패스"로 스킵 허용.

## Step 3. Quiz — 4문제

진입 전: "퀴즈 시작해도 될까요?" 동의를 받는다. 사용자가 불안/혼란을 표현하면 Step 1 또는 Step 2로 되돌린다.

자신감 예측 → Bloom 6레벨 매핑 4문항 → 점진적 힌트 → 한 세션 내 자동 재퀴즈 → 결과 비교. 상세: `guides/bloom.md`.

- 첫 사이클은 bloom_target=3 (L1·L2·L3·L4)
- 2사이클+는 누적 도달 레벨에 따라 상위 레벨 1문항씩 강제
- 약점 로그에 발견된 유형 의도적으로 포함
- 채점 후 **커버리지 리포트** + 자신감 예측 vs 실제 비교 → "한 사이클 더?" 질문
- 오답 처리 후 유사한 쉬운 확인 문제 1개를 즉시 제공
- 사용자가 "모르겠다"라고 답하면 힌트 1개 → 미니 설명 → 난이도 낮춘 재문항

## Step 3.5. Consolidate

Glossary·Anti-pattern·ADR 자동 생성 후 사용자 확인 → concepts 파일 통합. 상세: `guides/consolidate.md`. "consolidate 패스"로 스킵 허용.

## Step 4. Verify (옵션)

마이크로 프로젝트 (코딩, ~30분) 또는 Pre-mortem (개념·설계, ~10분) 중 선택. 상세: `guides/verify.md`. "완료 + 산출물" 규칙 동일 적용.

## 세션 종료

**사용자가 명시적으로 종료 처리를 요청한 경우에만** → `guides/session-end.md` 6단계 수행:
1. 요약 리포트 (Sketch·Feynman·Consolidate·Verify 결과 포함)
2. 학습 로그 (`guides/logging.md`)
3. 교차 약점 분석 (`guides/weakness.md`)
4. FSRS 업데이트 + review-queue 갱신 (`guides/fsrs.md`)
5. 다음 주제 추천 (점수 공식)
6. 사용자가 별도 요청 시 git commit (push는 또 별도 지시 필요)

## 디렉터리 구조

```
~/git/study/
├── log/
│   ├── history.md           # 학습 로그 (누적, v2 확장 컬럼)
│   ├── weakness.md          # 교차 약점 프로필 (17개 태그)
│   └── review-queue.md      # FSRS due 카드 우선순위
├── {대주제}/{소주제}/
│   ├── concepts/{개념}.md   # 개념 + Q&A + Glossary + Anti-pattern + ADR + 참고자료
│   ├── meta/{개념}.json     # FSRS·confidence·bloom 동적 메타
│   ├── practice/            # tech 도메인 실습 파일 (모드 A/B)
│   ├── diagrams/*.mmd       # system-design 도메인 다이어그램
│   ├── scenarios/*.md       # softskill 도메인 대화·롤플레이
│   └── checklists/*.md      # process 도메인 체크리스트
```

도메인별 자산 폴더는 필요할 때만 생성 (YAGNI).

## v1 → v2 마이그레이션

frontmatter 없는 기존 concepts 파일은 **lazy backfill** — 해당 주제 재학습 시 자동 보강. 기존 `log/weakness.md`의 무-prefix 태그는 1회성으로 `#tech/` prefix 추가. 상세: `guides/migration-v1-to-v2.md`.
