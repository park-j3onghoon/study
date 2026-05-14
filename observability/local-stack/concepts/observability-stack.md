# 로컬 옵저버빌리티 스택

> 한 줄 요약: "내 앱이 지금 어떤 상태인지"를 알아내기 위해 **세 종류의 데이터**(로그·메트릭·트레이스)를 모으고, 저장하고, 조회하는 도구 묶음.

## 1. 옵저버빌리티(Observability)란

시스템 내부 상태를 외부에서 관찰할 수 있는 능력. 이를 가능하게 하는 세 가지 데이터를 **"3대 기둥(Three Pillars)"** 이라 부른다.

### 비유: 자동차 계기판

- 속도계(메트릭) → 숫자로 상태를 본다
- 블랙박스 영상(로그) → 무슨 일이 있었는지 기록한다
- 내비 경로(트레이스) → 출발~도착까지 경로를 추적한다

## 2. 세 가지 기둥: Logs, Metrics, Traces

| 기둥 | 비유 | 핵심 질문 | 예시 |
|------|------|-----------|------|
| **Logs** | 블랙박스 영상 | "무슨 일이 있었지?" | `ERROR: DB connection timeout at 14:32:05` |
| **Metrics** | 속도계/온도계 | "지금 숫자가 어떻지?" | CPU 사용률 85%, 요청 에러율 2.3% |
| **Traces** | 택배 추적번호 | "이 요청이 어디를 거쳤지?" | 유저요청→인증(50ms)→주문(120ms)→DB(80ms) |

### 역할 분담

- **Metrics**: 이상 징후 감지 (알림 발생)
- **Traces**: 문제의 실행 경로 파악
- **Logs**: 문제의 상세 원인 확인

## 3. 전체 아키텍처

```
 ┌──────────┐
 │   App    │  로그, 메트릭, 트레이스를 생성
 └────┬─────┘
      │ 세 종류의 데이터를 전부 보냄
      ▼
 ┌──────────┐
 │  Vector  │  "우체국 분류센터"
 │ (파이프  │  → 데이터를 받아서 종류별로 분류·가공·전달
 │  라인)   │
 └──┬──┬──┬─┘
    │  │  │
    ▼  ▼  ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│Victoria│ │ Victoria │ │ Victoria │
│  Logs  │ │ Metrics  │ │  Traces  │
└───┬────┘ └────┬─────┘ └────┬─────┘
    ▼          ▼            ▼
  LogQL     PromQL       TraceQL
```

## 4. Vector — 데이터 파이프라인

Datadog이 관리하는 오픈소스 도구. 옵저버빌리티 데이터를 **수집(Source) → 변환(Transform) → 전달(Sink)** 하는 파이프라인.

### 비유: 우체국 분류센터

편지(데이터)가 들어오면 → 종류별로 분류 → 각 목적지(Victoria DB들)로 배달.

### 왜 Vector를 쓰는가?

- 앱이 Vector **한 곳에만** 보내면 됨 (단일 진입점)
- Vector가 종류별로 분류해서 적절한 저장소로 전달
- 앱 입장에서 단순해짐

### 내부 구조

```
  Source(수집)      Transform(변환)       Sink(전달)
 ┌───────────┐    ┌──────────────┐    ┌──────────────┐
 │ 앱 로그   │───▶│ 파싱/필터링  │───▶│ Victoria Logs│
 │ 앱 메트릭 │───▶│ 포맷 변환    │───▶│ Victoria Met.│
 │ 앱 트레이스│───▶│ 라벨 추가    │───▶│ Victoria Tr. │
 └───────────┘    └──────────────┘    └──────────────┘
```

## 5. Victoria 시리즈 — 전문 데이터 저장소

VictoriaMetrics 팀이 만든 세 개의 전문 데이터베이스:

| 저장소 | 저장하는 것 | 비유 |
|--------|------------|------|
| **VictoriaLogs** | 로그 (텍스트 이벤트 기록) | 도서관의 일지 보관함 |
| **VictoriaMetrics** | 메트릭 (시계열 숫자) | 병원의 환자 차트 |
| **VictoriaTraces** | 트레이스 (요청 경로 추적) | 택배 배송 추적 시스템 |

### 왜 따로 저장하는가?

- 데이터 성격이 완전히 다름 (텍스트 vs 숫자 vs 구조화된 경로)
- 각각에 최적화된 저장/압축/검색 방식이 다름
- 하나의 DB에 다 넣으면 어느 것도 잘 못함

## 6. 쿼리 언어 — 저장된 데이터를 조회하는 방법

| 쿼리 언어 | 대상 | 하는 일 |
|-----------|------|---------|
| **LogQL** | 로그 | "에러 로그만 찾아줘", "최근 5분간 에러 몇 개?" |
| **PromQL** | 메트릭 | "CPU 사용률 추이 보여줘", "에러율 5% 넘으면 알려줘" |
| **TraceQL** | 트레이스 | "500ms 넘는 느린 요청 찾아줘" |

### 예시

```
# LogQL — error 레벨 로그 검색
{job="my-app"} |= "error"

# PromQL — 최근 5분간 HTTP 요청의 초당 처리량
rate(http_requests_total[5m])

# TraceQL — duration이 500ms 넘는 span 찾기
{ duration > 500ms }
```

LogQL은 PromQL에서 영감을 받아 만들어져 문법 철학이 유사하다.

## 참고 자료

- [VictoriaMetrics: Simple & Reliable Monitoring for Everyone](https://victoriametrics.com/) — VictoriaMetrics 공식 사이트
- [Full-Stack Observability with VictoriaMetrics in the OTel Demo](https://victoriametrics.com/blog/victoriametrics-full-stack-observability-otel-demo/) — Victoria 스택 전체 구성 데모
- [Victoria: The Observability Stack That Slaps the Industry](https://blog.vonng.com/en/db/victoria-stack/) — Victoria 스택 아키텍처 개요
- [Vector | A lightweight, ultra-fast tool for building observability pipelines](https://vector.dev/) — Vector 공식 사이트
- [Vector GitHub Repository](https://github.com/vectordotdev/vector) — Vector 소스코드 및 설명
- [How to Collect, Process, and Ship Log Data with Vector](https://betterstack.com/community/guides/logging/vector-explained/) — Vector 동작 방식 가이드
- [Three Pillars of Observability: Logs, Metrics and Traces | IBM](https://www.ibm.com/think/insights/observability-pillars) — 옵저버빌리티 3대 기둥 설명
- [Learn about query languages | Grafana Cloud](https://grafana.com/docs/grafana-cloud/telemetry-signals/query-visualize-data/visualize-query/learn-query-languages/) — LogQL, PromQL, TraceQL 비교
- [TraceQL: A powerful query language for distributed tracing](https://grafana.com/blog/get-to-know-traceql-a-powerful-new-query-language-for-distributed-tracing/) — TraceQL 소개
