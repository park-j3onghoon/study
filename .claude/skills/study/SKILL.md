---
name: study
description: "5단계 학습 스킬 v2: Explain → Sketch → Execute → Quiz → Consolidate (+옵션 Verify). 사용자가 무언가를 물어보거나 학습을 요청하면 자동 발동. 발동 키워드: '~를 공부하자', '~가 뭐야', '~이 뭐야', '~ 설명해줘', '~ 알려줘', '~ 궁금해', '~의 차이', '~랑 ~랑 차이', '~ 어떻게 동작해', '~ 이해가 안돼', '~ 알고 싶어'. 주제 불문, 질문이나 호기심 표현이면 무조건 발동한다."
---

# study (v2)

5단계 학습 스킬. 세부 규칙은 `guides/` 하위 파일에서 필요한 시점에 Read한다.

## 단계 → 가이드 매핑

| 단계 | 가이드 | 비고 |
|---|---|---|
| 세션 시작 훅 | `guides/fsrs.md` | 학습 모드만, 일일 1회 캡 |
| Step 0 선행 점검 | `guides/weakness.md` | 약점·다음 주제 추천 |
| Step 1 Explain | — | 변경 없음 |
| Step 1.5 Sketch | `guides/sketch.md` | HTML 단일 파일, "스케치 패스"로 스킵 |
| Step 1.7 Q&A | — | 변경 없음 |
| Step 2 Execute + Feynman | `guides/feynman.md` | 모드 A/B/C + 5문장 설명 |
| Step 3 Quiz | `guides/bloom.md` | 자신감 예측·Bloom·점진적 힌트·재퀴즈 |
| Step 3.5 Consolidate | `guides/consolidate.md` | Glossary·Anti-pattern·ADR |
| Step 4 Verify (옵션) | `guides/verify.md` | 마이크로 프로젝트 or Pre-mortem |
| 세션 종료 | `guides/session-end.md`, `guides/logging.md`, `guides/obsidian-export.md` | FSRS 업데이트·다음 주제 추천 포함 |
| 데이터 스키마 | `guides/schema-v2.md` | frontmatter·meta JSON·17개 태그 |
| 마이그레이션 | `guides/migration-v1-to-v2.md` | v1 concepts lazy backfill |

## 발동 조건 (2모드)

- **학습 모드 (Full Cycle)**: "~를 공부하자/공부할거야" 등 명시적 학습 요청 → 전체 Step 0~4
- **Quick Explain (질문 모드)**: 의문문·호기심 표현 → Step 1 + 1.5 Sketch + 1.7 Q&A만, FSRS due 알림·Feynman·Quiz·Consolidate·Verify 스킵
  - 마지막에 "전체 학습 사이클로 넘어갈까요?" 묻고 "예"면 Full Cycle 진입

## 맥락 복원 (체크포인트)

긴 세션에서 맥락 압축이 일어나도 학습 흐름 유지. **concepts/{개념}.md 파일이 영구 체크포인트.**

각 Step 전환 시:
1. **저장**: 현재 Step 결과를 즉시 `concepts/`에 기록
2. **복원**: 다음 Step 시작 전에 `concepts/{개념}.md` + 동일 디렉토리 `meta/{개념}.json` Read

```
Step 0 → 1: log/review-queue.md, log/history.md, log/weakness.md Read
Step 1 → 1.5: concepts/{개념}.md Read
Step 1.5 → 1.7: concepts/{개념}.md + diagrams/{개념}.html Read
Step 1.7 → 2: concepts/{개념}.md (Q&A 반영분) Read
Step 2 → 3: concepts/{개념}.md (Execute·Feynman 결과) Read
Step 3 → 3.5: concepts/{개념}.md + meta/{개념}.json Read (채점 결과)
Step 3.5 → 4: concepts/{개념}.md (Consolidate 결과) Read
Step 4 → 세션 종료: concepts/{개념}.md + meta/{개념}.json + log/ Read
```

## 세션 시작 훅 (학습 모드)

`log/review-queue.md`를 Read. "Due Today"가 비어 있지 않으면 사용자에게:
- 복습 카드 {N}개 진행
- 새 주제 학습
- 둘 다 (복습 우선)

일일 1회 알림 캡. Quick Explain 모드는 스킵. 상세: `guides/fsrs.md`.

## Step 0. 선행 개념 점검

1. 학습 모드 첫 진입 시 `log/weakness.md`·`log/history.md`를 Read하여 활성 약점과 누적 도달 Bloom 레벨 확인
2. 사용자에게 학습 주제와 `domain`(tech/system-design/softskill/process) 확인 — 디렉토리 추정이 가능하면 추정값 제시
3. 선행 개념 목록 정리 → 각 선행 개념마다 **퀴즈 3문제**(하·중·상)로 검증
   - 3문제 모두 정답 → 통과
   - 1문제라도 오답 → 해당 선행 개념부터 전체 사이클
4. 모두 통과하면 Step 1로

## Step 1. Explain — 1개

- **공식 문서 검색**: WebSearch → WebFetch로 유효성 확인
- **비유**: 일상 사물에 빗대어 설명
- **도식**: ASCII 또는 (다음 Step에서 HTML 단일 파일로 강화될) 개요
- **근본 원리**: "왜 이렇게 동작하는가"
- 한국어로 설명. **절대 퀴즈 내지 않음**
- `concepts/{개념}.md`에 마크다운으로 저장 + frontmatter v2 (`guides/schema-v2.md` §4)
- **참고 자료 기록 필수** — concepts 파일 맨 아래 `## 참고 자료` 섹션:
  ```markdown
  ## 참고 자료

  - [문서 제목](URL) — 참고한 부분 한 줄 설명
  - [문서 제목](URL#L100-L120) — 줄 범위 가능하면 표시
  ```
  WebSearch/WebFetch로 찾은 모든 URL 기록. Q&A에서 추가 검색한 자료도 즉시 추가.

## Step 1.5. Sketch

단일 HTML 파일(외부 의존성 없는 인라인 SVG/CSS)로 멘탈 모델 시각화. 모바일·데스크탑 호환. "스케치 패스"로 스킵 허용. 상세: `guides/sketch.md`.

## Step 1.7. Q&A

- **첫 사이클**: 최대 **3번** 질문
- **연속 2사이클+**: 질문 **무제한**
- "없음" 입력 시 Step 2로
- Q&A 답변은 반드시 `concepts/{개념}.md`의 `## Q&A` 섹션에 즉시 추가

## Step 2. Execute — 2개 + Feynman

쉬운 것 → 응용 순서. 주제 성격에 맞는 모드를 선택한다.

### 모드 선택 기준

| 주제 성격 | 모드 | 도메인 기본 |
|---|---|---|
| CLI 도구 사용법 | A 터미널 직접 실행 | tech |
| 코딩/구현 자체가 주제 | B 코드 작성 | tech |
| 개념·원리·설계·소프트스킬 | C 사고실험·관찰·시나리오 | system-design / softskill / process |

혼합 가능. 판단이 애매하면 모드 C 우선.

### 모드별 절차

- **A**: 명령어를 직접 타이핑하고 결과 확인
- **B**: `practice/`에 스켈레톤 생성, TODO를 채워 실행
- **C**: 시나리오 예측 / 실제 관찰 / 비교 분석 / 오개념 판별 중 적절한 방식. AskUserQuestion으로 출제, 즉시 피드백

> 실습을 직접 해보세요! 완료되면 "완료"라고 입력해주세요.

**반드시 멈추고 "완료" 대기.** (모드 C는 AskUserQuestion 응답이 "완료" 역할을 대신함)

### Feynman 마이크로 (Execute 완료 직후)

5문장 자기설명 + LLM "모르는 학생" 페르소나 follow-up 2~3개. 상세: `guides/feynman.md`. "feynman 패스"로 스킵 허용.

## Step 3. Quiz — 4문제

자신감 예측 → Bloom 6레벨 매핑 4문항 → 점진적 힌트 → 한 세션 내 자동 재퀴즈 → 결과 비교. 상세: `guides/bloom.md`.

- 첫 사이클은 bloom_target=3 (L1·L2·L3·L4)
- 2사이클+는 누적 도달 레벨에 따라 상위 레벨 1문항씩 강제
- 약점 로그에 발견된 유형 의도적으로 포함
- 채점 후 **커버리지 리포트** + 자신감 예측 vs 실제 비교 → "한 사이클 더?" 질문

## Step 3.5. Consolidate

Glossary·Anti-pattern·ADR 자동 생성 후 사용자 확인 → concepts 파일 통합. 상세: `guides/consolidate.md`. "consolidate 패스"로 스킵 허용.

## Step 4. Verify (옵션)

마이크로 프로젝트 (코딩, ~30분) 또는 Pre-mortem (개념·설계, ~10분) 중 선택. 상세: `guides/verify.md`.

## 세션 종료

**학습 단위(사이클)의 종료와 채팅 세션의 종료는 별개다.** "다음 사이클에 X"는 X를 다음 학습 단위에서 한다는 뜻일 뿐, 지금 채팅을 끝내자는 신호가 아니다. 채팅 세션 종료 신호가 명확한 경우("이만 끝", "오늘은 여기까지", "세션 종료", "/clear 예정" 등)에만 아래 종료 처리에 진입한다. 모호하면 사용자에게 짧게 묻는다.

**사용자가 명시적으로 종료 처리를 요청한 경우에만** → `guides/session-end.md` 단계 수행:
1. 요약 리포트 (Sketch·Feynman·Consolidate·Verify 결과 포함)
2. 학습 로그 (`guides/logging.md`)
3. 교차 약점 분석 (`guides/weakness.md`)
4. FSRS 업데이트 + review-queue 갱신 (`guides/fsrs.md`)
5. 다음 주제 추천 (점수 공식)
6. **사용자가 별도 요청 시** git commit (push는 또 별도 지시 필요. force push 금지)
7. **사용자가 별도 요청 시** 옵시디언 비동기 export (`guides/obsidian-export.md`)

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
│   ├── diagrams/*.html      # 단일 파일 HTML 다이어그램 (모바일 호환, 인라인 SVG/CSS)
│   ├── scenarios/*.md       # softskill 도메인 대화·롤플레이
│   └── checklists/*.md      # process 도메인 체크리스트
```

도메인별 자산 폴더는 필요할 때만 생성 (YAGNI).

## v1 → v2 마이그레이션

frontmatter 없는 기존 concepts 파일은 **lazy backfill** — 해당 주제 재학습 시 자동 보강. 기존 `log/weakness.md`의 무-prefix 태그는 1회성으로 `#tech/` prefix 추가. 상세: `guides/migration-v1-to-v2.md`.
