#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run-spec-workflow.sh --spec-name <name> --module-path <path> [options]

Required:
  --spec-name NAME        Spec folder name. Reads: tmp/{NAME}/specs/*
  --module-path PATH      Module path passed to cw -m

Options:
  --session NAME          Workflow session name (default: spec-name)
  --quality-dir PATH      Quality docs directory (default: tmp/{spec-name}/quality)
  --multiplier N          Iteration multiplier for cw (default: 1.5)
  --model NAME            Codex model (default: gpt-5.3-codex)
  --reasoning-effort LVL  Reasoning effort (default: xhigh)
  --templates DIR         Custom cw templates directory
  --dry-run               Print commands without executing cw
  -h, --help              Show this help

Output artifacts:
  - tmp/{session}/workflow/spec-order.txt
  - tmp/{session}/workflow/workflow-state.env
  - tmp/{session}/workflow/{chunk}/phase00..phase19/status.md
  - tmp/{session}/workflow/{chunk}/summary.md
  - tmp/{session}/workflow/summary.md
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

SPEC_NAME=""
MODULE_PATH=""
SESSION_NAME=""
QUALITY_DIR=""
MULTIPLIER="1.5"
MODEL_NAME="gpt-5.3-codex"
REASONING_EFFORT="xhigh"
TEMPLATES_DIR=""
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spec-name)
      SPEC_NAME="${2:-}"
      shift 2
      ;;
    --module-path)
      MODULE_PATH="${2:-}"
      shift 2
      ;;
    --session)
      SESSION_NAME="${2:-}"
      shift 2
      ;;
    --quality-dir)
      QUALITY_DIR="${2:-}"
      shift 2
      ;;
    --multiplier)
      MULTIPLIER="${2:-}"
      shift 2
      ;;
    --model)
      MODEL_NAME="${2:-}"
      shift 2
      ;;
    --reasoning-effort)
      REASONING_EFFORT="${2:-}"
      shift 2
      ;;
    --templates)
      TEMPLATES_DIR="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "${SPEC_NAME}" || -z "${MODULE_PATH}" ]]; then
  echo "Both --spec-name and --module-path are required." >&2
  usage >&2
  exit 1
fi

if [[ -z "${SESSION_NAME}" ]]; then
  SESSION_NAME="${SPEC_NAME}"
fi

if [[ -z "${QUALITY_DIR}" ]]; then
  QUALITY_DIR="tmp/${SPEC_NAME}/quality"
fi

SPECS_DIR="tmp/${SPEC_NAME}/specs"
WORKFLOW_DIR="tmp/${SESSION_NAME}/workflow"
CW_SESSIONS_DIR="tmp/codex-workflow"
STATE_FILE="${WORKFLOW_DIR}/workflow-state.env"
ORDER_FILE="${WORKFLOW_DIR}/spec-order.txt"
SUMMARY_FILE="${WORKFLOW_DIR}/summary.md"

mkdir -p "${WORKFLOW_DIR}"

if ! command -v cw >/dev/null 2>&1; then
  echo "cw command not found. Install/link codex-workflow first." >&2
  exit 1
fi

if [[ ! -d "${SPECS_DIR}" ]]; then
  echo "Specs directory not found: ${SPECS_DIR}" >&2
  exit 1
fi

sort_paths() {
  if sort -V </dev/null >/dev/null 2>&1; then
    sort -V
  else
    sort
  fi
}

SPEC_FILES=()
while IFS= read -r spec_file; do
  SPEC_FILES+=("${spec_file}")
done < <(find "${SPECS_DIR}" -maxdepth 1 -type f \( -name '*.md' -o -name '*.markdown' -o -name '*.txt' \) | sort_paths)
if [[ "${#SPEC_FILES[@]}" -eq 0 ]]; then
  echo "No spec files found under ${SPECS_DIR}" >&2
  exit 1
fi

sanitize_name() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/--+/-/g'
}

write_state() {
  local status="$1"
  local current_index="$2"
  local current_file="$3"
  cat > "${STATE_FILE}" <<EOF
SESSION_NAME=${SESSION_NAME}
SPEC_NAME=${SPEC_NAME}
MODULE_PATH=${MODULE_PATH}
TOTAL_CHUNKS=${#SPEC_FILES[@]}
CURRENT_INDEX=${current_index}
CURRENT_FILE=${current_file}
STATUS=${status}
UPDATED_AT=$(date '+%Y-%m-%d %H:%M:%S')
EOF
}

apply_quality_context() {
  local managed_start="<!-- SPEC_WORKFLOW_QUALITY_START -->"
  local managed_end="<!-- SPEC_WORKFLOW_QUALITY_END -->"
  local claude_local="CLAUDE.local.md"

  if [[ ! -d "${QUALITY_DIR}" ]]; then
    return 0
  fi

  QUALITY_FILES=()
  while IFS= read -r quality_file; do
    QUALITY_FILES+=("${quality_file}")
  done < <(find "${QUALITY_DIR}" -type f | sort_paths)
  if [[ "${#QUALITY_FILES[@]}" -eq 0 ]]; then
    return 0
  fi

  local body_file
  body_file="$(mktemp)"
  {
    echo "${managed_start}"
    echo "# Workflow Quality Reference"
    echo ""
    echo "Read these files once at session start before implementation/review phases."
    echo ""
    for qf in "${QUALITY_FILES[@]}"; do
      echo "- ${qf}"
    done
    echo ""
    echo "${managed_end}"
  } > "${body_file}"

  if [[ -f "${claude_local}" ]]; then
    awk -v start="${managed_start}" -v end="${managed_end}" '
      $0==start {skip=1; next}
      $0==end {skip=0; next}
      !skip {print}
    ' "${claude_local}" > "${claude_local}.tmp"
    mv "${claude_local}.tmp" "${claude_local}"
    echo "" >> "${claude_local}"
    cat "${body_file}" >> "${claude_local}"
  else
    cat "${body_file}" > "${claude_local}"
  fi

  rm -f "${body_file}"
}

phase_name() {
  case "$1" in
    0) echo "plan" ;;
    1) echo "plan-review" ;;
    2) echo "plan-verify" ;;
    3) echo "yagni" ;;
    4) echo "implement" ;;
    5) echo "spec-verify" ;;
    6) echo "bug-security" ;;
    7) echo "fix-verify" ;;
    8) echo "structure" ;;
    9) echo "integration" ;;
    10) echo "side-effects" ;;
    11) echo "full-review" ;;
    12) echo "cleanup" ;;
    13) echo "quality" ;;
    14) echo "performance" ;;
    15) echo "ddd-review" ;;
    16) echo "user-flow" ;;
    17) echo "deep-review" ;;
    18) echo "deploy-judge" ;;
    19) echo "commit" ;;
    *) echo "unknown" ;;
  esac
}

phase_promise() {
  case "$1" in
    0) echo "PLAN DONE" ;;
    1) echo "PLAN REVIEW DONE" ;;
    2) echo "PLAN VERIFIED" ;;
    3) echo "YAGNI DONE" ;;
    4) echo "IMPL DONE" ;;
    5) echo "SPEC VERIFIED" ;;
    6) echo "SECURITY DONE" ;;
    7) echo "FIXES VERIFIED" ;;
    8) echo "REFACTOR DONE" ;;
    9) echo "INTEGRATION DONE" ;;
    10) echo "SIDEEFFECT DONE" ;;
    11) echo "FULL REVIEW DONE" ;;
    12) echo "CLEANUP DONE" ;;
    13) echo "QUALITY DONE" ;;
    14) echo "PERF DONE" ;;
    15) echo "DDD DONE" ;;
    16) echo "UX DONE" ;;
    17) echo "DEEP REVIEW DONE" ;;
    18) echo "SHIP IT" ;;
    19) echo "COMMIT DONE" ;;
    *) echo "" ;;
  esac
}

contains_promise() {
  local promise="$1"
  shift
  [[ $# -eq 0 ]] && return 1
  grep -qE "<promise>[[:space:]]*${promise}[[:space:]]*</promise>|${promise}" "$@" 2>/dev/null
}

session_state_value() {
  local file="$1"
  local key="$2"
  if [[ ! -f "${file}" ]]; then
    echo ""
    return 0
  fi
  grep "^${key}=" "${file}" | head -n 1 | cut -d'=' -f2-
}

build_chunk_report() {
  local chunk_key="$1"
  local cw_session_name="$2"
  local spec_file="$3"
  local source_dir="${CW_SESSIONS_DIR}/${cw_session_name}"
  local target_dir="${WORKFLOW_DIR}/${chunk_key}"
  local chunk_summary="${target_dir}/summary.md"
  local session_state="${source_dir}/state.env"
  local status current_phase

  mkdir -p "${target_dir}"
  status="$(session_state_value "${session_state}" "STATUS")"
  current_phase="$(session_state_value "${session_state}" "CURRENT_PHASE")"
  [[ -z "${status}" ]] && status="unknown"
  [[ -z "${current_phase}" ]] && current_phase="-1"

  {
    echo "# Chunk Summary"
    echo ""
    echo "- chunk: ${chunk_key}"
    echo "- cw_session: ${cw_session_name}"
    echo "- spec_file: ${spec_file}"
    echo "- cw_status: ${status}"
    echo "- cw_current_phase: ${current_phase}"
    echo ""
    echo "## Phase Status"
  } > "${chunk_summary}"

  for phase in $(seq 0 19); do
    local ptag pname promise pdir pstatus iterations
    ptag="$(printf 'phase%02d' "${phase}")"
    pname="$(phase_name "${phase}")"
    promise="$(phase_promise "${phase}")"
    pdir="${target_dir}/${ptag}-${pname}"
    mkdir -p "${pdir}"

    shopt -s nullglob
    local files=("${source_dir}/cw-phase-${phase}-iter-"*.log "${source_dir}/cw-phase-${phase}-iter-"*-prompt.md)
    shopt -u nullglob

    if [[ "${#files[@]}" -eq 0 ]]; then
      pstatus="NOT_STARTED"
      iterations=0
    else
      iterations="$(printf '%s\n' "${files[@]}" | sed -nE 's/.*iter-([0-9]+).*/\1/p' | sort -u | wc -l | tr -d ' ')"
      if contains_promise "${promise}" "${source_dir}/cw-phase-${phase}-iter-"*.log; then
        pstatus="DONE"
      elif [[ "${status}" == "completed" && "${phase}" -le 19 ]]; then
        pstatus="DONE_NO_PROMISE"
      elif [[ "${current_phase}" =~ ^[0-9]+$ ]] && (( phase < current_phase )); then
        pstatus="DONE_NO_PROMISE"
      elif [[ "${current_phase}" =~ ^[0-9]+$ ]] && (( phase == current_phase )) && [[ "${status}" == "in_progress" ]]; then
        pstatus="IN_PROGRESS"
      else
        pstatus="ATTEMPTED"
      fi
    fi

    {
      echo "# ${ptag} ${pname}"
      echo ""
      echo "- status: ${pstatus}"
      echo "- promise: ${promise}"
      echo "- iteration_count: ${iterations}"
      echo ""
      echo "## Files"
      if [[ "${#files[@]}" -eq 0 ]]; then
        echo "- (none)"
      else
        for f in "${files[@]}"; do
          local line_count
          line_count="$(wc -l < "${f}" | tr -d ' ')"
          echo "- ${f} (lines=${line_count})"
        done
      fi
    } > "${pdir}/status.md"

    echo "- ${ptag} ${pname}: ${pstatus}" >> "${chunk_summary}"
  done
}

build_workflow_summary() {
  {
    echo "# Workflow Summary"
    echo ""
    echo "- session: ${SESSION_NAME}"
    echo "- spec_name: ${SPEC_NAME}"
    echo "- module_path: ${MODULE_PATH}"
    echo "- chunks: ${#SPEC_FILES[@]}"
    echo ""
    echo "## Chunks"
  } > "${SUMMARY_FILE}"

  local idx=0
  for spec_file in "${SPEC_FILES[@]}"; do
    idx=$((idx + 1))
    local base chunk_key chunk_slug cw_session chunk_dir cstatus
    base="$(basename "${spec_file}")"
    chunk_slug="$(sanitize_name "${base%.*}")"
    chunk_key="$(printf '%03d-%s' "${idx}" "${chunk_slug}")"
    cw_session="${SESSION_NAME}-${chunk_key}"
    chunk_dir="${WORKFLOW_DIR}/${chunk_key}"

    if [[ -f "${CW_SESSIONS_DIR}/${cw_session}/state.env" ]]; then
      cstatus="$(session_state_value "${CW_SESSIONS_DIR}/${cw_session}/state.env" "STATUS")"
    else
      cstatus="not_started"
    fi

    echo "- ${chunk_key}: ${spec_file} (cw_session=${cw_session}, status=${cstatus})" >> "${SUMMARY_FILE}"
    if [[ -f "${chunk_dir}/summary.md" ]]; then
      echo "  - report: ${chunk_dir}/summary.md" >> "${SUMMARY_FILE}"
    fi
  done
}

apply_quality_context

{
  echo "# Ordered Spec Chunks"
  echo ""
  i=0
  for spec_file in "${SPEC_FILES[@]}"; do
    i=$((i + 1))
    echo "$(printf '%03d' "${i}") ${spec_file}"
  done
} > "${ORDER_FILE}"

write_state "in_progress" "0" "-"

index=0
for spec_file in "${SPEC_FILES[@]}"; do
  index=$((index + 1))
  spec_base="$(basename "${spec_file}")"
  chunk_slug="$(sanitize_name "${spec_base%.*}")"
  chunk_key="$(printf '%03d-%s' "${index}" "${chunk_slug}")"
  cw_session="${SESSION_NAME}-${chunk_key}"
  cw_state_file="${CW_SESSIONS_DIR}/${cw_session}/state.env"

  write_state "in_progress" "${index}" "${spec_file}"

  if [[ -f "${cw_state_file}" ]]; then
    cw_status="$(session_state_value "${cw_state_file}" "STATUS")"
    if [[ "${cw_status}" == "completed" ]]; then
      echo "[${chunk_key}] already completed. Skip cw run."
      build_chunk_report "${chunk_key}" "${cw_session}" "${spec_file}"
      build_workflow_summary
      continue
    fi
  fi

  cmd=(cw -s "${cw_session}" "${spec_file}" -m "${MODULE_PATH}" -n "${MULTIPLIER}" --model "${MODEL_NAME}" --reasoning-effort "${REASONING_EFFORT}")
  if [[ -n "${TEMPLATES_DIR}" ]]; then
    cmd+=(--templates "${TEMPLATES_DIR}")
  fi

  echo "[${chunk_key}] run: ${cmd[*]}"
  if [[ "${DRY_RUN}" == "true" ]]; then
    continue
  fi

  if ! "${cmd[@]}"; then
    build_chunk_report "${chunk_key}" "${cw_session}" "${spec_file}"
    build_workflow_summary
    write_state "failed" "${index}" "${spec_file}"
    echo "cw failed at chunk ${chunk_key} (${spec_file}). Resume by re-running the same command." >&2
    exit 1
  fi

  build_chunk_report "${chunk_key}" "${cw_session}" "${spec_file}"
  build_workflow_summary
done

if [[ "${DRY_RUN}" == "true" ]]; then
  write_state "dry_run" "0" "-"
  build_workflow_summary
  echo "Dry-run completed."
  exit 0
fi

write_state "completed" "${#SPEC_FILES[@]}" "ALL_DONE"
build_workflow_summary
echo "Workflow completed."
echo "Summary: ${SUMMARY_FILE}"
