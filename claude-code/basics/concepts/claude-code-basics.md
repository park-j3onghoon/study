# Claude Code 기본

학습일: 2026-02-17

## 핵심 개념

Claude Code는 터미널에서 실행하는 AI 코딩 에이전트다.
자연어로 명령하면 파일 읽기/쓰기, 코드 실행, Git 작업 등을 자율적으로 수행한다.

## 구조: 3개의 핵심 레이어

```
┌─────────────────────────────────────────┐
│            사용자 (터미널)                │
│         $ claude "이 버그 고쳐줘"         │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────┐
    │     설정 레이어 (Config)      │
    │  ┌─────────────────────────┐ │
    │  │ CLAUDE.md    → 지시/맥락 │ │  "이 프로젝트는 TypeScript 씀"
    │  │ settings.json → 설정값   │ │  { "permissions": {...} }
    │  └─────────────────────────┘ │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │      도구 레이어 (Tools)      │
    │  Read, Edit, Write, Bash,   │
    │  Grep, Glob, WebSearch ...  │
    │  → 권한 시스템이 통제        │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │     모델 레이어 (LLM)        │
    │  Opus / Sonnet / Haiku      │
    │  → 실제 추론 엔진            │
    └─────────────────────────────┘
```

## CLAUDE.md vs settings.json

| 구분 | CLAUDE.md | settings.json |
|------|-----------|---------------|
| 형식 | 마크다운 (자연어) | JSON (구조화) |
| 용도 | 프로젝트 맥락, 코딩 규칙, 지시사항 | 권한, 환경변수, 도구 허용/차단 |
| 비유 | 신입에게 주는 온보딩 문서 | 회사 보안 정책/시스템 설정 |
| 예시 | "항상 TypeScript 사용" | `{ "permissions": { "deny": ["Read(.env)"] } }` |

## 설정 파일 계층 (우선순위 높은 순)

```
managed-settings.json   ← IT 관리자 강제 설정 (최우선)
    ↓
CLI 플래그              ← 실행 시 임시 설정 (--model 등)
    ↓
.claude/settings.local.json ← 나만의 프로젝트 설정 (gitignore)
    ↓
.claude/settings.json   ← 팀 공유 프로젝트 설정
    ↓
~/.claude/settings.json ← 나의 전역 설정 (최하위)
```

## 권한 시스템

```
deny  (차단) → 무조건 막힘
  ↓
ask   (확인) → 사용자에게 물어봄
  ↓
allow (허용) → 자동 실행
```

## 주요 CLI 명령어

| 명령어 | 설명 |
|--------|------|
| `claude` | 대화형 모드 시작 |
| `claude "query"` | 초기 프롬프트와 함께 시작 |
| `claude -p "query"` | 비대화형 모드 (출력 후 종료) |
| `claude -c` | 가장 최근 대화 이어하기 |
| `claude -r "세션명"` | 특정 세션 재개 |
| `claude update` | 최신 버전 업데이트 |
| `claude mcp` | MCP 서버 설정 |

## Q&A

### Q: "에이전트"가 뭔가? 일반 AI 챗봇이랑 뭐가 다른가?

챗봇은 **답변만** 하지만, 에이전트는 **도구를 써서 직접 행동**하는 AI다.

```
챗봇:    사용자 → "버그 고쳐줘" → AI: "이렇게 고치세요~" (말만 함)
에이전트: 사용자 → "버그 고쳐줘" → AI: 파일 읽기 → 원인 분석 → 코드 수정 → 테스트 실행 (직접 행동)
```

에이전트의 핵심 특징:
- **도구 사용**: Read, Edit, Bash 등을 직접 호출하여 실제 작업 수행
- **자율 판단**: "이 파일도 봐야겠다" 같이 다음 행동을 스스로 결정
- **연쇄 행동**: 한 번의 명령으로 여러 단계를 자동으로 이어서 수행

### Q: settings.json 계층 구조가 구체적으로 어떻게 동작하나?

회사에서 팀 프로젝트를 하는 예시:

```
1. IT 관리자 (managed-settings.json)  → ".env 파일 접근 금지!"
2. 내 전역 설정 (~/.claude/settings.json) → "opus 모델 사용"
3. 팀 공유 설정 (.claude/settings.json)   → "npm run test 자동 허용"
4. 나만의 설정 (.claude/settings.local.json) → "WebSearch 자동 허용"
```

충돌 시 규칙:
- `.env` 읽기 시도 → ✗ 차단 (1번 managed가 deny → 나머지 다 무시)
- 모델 선택 → opus (2번에서 정의, 위에서 안 건드림)
- 팀원 john의 WebSearch → 확인 필요 (4번은 teddy의 local이라 john에겐 미적용)

**핵심: 위에서 정한 건 아래에서 못 바꾸고, 같은 레벨이면 더 구체적인 게 이긴다**

### Q: Hooks로 학습 흐름(선행 개념 점검 등)을 자동 트리거할 수 있나?

안 된다. Hooks와 Skills는 역할이 다르다.

```
Hooks  → 도구(Tool) 레벨 이벤트에 반응 ("Bash가 실행됐다")
Skills → 사용자 의도에 반응 ("공부할거야")
```

Hooks가 할 수 있는 이벤트:
- PreToolUse: 도구 실행 전
- PostToolUse: 도구 실행 후
- Notification: 알림 발생 시
- Stop: 세션 종료 시

Hooks가 할 수 없는 것:
- 사용자 메시지 내용을 읽고 의도를 판단하는 것
- 따라서 학습 워크플로우 트리거는 Skill이 맞는 위치

### Q: Stop hook은 터미널을 강제 종료해도 실행되나?

안 된다. Stop hook은 **정상 종료** 시에만 동작한다.

```
Stop hook 동작 O (정상 종료):
  - /exit 입력
  - Ctrl+C 종료
  - claude -p 모드 작업 완료 후 자동 종료

Stop hook 동작 X (강제 종료):
  - 터미널 창 X로 닫기
  - kill -9 (프로세스 강제 킬)
  - 컴퓨터 꺼짐 / 크래시
```

프로세스가 죽으면 cleanup 코드를 실행할 기회 자체가 없다.
따라서 자동 커밋 같은 중요한 작업은 hook이 아니라 학습 사이클 종료 시점에 명시적으로 수행하는 게 안전하다.

### Q: SKILL.md가 길어지면 Claude Code가 내용을 빠뜨리나?

그렇다. "Lost in the Middle" 현상이 있어서 긴 문서의 중간 부분을 놓칠 수 있다.

```
~100줄:  거의 100% 다 따름
~300줄:  대부분 따르지만 세부사항 가끔 누락
~500줄+: 중간 부분 놓침 현상 발생
~1000줄+: 앞뒤만 잘 보고 중간 약해짐
```

해결책: 핵심 흐름만 메인 파일에 두고 (~100줄), 세부 규칙은 별도 파일로 분리.
필요한 시점에 Read 도구로 해당 파일만 가져온다.

## 참고 문서

- [공식 문서 - Settings](https://code.claude.com/docs/en/settings)
- [공식 문서 - CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [GitHub - claude-code](https://github.com/anthropics/claude-code)
