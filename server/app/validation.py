"""공통 입력 검증. 도구와 라우터가 모두 사용."""
import re

CONCEPT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def is_valid_concept_id(concept_id: str) -> bool:
    return bool(CONCEPT_ID_RE.match(concept_id))
