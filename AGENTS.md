## Skills
A skill is a set of local instructions stored in a `SKILL.md` file.

### Available skills
- `skill-creator`: Guide for creating or updating Codex skills. (file: `/Users/teddy.park/.codex/skills/.system/skill-creator/SKILL.md`)
- `skill-installer`: Install skills into `$CODEX_HOME/skills`. (file: `/Users/teddy.park/.codex/skills/.system/skill-installer/SKILL.md`)
- `study`: 3-step Korean learning workflow (Explain -> Execute -> Quiz). Trigger when users ask to study or ask curiosity/explanation questions. (file: `/Users/teddy.park/git/study/.codex/skills/study/SKILL.md`)

### How to use skills
- If the user explicitly names a skill, use it.
- If a request clearly matches a skill description, use that skill even without explicit naming.
- Read only the minimum required files for the task; for `study`, load only needed files under `guides/`.

### Local preferences (migrated from `.claude/settings.local.json`)
- Prefer official docs via web lookup when explaining technical topics.
- Commonly expected shell commands for study sessions: `wc`, `mkdir`, `git add`, `git commit`, `git push`.
- Follow Codex sandbox/approval rules before running commands.
