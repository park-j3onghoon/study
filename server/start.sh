#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# localhost-only binding. Do not change host to 0.0.0.0 — see ADR-4 in plan.md.
exec uvicorn app.main:app --host 127.0.0.1 --port 9999 --reload
