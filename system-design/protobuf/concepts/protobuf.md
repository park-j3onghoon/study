---
concept_id: system-design/protobuf
title: "Protobuf: Oneof + Updating + Backwards Compatibility"
domain: system-design
bloom_level: 3
bloom_achieved_max: 0
prerequisites: []
weakness_tags: []
references:
  - url: https://protobuf.dev/programming-guides/proto3/
    note: "Protobuf Language Guide (proto3) — 메시지 정의, oneof, wire type 등 공식 가이드"
  - url: https://protobuf.dev/programming-guides/proto3/#updating
    note: "§Updating A Message Type — 안전한/위험한 변경 규칙"
  - url: https://protobuf.dev/programming-guides/encoding/
    note: "§Encoding — wire type 정의와 호환 규칙"
session_modes_used: [C]
quick_explain_only: false
created: 2026-05-18
updated: 2026-05-18
---

# Protobuf: Oneof + Updating + Backwards Compatibility

## 0. 약어 풀이

| 약어 | 풀네임 | 한 줄 설명 |
|---|---|---|
| **Protobuf** | Protocol Buffers | 구글이 2008년 오픈소스화한 데이터 직렬화 포맷 + 스키마 언어 |
| **wire format** | 직렬화 결과의 바이너리 표현 형식 | 필드를 `(번호, wire type, 값)` 트리플로 인코딩 |
| **proto3 / proto2** | Protobuf 스키마 언어의 버전 | proto3가 현재 표준 (2016~). 이 문서는 proto3 기준 |
| **protoc** | Protobuf 컴파일러 | `.proto` 파일을 각 언어(Go, Python, Java 등)별 클래스로 생성 |
| **gRPC** | Google RPC | Protobuf를 기반으로 한 RPC 프레임워크. 마이크로서비스 통신에 자주 사용 |

## 1. 왜 Protobuf인가 — JSON 대비

| | JSON | Protobuf |
|---|---|---|
| 형식 | 텍스트 (사람이 읽음) | 바이너리 (사람은 못 읽음) |
| 크기 | 큼 | **3~10배 작음** |
| 속도 | 느림 | **빠름** |
| 타입 안전 | ❌ 런타임에 알게 됨 | ✅ 컴파일 시 보장 |
| 스키마 | 없음 (자유롭게 추가/삭제, 위험) | 필수 (`.proto`에 명시) |

마이크로서비스 간 RPC(특히 gRPC), 데이터 저장, 모바일↔서버 통신에 많이 씀.

## 2. 기본 문법

```protobuf
syntax = "proto3";

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

- `message User { ... }`: 메시지 정의
- 각 필드 = `타입 이름 = 번호;`
- 번호(1, 2, 3...)가 핵심 — 직렬화 키
- 이름은 코드에서 접근할 때만 쓰는 라벨

## 3. ⭐ 핵심 통찰 — 필드 번호 vs 이름

> **이름은 .proto와 너의 코드 안에서만 쓰임. 직렬화 바이트엔 번호만 들어감.**

`User{id=42, name="Teddy"}`를 직렬화하면 바이트는 대략:
```
08 2A 12 05 54 65 64 64 79
─┬─ ─┬─ ─┬─ ─┬─ ──────┬──────
필드1 값  필드2 길이  "Teddy"
 키  42   키   5     (UTF-8)
```

→ 어디에도 "id", "name" 같은 글자 없음. 번호 1, 2만 있음.

**결과**:
- 이름은 바꿔도 됨 (호환됨)
- 번호는 절대 바꾸면 안 됨 (호환 깨짐)
- 새 필드는 새 번호로 추가
- 삭제한 필드의 번호를 **재사용 금지**

### 비유 — 콘서트 좌석 번호

티켓에 "12번 좌석"이라고 적혀 있지 "John의 좌석"이라고 적혀 있진 않음. 좌석 번호로 매칭. 사람 이름은 어디서도 안 나옴. 그래서 누가 그 좌석에 앉든 OK.

## 4. 안전한 변경 ✅ — 새 필드 추가

```protobuf
// v1
message User {
  int32 id = 1;
  string name = 2;
}

// v2 (필드 추가, 새 번호)
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

**양방향 호환**:

| 방향 | 결과 |
|---|---|
| v1 데이터 → v2 코드 (backward) | `User{id=42, name="Teddy", email=""}` — email은 default |
| v2 데이터 → v1 코드 (forward) | `User{id=42, name="Teddy"}` — email은 unknown으로 무시 |

proto3의 모든 필드는 implicit default (string=`""`, int=`0`, bool=`false`, message=`null`). 그래서 빠진 필드는 자동으로 default.

wire format은 각 필드마다 `(번호, wire type, 길이)`를 적기 때문에, 모르는 번호를 만나도 길이만큼 건너뛰면 됨 → forward compatible.

## 5. 위험한 변경 ❌ — 필드 번호 재사용

가장 흔한 함정. **삭제한 필드의 번호를 새 필드에 재사용하지 마세요.**

```protobuf
// v1
message User {
  int32 id = 1;
  string name = 2;
  int32 age = 3;
}

// v2 — age 삭제
message User {
  int32 id = 1;
  string name = 2;
}

// v3 — 누군가 "3번이 비어있네!" 하고 추가 ⚠️
message User {
  int32 id = 1;
  string name = 2;
  string nickname = 3;  // 재사용 ❌
}
```

**문제**: v1 데이터엔 `[3: int32: 25]`(age=25)가 들어있는데, v3 코드는 그걸 string nickname으로 읽으려 함. wire type 다름(varint vs length-delimited) → 역직렬화 에러. 우연히 wire type이 같으면 엉뚱한 데이터.

### 해결책 — `reserved` 키워드

```protobuf
// v2 — age 삭제할 때 reserved 선언
message User {
  int32 id = 1;
  string name = 2;
  reserved 3;          // 번호 3 재사용 금지
  reserved "age";      // 이름 "age"도 재사용 금지
}
```

- 누군가 v3에서 `nickname = 3`을 쓰면 컴파일 에러
- 이름까지 reserved하는 이유: 옛 코드와 같은 이름 쓰면 혼동

## 6. wire type — 타입 변경의 호환 기준

Protobuf의 wire format은 6가지 wire type을 사용. 실무에서 자주 만나는 3개:

| wire type | 어떤 .proto 타입들이 여기에 속함 |
|---|---|
| **varint** (0) | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
| **fixed32** (5) | fixed32, sfixed32, float |
| **length-delimited** (2) | string, bytes, embedded message, packed repeated |

### 호환 규칙

> **같은 wire type 그룹 안에서 변경은 호환. 다른 그룹으로 가면 호환 깨짐.**

| 변경 | 호환? |
|---|---|
| int32 ↔ int64 ↔ uint32 ↔ bool ↔ enum | ✅ (모두 varint) |
| string ↔ bytes | ✅ (모두 length-delimited) |
| float ↔ double | ❌ (fixed32 vs fixed64) |
| int32 → string | ❌ (varint vs length-delimited) |

### 비유 — 옷걸이

타입 라벨이 "int32"인지 "int64"인지는 코드의 문제. 옷걸이 크기(wire type)가 같으면 옷걸이에 걸 수 있음. int32와 int64는 라벨만 다른 옷, 옷걸이는 같은 varint.

### 주의 — protoc는 호환성 검사 안 함

`.proto` 컴파일러(protoc)는 그저 새 코드를 생성할 뿐, 옛 버전과의 호환성을 자동 검증하지 않음. 변경이 호환되는지 확인하려면 **외부 도구**(예: [buf](https://buf.build))를 써야 함.

## 7. Oneof — 정확히 하나만

별도 주제. 호환성과는 다른 측면.

```protobuf
message PaymentMethod {
  int32 user_id = 1;
  
  oneof method {
    string credit_card_number = 2;
    string paypal_email = 3;
    string crypto_wallet = 4;
  }
}
```

### 무엇인가
- `method` 라는 이름의 oneof 안에 3개 필드
- 이 셋 중 **정확히 하나만** 설정 가능
- 새 값 설정 시 기존 값 자동 클리어

### 왜 일반 필드 3개로 두면 안 되나
- 일반 필드 3개: 기술적으론 셋 다 채울 수도, 다 비울 수도 있음. "정확히 하나" 규칙을 코드 곳곳에서 검증해야 함
- Oneof: 스키마 수준에서 강제. API가 어느 필드 설정됐는지 확인하는 메서드 자동 생성

### 비유 — 라디오 다이얼
한 번에 한 채널만. KBS 켜면 MBC 자동으로 꺼짐.

### Oneof와 호환성 주의점
- **Oneof 안에 새 필드 추가**: ✅ 안전
- **일반 필드를 Oneof로 옮기기 (또는 반대)**: ❌ 위험. 데이터 의미 달라짐
- **Oneof 안의 필드를 다른 Oneof로 옮기기**: ❌ 위험. 그룹 소속 바뀜
- **Oneof 자체 삭제**: 옛 데이터의 그 필드들은 무시

## 8. 한 줄 핵심 정리

1. **필드 번호 = 직렬화 키, 이름 = 라벨**. 이름은 자유, 번호는 영원
2. **새 필드 추가(새 번호) = 양방향 호환**. proto3 default + unknown field skip
3. **번호 재사용 금지. 삭제 시 `reserved`로 가드**
4. **wire type이 같으면 타입 변경 호환**. varint ↔ varint OK, varint → length-delimited X
5. **Oneof = 정확히 하나만**. 메모리 효율 + 의도 명확
6. **protoc는 호환성 검사 안 함**. buf 같은 외부 도구 필요

---

## Q&A

(이번 사이클에서는 사용자 질문 없이 진행)

---

## 다이어그램 (시각화)

본문의 핵심 5개 개념을 단일 HTML 파일로 시각화. 모바일·데스크탑·다크 모드 호환, 외부 의존성 없음.

📊 **[다이어그램 보기](../diagrams/protobuf.html)**

수록:
1. 직렬화 결과의 바이트 분해 (번호 vs 이름)
2. v1↔v2 양방향 호환 (필드 추가)
3. 번호 재사용 위험 시나리오
4. wire type 그룹 호환 매트릭스
5. Oneof — 라디오 채널 비유

---

## 참고 자료

- [Protobuf Language Guide (proto3)](https://protobuf.dev/programming-guides/proto3/) — 공식 가이드
- [§Updating A Message Type](https://protobuf.dev/programming-guides/proto3/#updating) — 안전한/위험한 변경 규칙
- [§Encoding](https://protobuf.dev/programming-guides/encoding/) — wire type 정의와 호환 규칙
- [§Oneof](https://protobuf.dev/programming-guides/proto3/#oneof) — Oneof 정의와 호환성
- [buf — Protobuf 호환성 검사 도구](https://buf.build) — protoc가 못 하는 호환성 검사 자동화
