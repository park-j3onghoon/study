## 2026-02-21 | claude-code > rules-vs-skills

- 학습 내용: Rules(권한 시스템, settings.json)과 Skills(지식 확장, SKILL.md)의 차이, 파일 구조, 우선순위
- 퀴즈 결과: 4/4 (전체 정답)
- 커버리지: 실습 70% / 퀴즈 100% / 총 85% (누적 1사이클)
- 틀린 문제: 없음
- 남은 영역: Managed Rules 실습, allowed-tools 등 SKILL.md 고급 frontmatter, Hooks와의 연계
- 질문/혼란: 스킬 내부 rules/ 폴더와 Claude Code Rules 혼동 (→ guides/로 리네임하여 해소)
- 약점 태그: #용어혼동
  - 실습에서 `user-invocable`(boolean)에 트리거 키워드를 적음 — 필드 역할 혼동
  - 실습에서 `Bash(git commit *` 닫는 괄호 누락 — 문법 실수

## 2026-02-17 | claude-code > basics (선행 학습 — 미완료)

- 학습 내용: Claude Code 기본 구조, 설정 파일 체계, 권한 시스템, CLI 명령어
- 퀴즈 결과: 선행 점검만 수행 1/2 (본 퀴즈 미수행)
- 커버리지: 미산정 (사이클 미완료)
- 틀린 문제:
  - 선행 Q2 [중]: "프로젝트별 설정 파일은?" → 오답: CLAUDE.md / 정답: .claude/settings.json
  - 오답 원인: CLAUDE.md(맥락/지시)와 settings.json(설정값)의 역할을 혼동
- 남은 영역: 실습 미수행, 본 퀴즈 미수행, Subagent 개념 선행 점검 필요
- 질문/혼란: 에이전트 개념, settings.json 계층 구조, Hooks vs Skills 차이, SKILL.md 길이 제한
- 약점 태그: #용어혼동

### 이어갈 지점
1. Claude Code 기본 실습 2개 → 퀴즈 4문제
2. Subagent 선행 점검
3. Agent Teams 본 학습

## 2026-05-14 | system-design > rfc3986 | domain=system-design | bloom_target=3 (사이클 중도 보류)

- 학습 내용: RFC 3986 URI Generic Syntax + §4.2 Relative Reference. 약어(IETF/RFC/URI/URL/URN/ABNF) → 배경 → URI vs URL vs URN → 5컴포넌트 → URI Reference 분류 → §4.2 콜론 모호성
- 진행 단계: Step 0 → 1(Explain) → 1.5(HTML 단일 파일 시각화 5개) → 1.7(패스) → 2(Execute 모드 C) → [신호 받음 "뭔말인지 모르겠어"] → Step 1 단계별 재방문 + 작은 확인 5번 모두 통과 → Step 2 재진입(2문제, 둘 다 오답) → 사용자 요청으로 다음 그룹 전환
- Step 2 결과: 첫 묶음 2/4 (Q1 `42` 분류, Q3 `?fields=email` 끝 `/` 보존 오답), 응용 시나리오 0/2 (base path merge 끝 `/` 유무, `time:12-30` 콜론 모호성)
- 커버리지: 본문 100% / 실습 33% / 퀴즈 0% / 총 약 45% (1사이클 중도)
- FSRS: state=learning, stability=1.0, next_due=2026-05-16
- 약점 태그:
  - #tech/용어혼동 (출현 3회) — "콜론=scheme" + "절대 경로 vs 절대 URI" 혼동
  - #tech/엣지케이스 (신규, 출현 1회) — base path 끝 `/` 유무, path-empty 시 base path 보존
- 글로서리 추가 후보: [scheme], [authority], [Relative Reference], [path-noscheme], [dot-segment], [merge], [remove-dot-segments]
- 추천 다음 주제: 1) protobuf/oneof (그룹 사이클 다음) 2) protobuf/updating 3) protobuf/backwards-compat
- 비고: Quick Explain만 한 게 아니라 Step 2까지 갔으나 Quiz/Consolidate/Verify 패스. 다음 사이클에서 §4.2 콜론 모호성과 base path merge 재방문 권장.

### 이어갈 지점
1. RFC 3986 §4.2 콜론 모호성 응용 (`time:` scheme 오인 케이스) 재확인
2. base path 끝 `/` 유무에 따른 merge 차이 시나리오
3. Quiz 4문항(L1·L2·L3·L4) + Consolidate(Glossary·Anti-pattern·ADR)
4. system-design/rfc3986 사이클 종결 (Verify는 선택)

## 2026-05-18 | system-design > protobuf | domain=system-design | bloom_target=3 (Step 2까지, Quiz 패스)

- 학습 내용: Protobuf Oneof + Updating + Backwards Compatibility 통합 사이클. 약어/JSON 비교/기본 문법 → ⭐ 번호 vs 이름 → 필드 추가 호환 → 번호 재사용 위험 + reserved → Oneof → wire type 그룹 호환
- 진행 방식: **RFC 3986 회고 반영** — 본문 한꺼번에 폭포 X. 단계별 5섹션 짚기, 매 섹션마다 작은 확인 1문항. 본문은 사이클 끝나고 정리
- Step 결과: 작은 확인 4/5 통과
  - ① 번호 vs 이름 (1차 오답 → 본문 다시 짚어줌 → 재확인 정답)
  - ② 필드 추가 forward compat ✓
  - ③ reserved 키워드 목적 ✓
  - ④ Oneof 적용 시나리오 ✓
  - ⑤ int32 ↔ int64 호환 (오답: "컴파일러가 막을 거다" — protoc 호환성 검사 안 함 + wire type 같으면 호환 짚어줌)
- 커버리지: 본문 100% / 실습 90% / 퀴즈 0% / 총 약 65%
- FSRS: state=learning, stability=1.5, next_due=2026-05-21
- 약점 태그:
  - #tech/개념누락 (약함, 후보) — protoc가 호환성 자동 검사 안 한다는 점을 모름 (다른 컴파일 도구들에 대한 직관 적용)
- 추천 다음 주제: 1) aip/methods-130 2) aip/standard-methods-134 3) aip/standard-fields-148 (그룹 사이클)
- 비고: 단계별 짚기 방식이 흡수에 효과적. AIP 그룹도 동일 방식 적용 권장. Quiz/Consolidate/Verify 패스.

### 이어갈 지점
1. Protobuf Quiz 4문항 (다음 사이클)
2. wire type 그룹 매트릭스 응용 (혼합 케이스)
3. Oneof 호환성 깊이 (필드 이동 함정)
4. proto2 → proto3 마이그레이션 (선택)

## 2026-05-18 | system-design > aip-130-methods | domain=system-design | bloom_target=3 (선행 학습 — REST + AIP-130만)

- 학습 내용: REST API 기본(HTTP 메서드 5개 + 리소스 + URL 계층) + AIP-130 Methods(5개 표준 메서드 + Custom Method colon 표기). AIP는 RFC 3986 위에 쌓인 표준임을 짚음
- 진행 방식: 단계별 짚기 (RFC 3986 회고 반영, Protobuf 방식과 동일)
- Step 결과: 작은 확인 2/2 통과
  - ① 이메일만 수정 → PATCH /users/42 ✓
  - ② publish는 POST /posts/100:publish ✓ + 사용자가 "왜 1번 vs 3번?" 깊이 있는 질문 → Q&A로 흡수
- 사전 지식: 사용자는 REST API도 처음. 제로부터 짚었음
- 커버리지: 본문 100% / 실습 100% / 퀴즈 0% / 총 약 50%
- FSRS: state=learning, stability=1.5, next_due=2026-05-21
- 약점 태그: (이 사이클은 모두 통과, 새 약점 없음)
- 글로서리 추가 후보: [HTTP], [REST], [resource], [standard methods], [custom method], [colon notation]
- 추천 다음 주제: 1) aip/standard-fields-148 (공통 필드 이름) 2) aip/update-134 (PATCH의 세부) 3) aip/lro-151
- 비고: 사용자 결정 "AIP 9개 중 130만 깊이, 8개는 다음 세션". RFC 3986 + Protobuf + AIP-130 세 그룹 완료.

### 이어갈 지점
1. AIP 그룹 나머지 8개: 134 Update, 148 Standard fields, 151 LRO, 154 Freshness, 159 Reading across, 162 Revisions, 216 States, 217 Unreachable
2. AIP는 모두 RFC 3986 + Protobuf 위에 쌓인 표준이므로 두 선행은 안정적이어야 함
3. RFC 3986 + Protobuf Quiz도 다음 사이클에서 재방문 권장
