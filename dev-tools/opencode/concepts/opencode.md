# OpenCode — 오픈소스 AI 코딩 에이전트

## 한 줄 요약

**터미널에서 돌아가는 오픈소스 AI 코딩 에이전트.** Claude Code의 오픈소스 대안으로, 75개 이상의 LLM을 지원하며 MIT 라이선스로 공개되어 있다.

> 참고: 원래 이름은 OpenCode였으나, 2025년 9월 **Crush**로 리브랜딩되었다. 현재 opencode.ai 사이트에서 계속 개발 중.

---

## 비유

**OpenCode = 만능 리모컨**

Claude Code가 "삼성 TV 전용 리모컨"이라면, OpenCode는 "어떤 TV든 연결 가능한 만능 리모컨"이다. Claude든 GPT든 Gemini든 로컬 Ollama든, 원하는 모델을 꽂아서 쓸 수 있다.

---

## 핵심 특징

```
┌─────────────────────────────────────────────────┐
│                   OpenCode                       │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  TUI     │  │   CLI    │  │  Desktop/IDE │  │
│  │(Bubble   │  │(파이프   │  │  (VSCode     │  │
│  │  Tea)    │  │ 연동)    │  │   확장)      │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│       │              │               │           │
│       └──────────┬───┘───────────────┘           │
│                  ▼                                │
│  ┌─────────────────────────────────────────┐     │
│  │         Core Engine (Go)                │     │
│  │  ┌────────┐ ┌─────┐ ┌───────────────┐  │     │
│  │  │ Tools  │ │ LSP │ │ Session Mgmt  │  │     │
│  │  └────────┘ └─────┘ └───────────────┘  │     │
│  └─────────────────┬───────────────────────┘     │
│                    ▼                              │
│  ┌─────────────────────────────────────────┐     │
│  │        LLM Provider Layer               │     │
│  │  Claude │ GPT │ Gemini │ Ollama │ ...   │     │
│  └─────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### 1. 멀티 모델 지원 (75+ 프로바이더)

| 프로바이더 | 예시 모델 |
|-----------|----------|
| Anthropic | Claude 3.5~4 Sonnet, Opus, Haiku |
| OpenAI | GPT-4, O1, O3, O4 시리즈 |
| Google | Gemini 2.0~2.5 |
| 로컬 | Ollama (완전 오프라인 가능) |
| 기타 | AWS Bedrock, Groq, Azure OpenAI, GitHub Copilot |

### 2. 듀얼 에이전트 모드

- **Build 모드** (기본): 파일 수정, 명령 실행 등 풀 액세스
- **Plan 모드**: 읽기 전용 — 분석과 코드 탐색용
- `Tab` 키로 전환

### 3. 클라이언트/서버 아키텍처

```
Claude Code:  CLI ──→ Anthropic API  (단순 직통)

OpenCode:     Client ──→ Server ──→ LLM Provider
              (TUI)     (Go)      (선택 가능)
                         │
                         ├── Docker 컨테이너 세션
                         ├── LSP 서버 통합
                         └── MCP 서버 확장
```

서버를 분리한 덕분에 Docker 안에서 세션을 돌리거나, 원격 서버에서 실행하는 것도 가능하다.

### 4. LSP 네이티브 통합

코드를 단순 텍스트로 읽는 게 아니라, Language Server Protocol로 **심볼 정보, 타입 정보, 참조 관계**를 이해한다. Rust, TypeScript, Python 등 다양한 언어 서버를 자동 감지·설정.

### 5. 주요 도구(Tools)

Claude Code와 비슷한 도구 세트를 제공:
- 파일 읽기/쓰기/편집
- 터미널 명령 실행
- 파일 검색 (glob/grep)
- `/undo`, `/redo` — 변경사항 되돌리기/다시하기
- `/share` — 대화 공유
- `@` — 파일 참조 (컨텍스트 추가)
- `/init` — 프로젝트 분석 후 `AGENTS.md` 생성

---

## Claude Code와의 비교

| 항목 | Claude Code | OpenCode |
|------|-------------|----------|
| **라이선스** | 독점 (Anthropic) | MIT 오픈소스 |
| **모델** | Claude 전용 | 75+ 프로바이더 |
| **로컬 모델** | 불가 | Ollama 지원 |
| **언어** | TypeScript/Node | **Go** |
| **UI** | 단순 CLI | Bubble Tea TUI (테마 지원) |
| **아키텍처** | 단일 프로세스 | 클라이언트/서버 분리 |
| **LSP** | 없음 (텍스트 기반) | 네이티브 LSP 통합 |
| **MCP** | 지원 | 지원 |
| **커뮤니티** | Anthropic 관리 | GitHub 95K+ 스타, 700+ 기여자 |
| **성향** | 빠른 속도 | 철저한 분석 |

### 왜 이런 차이가 생기나?

**Claude Code**는 Anthropic이 자사 모델 판매를 극대화하기 위해 만든 도구다. 따라서 Claude에 최적화된 프롬프트, 도구 체인, 워크플로우를 제공한다. "Apple 방식" — 닫힌 생태계지만 완성도가 높다.

**OpenCode**는 SST(Serverless Stack) 팀이 만든 커뮤니티 주도 프로젝트다. 어떤 모델이든 꽂아 쓸 수 있는 유연성이 핵심 가치. "Android 방식" — 열린 생태계, 커스터마이징 자유도.

---

## 설치

```bash
# macOS (Homebrew)
brew install opencode-ai/tap/opencode

# curl
curl -fsSL https://raw.githubusercontent.com/opencode-ai/opencode/refs/heads/main/install | bash

# Go
go install github.com/opencode-ai/opencode@latest
```

---

## 현재 상태 (2026년 2월)

- GitHub Stars: 95K+
- 월간 사용자: 250만+
- 2025년 9월: **Crush**로 리브랜딩 (Charmbracelet 팀)
- 2026년 1월: GitHub Copilot 공식 파트너십 — Copilot 구독자 직접 인증 지원
- 크로스 플랫폼: macOS, Linux, Windows, Android, FreeBSD, OpenBSD, NetBSD

---

## 참고 자료

- [GitHub - opencode-ai/opencode](https://github.com/opencode-ai/opencode) — 원본 저장소 (아카이브됨, Crush로 이전)
- [OpenCode 공식 사이트](https://opencode.ai/) — 공식 문서 및 다운로드
- [OpenCode Docs - Intro](https://opencode.ai/docs/) — 공식 문서: 아키텍처, 설정, 에이전트 구조
- [OpenCode vs Claude Code - Builder.io](https://www.builder.io/blog/opencode-vs-claude-code) — 상세 비교 분석 (성능 벤치마크 포함)
- [OpenCode: Open-source AI Coding Agent - InfoQ](https://www.infoq.com/news/2026/02/opencode-coding-agent/) — 2026년 2월 기사
- [Review of Crush (Ex-OpenCode) - The New Stack](https://thenewstack.io/terminal-user-interfaces-review-of-crush-ex-opencode-al/) — Crush 리브랜딩 후 리뷰
- [2026 Guide to Coding CLI Tools - Tembo](https://www.tembo.io/blog/coding-cli-tools-comparison) — 15개 AI CLI 도구 비교
