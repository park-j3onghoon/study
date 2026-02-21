# 실습 1: Rules 설정 만들기

## 목표
프로젝트용 `settings.json`을 직접 작성해본다.

## 시나리오
당신은 팀 프로젝트를 셋업하는 중입니다. 다음 요구사항에 맞는 `.claude/settings.json`을 만드세요.

## 요구사항

1. **허용(allow)**: 아래 도구는 확인 없이 바로 실행
   - `Read` (모든 파일 읽기)
   - `Bash(npm run test)` (테스트만)
   - `Bash(npm run lint)` (린트만)

2. **확인(ask)**: 아래 도구는 매번 사용자 확인 필요
   - `WebFetch`
   - `Bash(git commit *)`

3. **차단(deny)**: 아래 도구는 절대 사용 금지
   - `Bash(rm -rf *)` (위험한 삭제)
   - `Read(.env*)` (.env 파일 접근 금지)

## 할 일

아래 파일을 열어서 `___` 부분을 채우세요:
→ `practice/01_settings.json`

완료되면 "완료"라고 입력해주세요.
