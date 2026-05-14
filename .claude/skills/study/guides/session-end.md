# 세션 종료 처리 규칙 (v2)

모든 사이클이 끝나면 아래를 순서대로 수행한다.

## 1. 학습 세션 요약 리포트

이번 세션의 모든 변경사항을 정리해서 보여준다:

```
━━━ 세션 요약 ━━━
날짜: {YYYY-MM-DD}
학습 주제: {대주제} > {소주제} (domain={...})
사이클: {N}회 수행, bloom_target={1-6}

[개념 설명]
- {설명한 개념 요약}

[Sketch]
- 다이어그램 타입: {flowchart|sequence|class|mindmap|state}

[실습]
- 모드: {A|B|C}, 수행 요약

[Feynman]
- 5문장 설명 결과 / follow-up 갭

[퀴즈 결과]
- 총 {맞은 수}/4 ({정답률}%)
- Bloom 레벨별: L1={x}, L2={x}, L3={x}, L4={x}
- 자신감 예측 {0.x} vs 실제 {0.x} = 오차 {±0.xx}

[Consolidate]
- Glossary 추가: {용어 N개}
- Anti-pattern: {개수}
- ADR: {유/무}

[Verify (선택)]
- 마이크로 프로젝트 또는 Pre-mortem 수행 여부

[커버리지]
- 실습: {X}% / 퀴즈: {X}% / 총: {X}%

[FSRS]
- stability {이전}→{이후}, next_due {YYYY-MM-DD}

[약점 태그 변동]
- 신규: #...
- 해소 카운트 변화: #... (n/3)

[파일 변경사항]
- 생성: {새로 만든 파일 목록}
- 수정: {수정한 파일 목록}

[추천 다음 주제]
- 1) ... 2) ... 3) ...
```

## 2. 학습 로그 기록

→ `guides/logging.md` 참조 (v2 확장 형식)

## 3. 교차 약점 분석

→ `guides/weakness.md` 참조 (17개 태그 + 도메인 가중치 + Bloom 해소 조건)

## 4. FSRS 업데이트 + review-queue.md 갱신

→ `guides/fsrs.md` 참조

1. 이번 세션 주제의 `meta/{개념}.json` 갱신 (stability, difficulty, last_review, next_due, reps, lapses, state)
2. `confidence_history`, `bloom_history`에 이번 세션 항목 append
3. 전체 concepts 스캔하여 `log/review-queue.md` 재정렬

## 5. 다음 주제 추천

`weakness.md` §"다음 주제 추천 알고리즘" 공식으로 상위 3개 계산 → 리포트에 포함.

## 6. 커밋 & 푸시

1. 변경된 파일들을 `git add` (학습 자료, 로그, meta/JSON 등; 특정 파일 명시. `-A` 사용 금지)
2. 커밋 메시지: `study: {대주제}/{소주제} - 사이클 {N}회 ({정답률}%, bloom L{target})`
3. `git push`까지 수행

## 7. 옵시디언 내보내기 (비동기)

→ `guides/obsidian-export.md` 참조

`concepts/{개념}.md` 파일을 옵시디언 Vault에 백그라운드로 내보낸다. `meta/{개념}.json`은 export 대상에서 제외. **현재 세션을 블로킹하지 않음** — Bash `run_in_background: true` 사용.

## 비고 — Consolidate 단계

Step 3.5 Consolidate(Glossary·Anti-pattern·ADR 생성)는 세션 종료가 아닌 **본 사이클 안의 단계**다. 세부 규칙은 `guides/consolidate.md` 참조. session-end에서는 Consolidate가 이미 끝난 상태로 가정한다.
