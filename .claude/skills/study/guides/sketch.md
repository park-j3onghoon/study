# sketch — Step 1.5 HTML 단일 파일 시각화

Explain 직후 멘탈 모델을 **단일 HTML 파일** 로 시각화한다. 모바일·데스크탑·옵시디언 어디서나 동일하게 보이도록 외부 의존성 없이 한 파일에 모든 자산을 인라인한다.

## 트리거

Step 1 Explain 완료 직후. 사용자가 "스케치 패스" / "skip sketch" 입력 시 건너뛴다.

## 출력 파일

- 경로: `{대주제}/{소주제}/diagrams/{개념}.html` — **한 학습 주제당 1개 파일**
- 한 파일 안에 여러 다이어그램을 섹션으로 묶는다 (최대 5개, 다이어그램당 노드 5~12개)
- concepts/{개념}.md의 `## 다이어그램` 섹션에 상대 경로 링크만 넣는다:
  `[다이어그램 보기](../diagrams/{개념}.html)`

## 단일 파일 제약 (필수)

- 외부 CSS/JS/이미지 의존 금지. CDN(Mermaid, Tailwind, jQuery 등) 사용 금지
- 모든 스타일·스크립트는 `<style>` / `<script>` 인라인. 이미지는 SVG 인라인 또는 data URI
- `<!DOCTYPE html>` + UTF-8 + `<meta name="viewport" content="width=device-width, initial-scale=1.0">` 필수
- 다크 모드: `@media (prefers-color-scheme: dark)`로 자동 대응
- 다이어그램 폭이 화면을 넘으면 **해당 다이어그램만** 가로 스크롤(`overflow-x: auto`) — 전체 페이지 가로 스크롤 금지

## 표현 수단 (자유)

라이브러리 없이 SVG/CSS/HTML로 직접 작성한다. 주제에 맞는 표현을 선택.

| 주제 성격 | 권장 표현 | 비고 |
|---|---|---|
| 순서·플로우 | 인라인 SVG flowchart (rect + 화살표) | 가로 스크롤 가능 |
| 시스템 간 상호작용 | 인라인 SVG sequence diagram (lifeline + 화살표) | |
| 개념 분류·계층 | 인라인 SVG tree, 또는 nested div + CSS | |
| 비교·매트릭스 | HTML `<table>` + CSS | 모바일에서 가장 안정 |
| 상태 전이 | 인라인 SVG state diagram (상태 박스 + 라벨 화살표) | |
| 시간·진행 | CSS bar / timeline | |

### 도메인별 기본 매핑
- `tech` → 순서 flowchart 또는 sequence
- `system-design` → flowchart + sequence + 비교 표 중 2개 권장
- `softskill` → 계층 트리 또는 비교 표
- `process` → flowchart + 상태 전이

## 모바일 호환 체크리스트

- 본문 폰트 ≥ 14px, 다이어그램 라벨 ≥ 12px
- WCAG AA 이상 색 대비
- hover-only 정보 금지 (터치 디바이스 호환)
- 가로 스크롤은 다이어그램 단위로만
- 인쇄/PDF 호환: 다크 모드와 별도로 흑백에서도 읽혀야 함

## ASCII 폴백

매우 단순한 비교는 concepts 본문 안 ASCII로 충분. 새 HTML 파일을 만들지 말고 본문에 둔다.

## 스킬 동작

1. 다이어그램 HTML 작성 후 사용자에게 "이 모델이 맞나요? 수정할 부분 있으면 말씀해 주세요." 한 번 묻기
2. 수정 요청 시 즉시 반영
3. "맞다" / 무응답 / "패스" → Step 1.7 Q&A로 진행

## 보일러플레이트

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{개념} — 시각화</title>
  <style>
    :root {
      --bg: #ffffff; --fg: #1a1a1a; --muted: #666;
      --accent: #2563eb; --border: #e5e5e5; --card: #fafafa;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0f0f0f; --fg: #f0f0f0; --muted: #888;
        --accent: #60a5fa; --border: #2a2a2a; --card: #1a1a1a;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 16px;
      background: var(--bg); color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", sans-serif;
      line-height: 1.6;
    }
    .container { max-width: 960px; margin: 0 auto; }
    h1, h2 { line-height: 1.3; }
    .diagram {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin: 24px 0;
      background: var(--card);
      overflow-x: auto;
    }
    .caption { color: var(--muted); font-size: 14px; margin-top: 8px; }
    svg { display: block; max-width: 100%; height: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid var(--border); padding: 8px; text-align: left; font-size: 14px; }
    th { background: var(--card); }
  </style>
</head>
<body>
  <div class="container">
    <h1>{개념}</h1>
    <section class="diagram">
      <h2>다이어그램 제목</h2>
      <svg viewBox="0 0 600 300" role="img" aria-label="설명"></svg>
      <div class="caption">한두 줄 캡션.</div>
    </section>
  </div>
</body>
</html>
```
