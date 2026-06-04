"""Phase 3 navigation — the postMessage trust boundary.

Two locks on the sender↔receiver contract, which is unsynchronized (one side is the
JS constant in static/js/navigation.js, the other is prose in config.py system_prompt
that the LLM reproduces into lesson_html):

1. The JS unit test (run under node) pins navigation.js's NAVIGATE_TYPE to the literal
   "navigate_lesson" — its valid case sends that exact type, so renaming the constant
   makes the valid case return null and the node run exits non-zero.
2. test_system_prompt_carries_navigation_contract pins the prompt to the same literal
   (and the safe targetOrigin). Drift on either side → a red test, not a silent dead button.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

from app.infrastructure.config import settings


_JS_UNIT_TEST = Path(__file__).resolve().parents[1] / "static" / "js" / "navigation.test.mjs"


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node not installed — navigation.js unit test skipped; install Node to run it",
)
def test_navigation_js_unit_passes():
    """Bridge the frameless node unit test for intendedConceptId into pytest."""
    result = subprocess.run(["node", str(_JS_UNIT_TEST)], capture_output=True, text=True)
    assert result.returncode == 0, (
        f"navigation.test.mjs failed (exit {result.returncode}):\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


def test_system_prompt_carries_navigation_contract():
    prompt = settings.system_prompt
    assert "navigate_lesson" in prompt, "system_prompt no longer names the message type — sender/receiver drift"
    assert "window.location.origin" in prompt, "system_prompt no longer specifies the safe targetOrigin"
    # Pin the data field name too: renaming the receiver's data.concept_id without the prompt
    # (or vice versa) is the most likely silent-dead-button drift; this turns it red.
    assert "concept_id" in prompt, "system_prompt no longer names the concept_id field — sender/receiver drift"
