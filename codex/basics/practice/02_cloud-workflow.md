# 실습 02: 원격 실행 워크플로우 (응용)

목표: Cloud 작업 생성 → 상태 확인 → diff 확인 → 로컬 적용 순서를 이해한다.

## 1) 명령 도움말 확인
```bash
codex cloud --help
codex cloud exec --help
```

## 2) 아래 템플릿 채우기 (실제 실행은 선택)
```bash
# 작업 생성
codex cloud exec --env <ENV_ID> --branch <BRANCH> "<TASK_PROMPT>"

# 상태 확인
codex cloud status <TASK_ID>

# 변경점 확인
codex cloud diff <TASK_ID>

# 로컬 반영
codex cloud apply <TASK_ID>
# 또는
codex apply <TASK_ID>
```

## 완료 조건
- `<ENV_ID>`, `<BRANCH>`, `<TASK_PROMPT>`를 본인 값으로 채워서 제출
- Cloud 실행이 어렵다면 템플릿만 정확히 채워도 완료 처리
