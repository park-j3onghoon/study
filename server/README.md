# Learning App (study v3) — Phase 1

브라우저 안에서 학습+채팅+문제풀이를 통합하는 로컬 학습 앱. 설계 문서: `~/plans/study/learning-app/plan.md`.

## Phase 1 범위 (현재)

- FastAPI 백엔드 스켈레톤
- Claude API + tool_use loop (동기 응답)
- 도구 자동 등록 시스템 (`app/tools/`)
- 시범 도구: `echo`
- `/api/health`, `/api/chat`

프론트엔드·SSE 스트리밍·학습지 생성 도구는 P2~P5에서.

## 셋업

```bash
cd ~/git/study/server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env 안의 ANTHROPIC_API_KEY를 본인 키로 채움
./start.sh
```

서버는 `http://127.0.0.1:9999` 에만 바인딩 (외부 노출 금지 — `ADR-4`).

## 검증

```bash
# health check
curl http://127.0.0.1:9999/api/health
# → {"status":"ok"}

# echo 도구 호출 (Claude API 키 필요)
curl -X POST http://127.0.0.1:9999/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"echo 도구로 hello 호출해줘"}]}'
```

## 새 도구 추가하는 법

`app/tools/` 에 파일 하나 만들면 자동 등록됩니다.

```python
# app/tools/my_tool.py
from typing import Any
from . import register_tool
from .base import Tool

@register_tool
class MyTool(Tool):
    name = "my_tool"
    description = "이 도구가 무엇을 하는지 Claude가 알도록 자세히 작성"
    input_schema = {
        "type": "object",
        "properties": {"x": {"type": "string"}},
        "required": ["x"],
    }
    async def execute(self, input: dict[str, Any]) -> str:
        return f"got: {input['x']}"
```

`app/tools/__init__.py` 가 디렉토리를 스캔해 자동 import → `@register_tool` 데코레이터가 실행됩니다.

## Phase 진행 상황

- ✅ P1: 백엔드 스켈레톤 (이 README 시점)
- ⏳ P2: 핵심 도구 (write_lesson, read_answers, grade, list_lessons)
- ⏳ P3: 프론트엔드 기본 (사이드바 + 학습지 뷰 + 동기 채팅)
- ⏳ P4: SSE 스트리밍 + 모델/effort UI
- ⏳ P5: 학습 흐름 E2E
- ⏳ P6: 라이브 인디케이터 + 파일 watch
- ⏳ P7: 채팅 히스토리 + 추가 학습지 자동 제안
