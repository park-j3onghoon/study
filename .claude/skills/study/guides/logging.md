# 학습 로그 규칙 (v2)

## 기록 위치

`~/git/study/log/history.md`에 누적 기록한다.

## 기록 형식

```markdown
## {YYYY-MM-DD} | {대주제} > {소주제} | domain={tech|system-design|softskill|process} | bloom_target={1-6}

- 학습 내용: {한 줄 요약}
- 퀴즈 결과: {맞은 수}/4
  - 레벨별 정답률: L1={x/n}, L2={x/n}, L3={x/n}, L4={x/n} (해당 레벨만)
- 자신감 예측: {0.0-1.0} / 실제 정답률: {0.0-1.0} / 오차: {±0.xx} → #meta/* 후보 표시
- 커버리지: 실습 {X}% / 퀴즈 {X}% / 총 {X}% (누적 {N}사이클)
- 틀린 문제:
  - Q{번호} [{난이도}·L{bloom}]: {문제 요약} → 오답: {선택한 답} / 정답: {올바른 답}
  - 오답 원인: {왜 틀렸는지 분석}
- FSRS: stability {이전}→{이후}, next_due {YYYY-MM-DD}
- 약점 태그: #{도메인}/{태그} (해소 카운트 {n}/3), ...
- 글로서리 추가: [{용어1}], [{용어2}], ...
- 추천 다음 주제: 1) {concept_id} 2) {concept_id} 3) {concept_id}
- 질문/혼란: {학습 중 사용자가 질문하거나 헷갈려한 부분}
- 남은 영역: {다루지 못한 세부 주제들}
```

Quick Explain 모드는 다음 약식 형식:

```markdown
## {YYYY-MM-DD} | {대주제} > {소주제} | Quick Explain only
- 설명: {한 줄}
- 질문 수: {n}회
- 추가 학습 의향: {예/아니오}
```

## 약점 태그

총 17개 — 상세 카탈로그는 `guides/schema-v2.md` §2 참조.

| domain | 태그 |
|---|---|
| tech | `#tech/용어혼동` `#tech/실행순서` `#tech/엣지케이스` `#tech/문법` `#tech/개념누락` `#tech/응용부족` |
| design | `#design/트레이드오프누락` `#design/스케일성무시` `#design/일관성결여` `#design/추상화레벨미스매치` |
| softskill | `#soft/의도전달부족` `#soft/구조화부족` `#soft/공감결여` `#soft/피드백톤` |
| meta | `#meta/과신` `#meta/저신` `#meta/일관성결여` |

새 패턴 발견 시 `schema-v2.md` 카탈로그에 추가 후 사용.

## Bloom 레벨별 정답률 산정

Quiz 4문항을 Bloom 레벨로 매핑한 뒤, 각 레벨에서 맞춘 문항 수를 기록. 같은 레벨에 2문항이 있을 수 있다 (예: L3=2/2). 점진적 힌트 후 맞춘 문항은 0.5점.

## 자신감 오차 처리

- |오차| ≥ 0.20 → 해당 방향 `#meta/과신` 또는 `#meta/저신` 후보로 마킹
- 같은 방향 3회 누적 시 weakness.md에 정식 등록
- 자세한 규칙은 `guides/weakness.md` 참조

## FSRS 업데이트

세션 종료 시점에 `meta/{개념}.json` 갱신 + `log/review-queue.md` 재정렬. 공식·전이 규칙은 `guides/fsrs.md` 참조.

## 활용

- 같은 주제 재학습 → 이전에 틀린 부분 + 같은 Bloom 레벨 집중
- 다른 주제 학습 → 약점 태그 패턴으로 설명 방식 조절 (`guides/weakness.md` 보완 전략 표)
- 자신감 오차 추이 → 메타인지 캘리브레이션 피드백
