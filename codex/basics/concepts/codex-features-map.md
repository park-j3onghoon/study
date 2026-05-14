# Codex 기능 지도 (Claude Code 비교)

기준일: 2026-02-21
로컬 확인 버전: `codex-cli 0.104.0`

## 한 줄 요약
Codex는 "로컬 에이전트 + 클라우드 태스크 + 확장(MCP/Skills/SDK) + 협업 통합(GitHub/Slack/Linear)" 조합으로 동작한다.

## 큰 그림
```text
[대화형 작업]
  codex (CLI/TUI)
      |
      +-- AGENTS.md / Rules / Permissions
      +-- Skills / MCP / Slash commands
      +-- Resume / Fork / Review
      |
[자동화]
  codex exec / codex review / Codex SDK
      |
[원격 위임]
  codex cloud exec -> status/diff -> apply
      |
[협업 통합]
  GitHub / Slack / Linear
```

## Claude Code와 대응되는 핵심 기능
1. 스킬 (Claude Skills 유사)
   - Codex도 `SKILL.md` 기반 Agent Skills를 지원한다.
   - 명시 호출(`$skill`, `/skills`) + 암시 호출(설명 매칭) 둘 다 가능하다.
   - 스킬은 `SKILL.md` + 선택 리소스(`scripts/`, `references/`, `assets/`) 구조다.

2. 프로젝트 지침 (CLAUDE.md/지침 파일 유사)
   - Codex는 `AGENTS.md`를 계층적으로 읽는다.
   - 전역(`~/.codex/AGENTS.md`) + 저장소 루트 + 하위 경로 오버라이드(`AGENTS.override.md`)를 병합한다.
   - 현재 경로에 가까운 지침이 뒤에서 덮어쓴다.

3. 권한/안전 제어 (승인 모드 유사)
   - 샌드박스: `read-only`, `workspace-write`, `danger-full-access`
   - 승인 정책: `untrusted`, `on-request`, `never` 등
   - Rules(`.rules`, Starlark)로 "샌드박스 밖 명령" 허용/차단 정책을 세밀 제어 가능

4. 도구 확장 (외부 툴 연동 유사)
   - MCP 서버를 `codex mcp add/list/get/remove/login/logout`로 관리
   - `config.toml` 기반으로 서버별 timeout/required/enabled_tools/disabled_tools 설정 가능
   - IDE extension과 CLI가 MCP 설정을 공유한다.

5. 멀티 에이전트 (병렬 에이전트 유사)
   - Multi-agent는 실험 기능이며 활성화 후 사용
   - 병렬 서브에이전트를 띄워 결과를 합친다.
   - 서브에이전트는 현재 샌드박스를 상속하며, 추가 승인 필요 작업은 실패 후 부모 워크플로우에 에러로 보고된다.

6. 세션 조작/운영 명령
   - `resume`, `fork`, `/new`, `/resume`, `/fork`, `/status`, `/compact`, `/diff`, `/review`, `/mcp`, `/agent` 등
   - 긴 세션 관리(컨텍스트 압축, 상태 점검, 스레드 전환)에 강하다.

7. 자동화/임베딩
   - 비대화형: `codex exec` (JSONL `--json`, 구조화 출력 `--output-schema`)
   - 코드리뷰 전용: `codex review`
   - SDK: `@openai/codex-sdk`로 앱/CI에 Codex 내장

8. 클라우드 위임 + 협업 통합
   - Cloud task: `codex cloud exec/status/diff/apply`
   - GitHub PR 코멘트 `@codex review`로 리뷰 요청
   - Slack에서 `@Codex`로 태스크 생성
   - Linear 이슈 assign/mention으로 태스크 위임

## 빠른 추천 사용 시나리오
1. 로컬 페어 프로그래밍: `codex`
2. 자동화 스크립트/CI: `codex exec --json ...`
3. 조직 확장: `AGENTS.md + Skills + MCP + Rules`
4. 비동기 위임: `codex cloud exec` + Slack/Linear/GitHub 통합

## Q&A

### Q1. "Claude Code의 스킬/에이전트 같은 기능이 Codex에도 있나?"
A. 있다. 대응 관계는 다음과 같다.
- Claude Skills <-> Codex Skills (`SKILL.md`)
- 프로젝트 지침 파일 <-> Codex `AGENTS.md` 계층
- 외부 도구 연동 <-> Codex MCP
- 에이전트 병렬 실행 <-> Codex Multi-agent(실험)
- 비동기 작업 위임 <-> Codex Cloud tasks
- 협업 연결 <-> GitHub/Slack/Linear 통합

## 참고 문서
- https://developers.openai.com/codex/cli
- https://developers.openai.com/codex/cli/slash-commands
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/mcp
- https://developers.openai.com/codex/multi-agent
- https://developers.openai.com/codex/noninteractive
- https://developers.openai.com/codex/sdk
- https://developers.openai.com/codex/integrations/github
- https://developers.openai.com/codex/integrations/slack
- https://developers.openai.com/codex/integrations/linear
