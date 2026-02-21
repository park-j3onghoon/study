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
