# sketch — Step 1.5 Mermaid 시각화

Explain 직후 멘탈 모델을 다이어그램으로 굳히는 단계. concepts 파일의 도식 섹션을 Mermaid 블록으로 강화한다.

## 트리거

Step 1 Explain 완료 직후. 사용자가 "스케치 패스" / "skip sketch" 입력 시 건너뛴다.

## 다이어그램 타입 자동 선택

주제 성격에 따라 1개 타입을 선택. 판단이 애매하면 flowchart로 폴백.

| 주제 성격 | 권장 타입 | 예시 |
|---|---|---|
| 순서·플로우 | `flowchart` | next-token-prediction, CI/CD 파이프라인 |
| 시스템 간 상호작용 | `sequenceDiagram` | OAuth 흐름, API 요청·응답 |
| 개념 분류·상속 | `classDiagram` | OOP 설계, 도메인 모델 |
| 개념 트리·연결 | `mindmap` | 학습 로드맵, 도메인 분류 |
| 상태 전이 | `stateDiagram-v2` | FSRS state, 워크플로우 상태 |
| 비교 매트릭스 | `quadrantChart` | 트레이드오프(CAP, scale vs cost) |

### 도메인별 기본 매핑
- `tech` → flowchart (실행 흐름) 또는 sequenceDiagram (네트워크·API)
- `system-design` → flowchart + sequenceDiagram 둘 다 권장
- `softskill` → mindmap (대화 분기) 또는 stateDiagram (감정·태도 전이)
- `process` → flowchart + stateDiagram

## 작성 규칙

1. Mermaid 블록을 concepts/{개념}.md에 삽입 (도식 섹션 또는 새 `## 다이어그램` 섹션)
2. 노드 수 5~12개를 목표. 12개 초과 시 핵심만 추리고 별도 다이어그램으로 분할
3. 한국어 라벨 허용, 단 `"인용부호"`로 감싸 파싱 오류 방지
4. 다이어그램 후 1~2줄 캡션 — 무엇을 시각화했는지

## ASCII 폴백

Mermaid가 어색한 경우(비교표·수학 식 등): ASCII 비교표, 분기 트리, 등고선 등 자유 형식 사용. 기존 v1 ASCII 다이어그램 그대로 유지 가능.

## 예시 (모드 C, ai-ml/next-token-prediction)

```
flowchart LR
  A["입력 텍스트"] --> B["토큰화"]
  B --> C["임베딩"]
  C --> D["Transformer 블록"]
  D --> E["다음 토큰 확률 분포"]
  E --> F["샘플링"]
  F --> A
```

캡션: 토큰화→임베딩→Transformer→확률→샘플링이 반복되며 텍스트가 한 토큰씩 생성된다.

## 진행 규칙

- 다이어그램 작성 후 사용자에게 "이 모델이 맞나요? 수정할 부분 있으면 알려주세요." 한 번 묻고 진행
- 수정 요청 시 즉시 반영 후 concepts 파일도 갱신
- "맞다" / 무응답 / "패스" → Step 1.7 Q&A로 진행
