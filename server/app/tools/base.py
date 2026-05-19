from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """모든 도구의 베이스 클래스. 서브클래스는 name·description·input_schema를 선언하고
    execute를 구현한다. execute는 string을 반환 — Claude가 그 결과를 다시 본다.
    """

    name: str
    description: str
    input_schema: dict

    @abstractmethod
    async def execute(self, input: dict[str, Any]) -> str:
        ...
