# verify — Step 4 검증 (옵트인, Codex)

Consolidate 직후 옵션 수행. 학습 내용을 외부 형태로 검증. 한 세션 내 30분 이내 완료 원칙.

## 트리거

Step 3.5 Consolidate 완료 후 사용자에게 묻는다:

> Step 4 Verify를 진행할까요?
> - 마이크로 프로젝트 (코딩 주제, 약 20~30분)
> - Pre-mortem (개념·설계 주제, 약 5~10분)
> - 건너뛰기 (세션 종료로)

사용자 선택에 따라 분기. Quick Explain 모드는 자동 스킵.

## 분기 1: 마이크로 프로젝트 (tech 주로)

학습한 개념을 작은 규모로 직접 구현한다.

### 스코프 규칙
- 30분 이내 완성 가능한 분량 (스킬이 사전 추정)
- 한 파일 50줄 이내 권장
- 외부 의존성 최소 (가능하면 표준 라이브러리만)

### 작성 위치
`{대주제}/{소주제}/practice/0X_verify_{슬러그}.{ext}` 또는 `mini-projects/{슬러그}/`

### 절차
1. 스킬이 요구사항 3~5줄 + TODO 스켈레톤 생성
2. 사용자가 직접 구현
3. 사용자가 "완료 + 산출물(코드 일부 또는 실행 결과 1~3줄)" 입력 시 검증
4. 의도와 다른 동작이면 디버깅 라운드 (최대 2회)
5. 정상 동작 확인 → 결과 요약을 concepts/{개념}.md의 `## Verify (마이크로 프로젝트)` 섹션에 기록

"완료"만 입력하면 통과시키지 않고 산출물을 1개 요청한다 (Codex의 산출물 강제 패턴).

### 시간 초과 시
- 30분 경과 시 현재까지 진행분 저장 + "다음 세션 todo로 이월할까요?" 확인
- 이월 시 `log/review-queue.md`의 "Upcoming"에 verify-pending으로 등록

## 분기 2: Pre-mortem (개념·system-design·softskill 주로)

"이 개념·설계가 망한다면 왜?"를 미리 상상하여 학습 사각지대를 드러낸다.

### 절차
1. 사용자에게 묻기: "방금 배운 내용을 실제 적용했더니 6개월 뒤 망했습니다. 왜 망했을까요? 3가지 원인을 적어보세요."
2. 사용자 답안 받기
3. 스킬이 검토하고 누락된 typical failure modes 1~2개 추가 제시
4. 각 원인에 대해 "그럼 어떻게 대비/감지하나요?" 후속 질문 1회
5. 결과를 concepts/{개념}.md의 `## Pre-mortem` 섹션에 기록

### 도메인별 typical failure modes 힌트
- `system-design`: 부하 폭증, 단일 장애점, 데이터 불일치, 보안 우회
- `softskill`: 의도 왜곡, 청자 가정 실패, 타이밍 실수, 톤 오해
- `tech`: 버전 호환성, 엣지 케이스 누락, 동시성 버그, 의존성 변경

### 저장 예시
```markdown
## Pre-mortem (2026-05-14)

### 가상 실패 시나리오
1. allowed-tools에 너무 광범위한 패턴 → 권한 누수
2. Skills 우선순위 잘못 → 잘못된 명령 발동
3. SKILL.md frontmatter 누락 → 스킬 미발동

### 대비책
1. 패턴은 가장 좁게. wildcard 사용 최소화
2. user-invocable과 description 확인 체크리스트
3. SKILL.md 작성 시 frontmatter 템플릿 사용
```

## 시간 캡

- 마이크로 프로젝트: 30분
- Pre-mortem: 10분
- 둘 다 초과 시 자동으로 "다음 세션 todo" 이월

## 학습 가치 회수

Verify에서 발견한 새 약점·갭은 즉시 weakness.md에 등록(`guides/weakness.md` 규칙 적용). FSRS stability에는 영향 없음 (Quiz가 stability 결정자).
