# 옵시디언 비동기 내보내기 (v2)

세션 종료 처리의 마지막 단계. **반드시 백그라운드로 실행**하여 현재 세션을 블로킹하지 않는다.

## Vault 경로

`~/Downloads/Obsidian Vault/`

## 내보내기 구조 (v2 — domain 레이어 추가)

```
Obsidian Vault/
└── 공부/
    └── {domain}/                    # tech | system-design | softskill | process
        └── {대주제}/
            └── {소주제}/
                └── {개념}.md
```

- `~/git/study/{대주제}/{소주제}/concepts/*.md` → `Obsidian Vault/공부/{domain}/{대주제}/{소주제}/*.md`
- **`meta/*.json`은 export 대상에서 제외** — study repo 전용 (FSRS·confidence·bloom 동적 메타)
- `practice/`, `diagrams/*.html`, `scenarios/*.md`, `checklists/*.md`는 export 안 함 (옵시디언에서 불필요)

## domain 추출

각 `concepts/{개념}.md` 파일의 frontmatter `domain:` 필드에서 추출. frontmatter가 없거나 domain 미정인 경우는 디렉토리 추정 폴백:
- `claude-code/`, `codex/`, `dev-tools/`, `ai-ml/`, `software-testing/` → `tech`
- `harness-engineering/`, `observability/` → `process`
- (그 외) → `tech` (가장 안전한 기본값)

## 내보내기 방식

**Bash `run_in_background: true`** 로 실행한다. 처리 흐름:

```bash
OBSIDIAN_VAULT="$HOME/Downloads/Obsidian Vault"

for concept_md in ~/git/study/{대주제}/{소주제}/concepts/*.md; do
  filename=$(basename "$concept_md")

  # 1. frontmatter에서 domain 추출 (없으면 추정 폴백)
  domain=$(awk '/^---$/{n++; next} n==1 && /^domain:/{print $2; exit}' "$concept_md")
  domain=${domain:-tech}

  # 2. 대상 디렉토리 생성
  target_dir="$OBSIDIAN_VAULT/공부/$domain/{대주제}/{소주제}"
  mkdir -p "$target_dir"
  target="$target_dir/$filename"

  # 3. frontmatter 처리
  if head -1 "$concept_md" | grep -q "^---$"; then
    # 이미 v2 frontmatter 있으면 그대로 통과 + 옵시디언 태그만 보강
    cp "$concept_md" "$target"
    # 옵시디언 태그를 frontmatter 안에 추가 (date, tags, source)
    # — frontmatter 끝(`---`) 직전에 obsidian 전용 필드 삽입
  else
    # frontmatter 없으면 자동 생성 후 본문 append (v1 폴백)
    {
      echo "---"
      echo "date: $(date +%Y-%m-%d)"
      echo "domain: $domain"
      echo "tags:"
      echo "  - 공부"
      echo "  - $domain"
      echo "  - {대주제}"
      echo "  - {소주제}"
      echo "source: claude-code-study"
      echo "---"
      echo ""
      cat "$concept_md"
    } > "$target"
  fi
done
```

(스크립트는 구현 시점에 위 흐름을 따르되, frontmatter 보강 부분은 sed/awk로 정밀하게 — `---` 라인 위치 찾고 그 직전에 obsidian-specific 키 삽입.)

## 규칙

1. **비동기 필수**: `run_in_background: true`로 실행. 사용자에게 "옵시디언에 내보내기 시작했습니다" 메시지만 출력하고 즉시 다음으로 넘어간다.
2. **덮어쓰기**: 같은 파일이 이미 있으면 최신 내용으로 덮어쓴다.
3. **frontmatter 통과 + 옵시디언 보강**: v2 frontmatter(domain·bloom_level·prerequisites·references 등)는 그대로 유지. 옵시디언 검색용 `date`, `tags`, `source`는 추가로 삽입 (중복 키는 옵시디언이 처리).
4. **meta/JSON 제외**: 명시적으로 `concepts/` 디렉토리만 스캔. `meta/`는 옵시디언으로 가지 않는다.
5. **실패 무시**: 내보내기 실패해도 학습 세션 자체에 영향 없음. 에러가 나면 다음 세션에서 재시도.
6. **Quick Explain도 포함**: Quick Explain 모드로 `concepts/`에 파일이 생성되었으면 동일하게 내보내기 수행.

## domain 폴더 마이그레이션

기존 옵시디언 Vault에 `공부/{대주제}/...` 구조로 이미 export된 파일이 있다면:
- v2 첫 실행 시 자동 이전하지 않음 — 사용자가 수동 정리 권장
- 신규 export부터 `공부/{domain}/{대주제}/...` 구조로 들어감
- 기존 파일은 그대로 두거나 사용자가 mv

## 옵시디언 태그 활용 예

옵시디언에서 도메인별 검색:
- `tag:#tech` — 기술 학습만
- `tag:#system-design` — 설계 학습만
- `tag:#softskill` — 소프트스킬 학습만

dataview 쿼리 예 (옵시디언 dataview 플러그인):
```dataview
TABLE bloom_achieved_max as "도달레벨", updated as "마지막학습"
FROM "공부/tech"
SORT updated DESC
```
