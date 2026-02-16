# Claude Code Agent Teams

학습일: 2026-02-16

## 핵심 개념

Agent Teams는 여러 개의 Claude Code 인스턴스가 팀처럼 협업하는 기능이다.
하나의 세션이 Team Lead 역할을 하고, 나머지는 Teammate로 독립적으로 작업하며,
공유 태스크 리스트와 메일박스 시스템으로 소통한다.

## 아키텍처

```
┌─────────────────────────────────────────────┐
│                  사용자 (You)                 │
│         Shift+Up/Down으로 팀원 선택           │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │    Team Lead       │  ← 메인 세션 (조율 담당)
         │  - 팀 생성/해체    │
         │  - 태스크 분배     │
         │  - 결과 종합       │
         └──┬──────┬──────┬──┘
            │      │      │     메일박스 (직접 소통)
     ┌──────▼┐  ┌──▼───┐  ┌▼──────┐
     │팀원 A │←→│팀원 B│←→│팀원 C │  ← 각각 독립 컨텍스트 윈도우
     │보안검토│  │성능분석│  │테스트  │
     └───┬───┘  └───┬──┘  └───┬───┘
         │          │          │
         └──────────┼──────────┘
              ┌─────▼─────┐
              │ 공유 태스크 │  ← 태스크 상태/의존성/소유권 관리
              │   리스트    │     ~/.claude/tasks/{team-name}/
              └───────────┘
```

## Subagent vs Agent Teams

| 구분 | Subagent | Agent Teams |
|------|----------|-------------|
| 컨텍스트 | 자체 윈도우, 결과만 호출자에게 반환 | 자체 윈도우, 완전 독립 |
| 소통 | 메인 에이전트에게만 보고 | 팀원끼리 직접 메시지 |
| 조율 | 메인 에이전트가 모든 작업 관리 | 공유 태스크 리스트로 자체 조율 |
| 적합한 경우 | 결과만 필요한 집중 작업 | 토론과 협업이 필요한 복잡한 작업 |
| 토큰 비용 | 낮음 (결과 요약만 반환) | 높음 (각 팀원이 별도 인스턴스) |

## 활성화 방법

settings.json에 추가:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## 디스플레이 모드

- **in-process**: 메인 터미널 내에서 모든 팀원 실행 (기본값)
- **split panes**: tmux/iTerm2로 각 팀원 별도 패널 (동시 출력 확인 가능)

## 주요 제한사항

- 실험적 기능 (experimental)
- 세션 재개 시 기존 팀원 복원 불가
- 세션당 1팀만 가능, 중첩 팀 불가
- 리드 변경 불가
- VS Code 통합 터미널에서 split pane 미지원

## 참고 문서

- [공식 문서 - Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Anthropic - Claude Code for Teams and Enterprise](https://www.anthropic.com/news/claude-code-on-team-and-enterprise)
- [TechCrunch - Opus 4.6 Agent Teams](https://techcrunch.com/2026/02/05/anthropic-releases-opus-4-6-with-new-agent-teams/)
