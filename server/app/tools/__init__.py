"""도구 자동 등록. 이 디렉토리에 파일 하나만 만들면 @register_tool 데코레이터로 자동 등록된다."""
import importlib
import pkgutil

from .base import Tool

_registry: list[Tool] = []


def register_tool(cls):
    _registry.append(cls())
    return cls


def get_all_tools() -> list[Tool]:
    return list(_registry)


def get_tool_schemas() -> list[dict]:
    return [
        {"name": t.name, "description": t.description, "input_schema": t.input_schema}
        for t in _registry
    ]


def find_tool(name: str) -> Tool | None:
    return next((t for t in _registry if t.name == name), None)


# 이 패키지 안의 모든 모듈을 자동 import → @register_tool 데코레이터가 실행됨.
_skip = {"base"}
for _, _module_name, _is_pkg in pkgutil.iter_modules(__path__):
    if _module_name in _skip or _is_pkg:
        continue
    importlib.import_module(f"{__name__}.{_module_name}")
