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
│   ├── anthropic_agent.py   # Agent 구현 (Anthropic SDK 직접 의존)
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
cp .env.example .env       # ANTHROPIC_API_KEY 채움
./start.sh                 # localhost:9999
```

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

- ✅ P1 백엔드 스켈레톤
- ✅ P2 핵심 도구 4개 + REST 라우터
- ✅ P3 프론트엔드 기본 (사이드바·학습지·채팅)
- ✅ P4 SSE 스트리밍 + thinking 인디케이터
- ✅ P5 클린 아키텍처 리팩토링 + iframe raw_html (same-origin)
- ⏳ P6 라이브 인디케이터 + 파일 watch
- ⏳ P7 채팅 히스토리 + 추가 학습지 자동 제안
