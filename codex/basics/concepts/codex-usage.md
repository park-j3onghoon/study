# 코덱스 사용법 (Quick Explain)

기준일: 2026-02-21

## 한 줄 정의
Codex는 자연어 요청을 받아 코드베이스를 읽고, 수정하고, 명령 실행까지 수행하는 코딩 에이전트입니다.

## 비유
코덱스는 "같은 터미널에 앉아 있는 페어 프로그래머"에 가깝습니다.
사용자가 목표를 말하면, 코덱스가 필요한 파일을 찾고, 수정안을 만들고, 실행/검증까지 이어서 처리합니다.

## 동작 도식
```text
[사용자 목표 입력]
        |
        v
[Codex가 계획 수립]
        |
        v
[파일 읽기/수정 + 명령 실행]
        |
        v
[승인 모드/샌드박스 검증]
        |
        v
[결과 보고 + 다음 액션 제안]
```

## 왜 이렇게 동작하는가 (근본 원리)
1. LLM 추론 + 도구 실행 결합
   - 단순 답변이 아니라 실제 파일/명령 도구를 호출해 작업을 완료합니다.
2. 안전 우선 실행
   - 권한 모드(Read Only/Auto/Edit/Full Access)와 승인 정책으로 위험한 작업을 제어합니다.
3. 반복 작업 자동화
   - 대화형(`codex`)과 비대화형(`codex exec`), 원격 실행(`codex cloud exec`)로 상황에 맞게 자동화 수준을 조절합니다.

## 가장 빠른 시작 순서
1. 설치
   - `npm i -g @openai/codex`
2. 실행
   - `codex`
3. 인증
   - ChatGPT 로그인 또는 OpenAI API 키로 로그인
4. 첫 요청
   - 예: `tests 깨지는 원인 찾고 수정해줘`
5. 권한 모드 확인
   - `/permissions`에서 승인/접근 정책 확인

## 자주 쓰는 실행 방식
- 대화형 에이전트: `codex`
- 1회성 작업 실행: `codex exec "PR #16 리뷰하고 버그 우선으로 요약"`
- 클라우드 원격 실행: `codex cloud exec "리팩터링 후 테스트 통과까지"`

## 참고 문서
- https://developers.openai.com/codex/cli
- https://developers.openai.com/codex/cli/features
- https://openai.com/index/introducing-codex/

## Q&A

### Q1. 원격 실행은 뭐고, 작업이 로컬에도 적용되나?
A. 원격 실행은 Codex Cloud에서 백그라운드로 작업을 돌리는 방식입니다.
- Cloud 쪽에서 컨테이너를 띄우고, 지정 브랜치/커밋을 체크아웃해 작업합니다.
- 로컬에 자동으로 바로 반영되는 개념은 아닙니다. 결과 diff를 확인한 뒤 적용하는 흐름입니다.
- CLI에서는 `codex cloud exec`로 작업을 던지고, 필요하면 `codex apply <TASK_ID>`로 로컬 저장소에 패치를 적용합니다.

### Q2. 권한은 디렉터리 제한인가, 세션 제한인가?
A. 둘 다입니다.
- 세션 단위: `/permissions`에서 승인 모드(Read-only/Auto/Full Access 등)를 현재 대화 세션 기준으로 바꿉니다.
- 디렉터리 단위: 기본은 현재 작업 디렉터리 범위이며, `--add-dir`로 추가 경로 접근을 열 수 있습니다.
- 영구 기본값: `~/.codex/config.toml`(사용자), `.codex/config.toml`(프로젝트), `--profile`로 기본 권한/샌드박스 정책을 저장해 다음 세션에도 적용할 수 있습니다.

### Q3. Claude Code의 스킬/기능과 비슷한 게 있나?
A. 있습니다. Codex에도 거의 대응되는 개념이 있습니다.
- Skills: Codex는 `SKILL.md` 기반 Agent Skills를 지원하고, 명시 호출(`$skill`, `/skills`) + 암시 호출(설명 매칭) 둘 다 가능합니다.
- 프로젝트 지침: `AGENTS.md`를 글로벌/프로젝트/하위 폴더로 계층 적용해 동작 규칙을 제어합니다.
- 확장: MCP 연동, Slash commands, Multi-agent(실험적), Cloud delegation 등으로 자동화/확장 가능합니다.

### Q4. `ENV_ID`와 `TASK_ID`는 뭐고 왜 필요한가?
A.
- `ENV_ID`: Codex Cloud에서 작업이 실행될 "원격 개발 환경" 식별자입니다. 어느 저장소/브랜치 컨텍스트에서 돌릴지 지정합니다.
- `TASK_ID`: Cloud에 제출된 "개별 작업 1건"의 식별자입니다. 상태 조회(`status`), 변경점 확인(`diff`), 로컬 적용(`apply`) 때 같은 작업을 가리킬 때 씁니다.

의미를 비유하면:
- `ENV_ID` = 작업장(어느 워크스페이스에서 일할지)
- `TASK_ID` = 작업번호(그 작업장 안에서 몇 번 작업인지)

### Q5. 왜 `exec`에는 `ENV_ID`, 후속 명령에는 `TASK_ID`가 필요한가?
A.
- `exec` 시점에는 "어디서 실행할지"를 먼저 정해야 하므로 `ENV_ID`가 필요합니다.
- 작업이 생성된 뒤에는 "어떤 작업을 조회/적용할지"가 중요하므로 `TASK_ID`를 씁니다.
- 즉, 흐름이 `환경 선택(ENV_ID) -> 작업 생성 -> 작업 식별(TASK_ID)` 순서입니다.

### Q6. 샌드박스/승인 정책/프로필은 각각 뭐고 어떻게 연결되나?
A.
- 샌드박스(`--sandbox`): 에이전트가 명령을 실행할 때의 접근 경계입니다.
  - `read-only`: 읽기 위주
  - `workspace-write`: 워크스페이스 쓰기 허용
  - `danger-full-access`: 제한 최소화
- 승인 정책(`--ask-for-approval`): 어떤 명령에서 사람 확인을 요구할지 정합니다.
  - 예: `untrusted`, `on-request`, `never`
- 프로필(`--profile`): 위 설정들을 묶어 재사용하는 프리셋 이름입니다(`config.toml`에 저장).

도식:
```text
profile(기본값 묶음)
   ├─ sandbox(어디까지 실행 허용?)
   └─ approval(언제 사람 승인 받나?)
```

예시:
```bash
codex --profile team-safe --sandbox workspace-write --ask-for-approval on-request --add-dir ../shared-lib
```
- 현재 디렉터리를 기본 작업 루트로 쓰고
- `../shared-lib`를 추가 접근 경로로 열어둔 실행 예시입니다.

### Q7. `--add-dir ../shared-lib`와 `sandbox`는 왜 필요한가?
A.
- `--add-dir ../shared-lib`는 "기본 작업 폴더 바깥의 특정 폴더 하나를 추가로 열어주는 옵션"입니다.
- 즉, 현재 프로젝트는 그대로 두고 `../shared-lib`까지 함께 읽고/쓸 수 있게 범위를 넓힙니다.

비유:
- 기본 작업 폴더 = 기본 작업실
- `--add-dir` = 옆 창고 열쇠 1개 추가
- `sandbox` = 출입 가능한 구역 자체를 정하는 건물 규칙

왜 쓰나:
1. 모노레포/멀티폴더 작업
   - 앱 코드는 현재 폴더, 공용 라이브러리는 `../shared-lib`에 있을 때 둘 다 수정 가능
2. 안전성 유지
   - `danger-full-access` 대신 필요한 폴더만 열어 최소 권한으로 작업 가능

실전 예시:
```bash
codex --sandbox workspace-write --add-dir ../shared-lib
```
- 현재 폴더 + `../shared-lib`만 실질 작업 범위로 두는 안전한 설정입니다.

### Q8. `--add-dir`는 하위폴더도 포함하나? `sandbox`를 권한 집합으로 봐도 되나?
A.
- 네. `--add-dir <DIR>`는 해당 디렉터리 트리(하위 폴더 포함)를 추가 작업 범위로 여는 개념으로 이해하면 됩니다.
- 그리고 `sandbox`를 "실행 권한 경계를 미리 정한 정책 집합"으로 보는 해석도 맞습니다.
- 다만 실제 실행 시에는 `sandbox` 정책 + 현재 작업 루트 + `--add-dir`로 연 추가 경로가 함께 적용됩니다.
