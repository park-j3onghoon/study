# 교차 약점 프로필

최종 업데이트: 2026-05-14 (rfc3986 사이클 보강)

## 활성 약점

### #tech/용어혼동 (출현 3회, 가중치 1.0)
- 발견 주제: claude-code/basics, claude-code/rules-vs-skills, system-design/rfc3986
- 패턴: 비슷한 이름/역할의 개념을 혼동
  - CLAUDE.md vs settings.json, user-invocable의 역할
  - "scheme이 있다 = 콜론(:)이 있다 = 절대 URI" 규칙 미흡 (Q1 `42`를 절대 URI로 오인, 응용 시나리오 `time:12-30` 콜론 모호성 미인식)
  - "절대 경로(absolute path)" vs "절대 URI(absolute URI)" 혼동 (`/foo/bar`는 path는 절대지만 URI는 아님 → Relative Reference)
- 보완 전략: 유사 개념 비교표 필수, 용어 구분 함정 문제 포함, "X와 Y의 차이"를 매 학습마다 1줄 요약 박스
- 해소 카운트: 0/3 (Bloom L3 이상 정답 필요)

### #tech/엣지케이스 (출현 1회, 가중치 1.0, 신규)
- 발견 주제: system-design/rfc3986
- 패턴: 경계 조건 누락
  - path-empty(`?query`)에서 base path 끝 `/` 보존 못 함 (Q3 오답)
  - base path 끝 `/` 유무에 따른 merge 결과 차이 인식 부족 (`/items/123` vs `/items/123/` 차이)
- 보완 전략: 경계값 시나리오 표(끝 /, 빈 path, dot-segment 위치 등) 별도 박스. "한 글자가 결정적" 케이스 의도적 출제
- 해소 카운트: 0/3

## 해소된 약점

(아직 해소된 약점 없음)
