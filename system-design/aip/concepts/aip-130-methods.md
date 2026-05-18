---
concept_id: system-design/aip-130-methods
title: "AIP-130: Methods (+ REST API 기본)"
domain: system-design
bloom_level: 3
bloom_achieved_max: 0
prerequisites:
  - system-design/rfc3986   # URL 문법, §4.2 colon은 AIP custom method 표기의 기반
weakness_tags: []
references:
  - url: https://aip.dev/130
    note: "AIP-130 Standard methods — 5개 표준 메서드 패턴 정의"
  - url: https://aip.dev/121
    note: "AIP-121 Resource-Oriented Design — 'Resources' 사상의 큰 그림"
  - url: https://datatracker.ietf.org/doc/html/rfc7231
    note: "RFC 7231 HTTP/1.1 Semantics — GET/POST/PUT/PATCH/DELETE의 의미와 안전성·멱등성"
session_modes_used: [C]
quick_explain_only: false
created: 2026-05-18
updated: 2026-05-18
---

# AIP-130: Methods (+ REST API 기본)

## 0. 약어 풀이

| 약어 | 풀네임 | 한 줄 설명 |
|---|---|---|
| **HTTP** | HyperText Transfer Protocol | 클라이언트↔서버 통신 프로토콜. 웹의 기본 |
| **REST** | Representational State Transfer | 2000년 Roy Fielding이 박사논문에서 제안한 API 설계 스타일. "리소스 + 표준 메서드" |
| **AIP** | API Improvement Proposals | Google이 자사 API를 일관성 있게 설계하기 위해 만든 가이드라인 모음. [aip.dev](https://aip.dev) |
| **RPC** | Remote Procedure Call | "원격 함수 호출" 스타일. REST가 명사 중심이라면 RPC는 동사 중심 |
| **CRUD** | Create, Read, Update, Delete | 데이터 다루는 4가지 기본 동작 |

## 1. REST API 기본

### HTTP 요청의 3요소

1. **메서드** — 어떤 동작인가
2. **URL** — 무엇에 대해 (RFC 3986에서 본 그 URL)
3. **body** — 필요한 데이터 (있을 때)

### HTTP 메서드 5개 (REST에서 자주 쓰는 것)

| 메서드 | 의미 | 안전한가?* | 멱등?† |
|---|---|---|---|
| **GET** | 조회 (변경 X) | ✅ | ✅ |
| **POST** | 생성·처리 | ❌ | ❌ |
| **PUT** | 전체 교체 | ❌ | ✅ |
| **PATCH** | 부분 수정 | ❌ | (보통) |
| **DELETE** | 삭제 | ❌ | ✅ |

\* 안전(safe) = 서버 상태를 바꾸지 않음
† 멱등(idempotent) = 같은 요청을 여러 번 보내도 결과 동일

### 리소스 개념

URL이 가리키는 것 = **리소스 (resource)**. 즉 "다루고 싶은 사물·엔티티".

```
/users           ← User 컬렉션 (전체)
/users/42        ← User 42 (개별)
/users/42/posts  ← User 42의 Post 컬렉션
/users/42/posts/7 ← User 42의 Post 7
```

URL 구조는 계층적. 큰 컨테이너 → 작은 것으로.

### REST의 모델

```
어떤 동작?   → 메서드
무엇에 대해? → URL (리소스)
필요 데이터? → body
```

객체지향의 `object.method(args)`와 유사. URL=object, method=method, body=args.

## 2. AIP-130 핵심 — Resource-Oriented Design

### 사상 — "동사가 아니라 명사"

Google의 가르침: **메서드(동사)보다 리소스(명사)가 먼저**. 모든 API를 "리소스에 표준 동작을 적용"하는 형태로.

API 설계 시 첫 질문: **"이 API의 리소스는 무엇이고, 동작은 표준 5개 중 어디에 속하나?"**

### 5개 표준 메서드

| 메서드 이름 | HTTP | URL | 의미 |
|---|---|---|---|
| **List**`Resources` | GET | `/resources` | 컬렉션 조회 |
| **Get**`Resource` | GET | `/resources/{id}` | 개별 조회 |
| **Create**`Resource` | POST | `/resources` (body) | 생성 |
| **Update**`Resource` | PATCH | `/resources/{id}` (body) | 수정 (부분) |
| **Delete**`Resource` | DELETE | `/resources/{id}` | 삭제 |

명명 규칙:
- 메서드 이름: 동사 + 리소스 단수 (`GetUser`, `CreateOrder`)
- 단, List만 복수형 (`ListUsers`)
- URL: 컬렉션은 복수, 개별은 `/resources/{id}`

### URL 패턴 — 계층

```
/users                           ← User 컬렉션
/users/42                        ← User 42
/users/42/posts                  ← 42의 Post 컬렉션 (sub-resource)
/users/42/posts/7                ← 42의 Post 7
```

## 3. Custom Methods — 표준 5개로 안 되는 동작

`:` 콜론으로 표시.

| 일반 REST | AIP-130 권고 |
|---|---|
| `POST /users/42/resetPassword` | `POST /users/42:resetPassword` |
| `POST /posts/100/publish` | `POST /posts/100:publish` |
| `POST /orders/55/refund` | `POST /orders/55:refund` |

### 왜 `:` 인가

1. **URL 자체는 명사 중심으로 유지** — `/posts/100`은 분명히 "글 100번"이라는 리소스
2. **`:publish`가 표준 동작이 아닌 custom임을 시각적으로 명시**
3. **모든 글 관련 API가 한 URL 패턴 아래** (`/posts`, `/posts/{id}`, `/posts/{id}:publish`)
4. **자동화 도구가 표준 vs custom을 즉시 구분 가능**

### RFC 3986과의 연결

`:`은 RFC 3986 §3.3 path 문법에서 segment 안에 허용되는 문자. 따라서 path 안에서 자유롭게 쓸 수 있음.

단, **첫 segment에는 `:` 금지** (§4.2 path-noscheme 콜론 모호성). custom method는 항상 리소스 뒤에 붙으므로 첫 segment가 아님 → 안전.

→ **AIP는 RFC 3986 위에 쌓인 표준**. RFC 3986의 규칙을 알고 있음을 전제로 함.

## 4. Custom Method를 만들지 말 것 — 핵심 권고

만들기 전에 묻기:
1. "이거 정말 표준 5개로 표현할 수 없나?"
2. "상태 변경이면 `UpdateUser` + 필드 변경(`state=ACTIVE`)으로 풀 수 있나?"

예: "사용자 활성화"는 custom method `activate`보다 `UpdateUser`로 `state` 필드 변경이 보통 더 깔끔.
→ 이게 AIP-216 (States) 주제. 다음 사이클에서 다룸.

## Q&A

### Q1: "글 발행(publish)이랑 '글 하나 만들기'랑 뭐가 다른가? 둘 다 글 생성 아닌가?"

**A**: 둘은 완전히 다른 동작이다.

- **새 글 만들기** (`POST /posts`): 새 ID 발급, 새 글 생성. 전에 없던 리소스가 새로 생긴다.
- **글 발행** (`POST /posts/100:publish`): ID 100 그대로, status만 draft → published로 바뀜. **같은 리소스, 상태만 바뀜**.

발행 전 글(id=100, status=draft)과 발행 후 글(id=100, status=published)은 **같은 글**이다. ID도 같고 제목·본문도 그대로. "공개됐다"는 상태만 다르다.

그래서 `POST /publishPosts body: {id: 100}` 같은 표현은 어색하다:
1. URL이 동사 중심이 됨 (AIP는 명사 중심을 권장)
2. `/publishPosts`가 새 리소스 컬렉션처럼 보임 (실제로 그런 컬렉션은 없음 — `/publishPosts/1`, `/publishPosts/2` 가 있을 리 없음)
3. 같은 글을 다루는 API가 `/posts`, `/publishPosts` 등으로 흩어져 일관성 깨짐
4. AIP의 `:` 표기는 "리소스에 적용하는 동작"임을 시각적으로 명확히 함

### Q2: `POST /posts/100/publish` (콜론 없이 슬래시)도 흔히 보이는데?

**A**: 일반 REST 글에서 자주 보이지만, AIP는 권장하지 않는다. 이유:
- `/publish`가 segment처럼 보이지만 사실 동사라 일관성이 흐려짐
- 자동화 도구가 표준 메서드인지 custom인지 구분하기 어려움
- AIP의 `:` 표기는 더 엄격한 일관성을 위한 것

REST에서 합당하지만, **AIP는 그것보다 더 엄격한 일관성을 요구**하는 표준이다.

## 다이어그램 (시각화)

(이번 사이클에선 AIP-130만 학습했으므로 별도 다이어그램은 만들지 않음. 다음 사이클에서 9개 AIP 통합 다이어그램 작성 예정.)

## 참고 자료

- [AIP-130: Standard methods](https://aip.dev/130) — 5개 표준 메서드 패턴 공식 정의
- [AIP-121: Resource-Oriented Design](https://aip.dev/121) — Resource-Oriented Design 사상의 큰 그림
- [AIP-136: Custom methods](https://aip.dev/136) — Custom method의 정의와 colon 표기
- [RFC 7231: HTTP/1.1 Semantics](https://datatracker.ietf.org/doc/html/rfc7231) — GET/POST/PUT/PATCH/DELETE의 의미, safety, idempotency
- [RFC 3986 §3.3 Path](https://datatracker.ietf.org/doc/html/rfc3986#section-3.3) — segment 안의 colon 허용 규칙 (AIP custom method `:`의 기반)
