# Learning App (study v3)

브라우저 안에서 학습 + 채팅 + 문제풀이를 통합하는 로컬 학습 앱. 설계 문서: `~/plans/study/learning-app/plan.md`.

## 아키텍처 (Clean Architecture + Cosmic Python)

```
app/
├── domain/              # 순수 도메인 — 외부 의존 0
│   ├── models.py            # ConceptId, Lesson, Question, Answers, Result, LessonSummary
│   ├── ports.py             # LessonRepository, Agent, Tool (ABC)
│   └── exceptions.py        # DomainException, InvalidConceptId, LessonNotFound
├── application/         # use case — domain만 의존
│   ├── lesson_service.py    # CQS (Commands: create/save_*; Queries: list_*/get/find_*)
│   └── chat_service.py
├── adapters/            # 외부 시스템 — domain 의존
│   ├── disk_repository.py   # LessonRepository 구현
│   ├── claude_sdk_agent.py   # Agent 구현 (claude-agent-sdk / Claude Max OAuth)
│   └── tools/               # 각 Tool은 lesson_service에 위임
├── interface/           # FastAPI 라우터 + DTO
│   ├── routes/{chat,lessons}.py
│   └── schemas.py
└── infrastructure/      # 컴포지션 루트
    ├── config.py
    └── bootstrap.py         # 모든 wiring이 한 곳에
```

**의존성 방향**: `infrastructure → interface → application → domain ← adapters`

도메인은 안쪽이라 외부 import 없음. adapters는 도메인이 선언한 ABC를 구현. interface는 application service만 호출. infrastructure가 모든 것을 build.

## 셋업

```bash
cd ~/git/study/server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Claude Max(OAuth)로 동작 — API 키 불필요.
# 그 머신에 Claude Code CLI(claude)가 설치+로그인돼 있어야 한다
# (claude-agent-sdk가 claude CLI를 서브프로세스로 실행).
claude login               # Max 구독 OAuth 로그인

./start.sh                 # localhost:9999
```

> **인증**: `main.py`가 시작 시 `ANTHROPIC_API_KEY`를 pop하여 API 키 결제 경로를 끊고 **Claude Max OAuth**를 강제한다. `.env`는 선택(없어도 `config.py` 기본값으로 동작). 새 머신은 `pip install` + `claude login`이면 충분하다.

## 새 도구 추가하기

1. `app/adapters/tools/my_tool.py`:
   ```python
   from typing import Any
   from ...application.lesson_service import LessonService
   from ...domain.ports import Tool

   class MyTool(Tool):
       name = "my_tool"
       description = "Claude가 언제 이 도구를 쓸지 알도록 자세히."
       input_schema = {"type": "object", "properties": {...}, "required": [...]}

       def __init__(self, service: LessonService):
           self.service = service

       async def execute(self, input: dict[str, Any]) -> str:
           ...
   ```

2. `app/infrastructure/bootstrap.py`의 `build()` 안 `tools` 리스트에 추가:
   ```python
   from ..adapters.tools.my_tool import MyTool
   ...
   tools = [..., MyTool(lesson_service)]
   ```

명시적 wiring (composition root). 자동 등록 디렉토리 스캔은 단방향 의존성과 충돌해서 제거했다.

## API

| Method | Path | 역할 |
|---|---|---|
| GET | `/api/health` | 헬스 체크 |
| POST | `/api/chat` | SSE 스트리밍 (text_delta, thinking_*, tool_use_*, message_stop, error) |
| GET | `/api/lessons` | 학습지 목록 (사이드바) |
| GET | `/api/lessons/{id}` | 메타 + lesson_html |
| GET | `/api/lessons/{id}/raw_html` | 학습지 HTML (iframe src용, same-origin) |
| POST | `/api/lessons/{id}/answers` | 답 저장 |
| GET | `/api/lessons/{id}/result` | 채점 결과 |

## Phase 진행 상황

- ✅ P1~P7 백엔드·프론트·SSE·클린 아키텍처·채팅 히스토리
- ✅ P8 아키텍처 문서화 + pytest
- ✅ P9 모델 자동 fetch → P10에서 StaticModelCatalog로 전환
- ✅ P10 claude-agent-sdk 마이그레이션 (Anthropic API 키 → **Claude Max OAuth**)
- ✅ 퀴즈 8~12문항 증량, chat 하단 재배치 (UI 개편)
- ⏳ Focus 모드 / 학습 완료 신호
