# consolidate — Step 3.5 학습 통합 (Codex)

Quiz 채점 후 학습 내용을 정착시키는 단계. 세 가지 산출물을 자동 생성하여 concepts/{개념}.md에 통합. "consolidate 패스"로 스킵 가능.

## 생성물 1: Glossary (용어 사전)

이 세션에서 등장한 핵심 용어를 사전 형식으로 정리.

### 추출 규칙
- Step 1 Explain의 정의·도식에서 명사 키워드 추출
- Step 3 Quiz에서 문항·답안에 나온 전문 용어 포함
- 5~10개 목표 (너무 많으면 핵심만)

### 저장 위치
concepts/{개념}.md의 `## Glossary` 섹션 (없으면 신규 생성).

```markdown
## Glossary

| 용어 | 정의 | 첫 등장 위치 |
|---|---|---|
| Skills | LLM이 동적으로 로드하는 명령·지식 단위 | Step 1 정의 |
| allowed-tools | SKILL.md frontmatter에서 도구 화이트리스트 지정 필드 | Step 3 Q3 |
```

여러 세션이 누적되어도 같은 표에 행 추가 (중복은 갱신).

## 생성물 2: Anti-pattern (피해야 할 패턴)

이 주제에서 흔히 잘못하는 패턴을 1~3개 기록.

### 출처
- Step 2 Execute에서 사용자가 처음 시도하다 막힌 지점
- Step 3 Quiz에서 틀린 문항의 오답 원인
- Feynman follow-up에서 짚어낸 갭

### 저장 위치
concepts/{개념}.md의 `## Anti-patterns` 섹션.

```markdown
## Anti-patterns

### 1. user-invocable 필드에 트리거 키워드 작성
- 증상: 스킬이 발동되지 않음
- 원인: user-invocable은 boolean. 키워드는 description에 적어야 함
- 대안: description에 발동 키워드 명시
- 출처: 2026-02-21 사이클, Step 2 모드 B
```

## 생성물 3: ADR 한 문단 (왜 이 접근?)

이 개념을 학습한 이유 또는 선택한 접근의 정당화를 한 문단으로 기록.

### 형식 (간이 ADR)
```markdown
## ADR (학습 시점)

- **결정**: rules-vs-skills를 모드 B(코드 작성)로 학습
- **컨텍스트**: SKILL.md frontmatter 실제 작성 경험 필요
- **선택지**: 모드 A(터미널)만 했다면 frontmatter 문법 실수 발견이 어려웠을 것
- **결과**: 실습에서 닫는 괄호 누락 발견 → #tech/문법 약점 등록
- **재검토**: 2주 후 (next_due 2026-05-19) 동일 결정 재확인
```

ADR은 시점 기록이라 갱신하지 않음. 재학습 시 새 ADR 섹션을 시간순으로 추가.

## domain별 비중

| domain | Glossary | Anti-pattern | ADR |
|---|---|---|---|
| tech | 필수 | 권장 | 옵션 |
| system-design | 권장 | 권장 | 필수 |
| softskill | 옵션 | 필수 | 권장 |
| process | 권장 | 필수 | 옵션 |

## 진행 규칙

1. Quiz 채점 직후 자동 발동
2. 3개 생성물을 순차로 작성하며 사용자에게 한 번씩 확인 ("이 정리 맞나요?")
3. 수정 요청 시 즉시 반영
4. concepts/{개념}.md에 통합 저장
5. Step 4 Verify(옵션) 또는 세션 종료로 진행
