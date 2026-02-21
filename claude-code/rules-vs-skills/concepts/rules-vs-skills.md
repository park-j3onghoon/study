# Claude Code: Rules vs Skills

## 한줄 요약

- **Rules** = "뭘 할 수 있는지" (보안/권한 게이트)
- **Skills** = "어떻게 잘 할 수 있는지" (지식/워크플로우 확장)

---

## 1. Rules (규칙)

### 정의
Claude Code가 **어떤 도구를 사용할 수 있는지** 제어하는 **권한 시스템**.

### 비유
건물의 **출입 카드 시스템**과 같다.
- `allow` = 자유 출입 가능한 구역 (카드 찍으면 바로 열림)
- `ask` = 방문 승인이 필요한 구역 (매번 확인)
- `deny` = 출입 금지 구역 (절대 못 들어감)

### 핵심 특징
| 항목 | 설명 |
|------|------|
| **파일 형식** | JSON (`settings.json`) |
| **적용 시점** | 도구 사용할 때마다 **자동 평가** |
| **역할** | 허용/차단/확인 (보안 게이트) |
| **우선순위** | deny > ask > allow |

### 설정 예시

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "Bash(npm run test)",
      "Read(src/**)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(.env)"
    ]
  }
}
```

### 스코프 (적용 범위) — 우선순위 순

```
Managed (조직 전체)        ← 최우선, 관리자가 강제
  ↓
Local Project              ← .claude/settings.local.json (개인, git 무시)
  ↓
Project                    ← .claude/settings.json (팀 공유, git 추적)
  ↓
User                       ← ~/.claude/settings.json (내 모든 프로젝트)
```

---

## 2. Skills (스킬)

### 정의
Claude Code의 **능력을 확장**하는 **지식 패키지 + 커스텀 명령어**.

### 비유
직원에게 주는 **업무 매뉴얼/SOP**와 같다.
- Rules가 "이 방에 들어갈 수 있는지"를 결정한다면
- Skills는 "방에 들어가서 무엇을 어떻게 해야 하는지"를 알려준다

### 핵심 특징
| 항목 | 설명 |
|------|------|
| **파일 형식** | Markdown + YAML frontmatter (`SKILL.md`) |
| **적용 시점** | `/skill-name`으로 호출하거나, 관련성 있으면 자동 발동 |
| **역할** | 지시/지식 제공 (워크플로우 확장) |
| **권한 제어** | 불가능 (도구 차단/허용 못함) |

### SKILL.md 예시

```yaml
---
name: deploy
description: 프로덕션 배포 워크플로우
user-invocable: true
allowed-tools: Bash, Read
---

# 배포 절차
1. 테스트 실행
2. 빌드
3. 배포 스크립트 실행
```

### 스코프

```
Project 스킬               ← .claude/skills/<name>/SKILL.md (팀 공유)
  ↓
User 스킬                  ← ~/.claude/skills/<name>/SKILL.md (개인)
```

---

## 3. 핵심 차이 비교

```
┌─────────────┬──────────────────────┬──────────────────────┐
│             │      Rules           │      Skills          │
├─────────────┼──────────────────────┼──────────────────────┤
│ 목적        │ 권한 제어 (보안)     │ 능력 확장 (생산성)   │
│ 파일        │ settings.json        │ SKILL.md             │
│ 형식        │ JSON                 │ YAML + Markdown      │
│ 발동        │ 자동 (매 도구 사용)  │ 수동(/cmd) 또는 자동 │
│ 도구 차단   │ ✅ 가능              │ ❌ 불가              │
│ 도구 허용   │ ✅ 가능              │ ❌ 불가              │
│ 지식 제공   │ ❌ 불가              │ ✅ 가능              │
│ 워크플로우  │ ❌ 불가              │ ✅ 가능              │
└─────────────┴──────────────────────┴──────────────────────┘
```

---

## 4. 실제 파일 구조

### 이 프로젝트(study)의 예시

```
~/git/study/.claude/
├── settings.local.json              ← Rules (권한 설정)
│   └── allow: WebSearch, git push 등
│
└── skills/
    └── study/                       ← Skill (학습 스킬)
        ├── SKILL.md                 ← 스킬 본체 (발동 조건, 플로우 정의)
        └── guides/                  ← 스킬 내부 참조 문서
            ├── logging.md
            ├── weakness.md
            └── session-end.md
```

### 일반적인 프로젝트 구조

```
my-project/
├── .claude/
│   ├── settings.json                ← Project Rules (팀 공유, git 추적)
│   ├── settings.local.json          ← Local Rules (개인, git 무시)
│   └── skills/
│       ├── deploy/
│       │   └── SKILL.md             ← 배포 스킬
│       ├── review/
│       │   └── SKILL.md             ← 코드 리뷰 스킬
│       └── test/
│           └── SKILL.md             ← 테스트 스킬

~/.claude/
├── settings.json                    ← User Rules (모든 프로젝트 적용)
└── skills/
    └── my-personal-skill/
        └── SKILL.md                 ← 개인 스킬 (모든 프로젝트 적용)
```

---

## 5. 참고 문서
- [Claude Code Skills 공식 문서](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code Settings/Permissions 공식 문서](https://docs.anthropic.com/en/docs/claude-code/settings)
