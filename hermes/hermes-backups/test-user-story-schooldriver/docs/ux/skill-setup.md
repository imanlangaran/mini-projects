# UX/Design Profile — Skill Setup (Step 1)

- Date: 2026-08-31
- Profile: `ux-design` (`~/.hermes/profiles/ux-design/`)
- Basis: governance spec §3.7 + lifecycle Phase 2 tooling list
  (`sketch`/`claude-design` HTML mockups, `excalidraw` diagrams, `p5js`
  interactive prototypes, doc generation)

## Required set — final state

| Skill | Required for | State |
|---|---|---|
| `sketch` | HTML mockups / wireframes | ✅ installed, enabled (no change needed) |
| `claude-design` | HTML mockups / screen design | ✅ installed, enabled (no change needed) |
| `excalidraw` | hand-drawn-style flow diagrams | ✅ installed, enabled (no change needed) |
| `p5js` | interactive low-fi prototype | ✅ installed, enabled (no change needed) |
| doc generation (`docx`) | documents / sign-off package | ⬇️ **newly installed** (copied from `~/.hermes/profiles/myglobal/skills/productivity/docx`, v1.1.0) and enabled; verified present in profile (`skills/productivity/docx/SKILL.md`) |

All five verified enabled after the config change: none appear in the
profile's `skills.disabled` list; each has a valid `SKILL.md` on disk.

## Missing-skills list

| Skill | Status | Reason / what it will be used for | Resolution |
|---|---|---|---|
| `docx` (doc generation) | was missing from this profile | Gate-2 sign-off package and design documentation output | **Installed 2026-08-31** from the `myglobal` profile; enabled. No failure. |
| `hermes-railway-deployment` | not installed anywhere on this machine | Listed in the brief as an example of skills to *disable* — it is a deploy skill, not needed for UX/Design | Nothing to disable. Not installed. |
| `hermes-railway-deployment`, `test-driven-development`, `github-pr-workflow`, `architecture-diagram` (as *required* set) | n/a | These are Phase 3/5/6 skills (Architect/Implementer/QA). Per brief §b they are explicitly NOT needed for this role. | **Disabled** in this profile (see below). |

## Disabled (installed but not needed for the UX/Design role)

Disable rationale: keep the profile minimal to §3.7 — flow design,
wireframing, prototyping, doc generation. Everything coding/CI/deploy/DB/
Phase-1-requirements is off.

- **Explicitly named in the brief:** `test-driven-development`,
  `github-pr-workflow`, `architecture-diagram`
- **Other coding/CI/deploy:** `codebase-inspection`, `github-auth`,
  `github-code-review`, `github-issues`, `github-issue-to-pr`,
  `github-repo-management`, `dogfood`, `spike`, `plan`,
  `requesting-code-review`, `simplify-code`, `systematic-debugging`,
  `python-debugpy`, `node-inspect-debugger`,
  `inspecting-hermes-desktop-dom`, `hermes-agent-skill-authoring`,
  `sdlc-review`
- **Phase-1 requirements skills (Requirements agent's tools, not UX's):**
  `acceptance-criteria`, `elicitation-interview`,
  `elicitation-technique-selector`, `moscow-prioritization`,
  `quality-attribute`, `requirements-baselining`,
  `requirements-elicitation-workshop`, `requirements-phase`,
  `requirements-review-advisor`, `requirements-traceability`,
  `specification-review-checklist`, `stakeholder-analysis`,
  `user-story-re`, `vision-and-scope`, `writing-requirements`
- **Non-UX creative:** `ascii-art`, `ascii-video`, `baoyu-infographic`,
  `comfyui`, `design-md`, `humanizer`, `manim-video`, `pretext`,
  `popular-web-designs`, `songwriting-and-ai-music`, `touchdesigner-mcp`
- **Productivity/office (beyond docx):** `airtable`, `google-workspace`,
  `notion`, `obsidian`, `pdf`, `xlsx`, `powerpoint`, `nano-pdf`,
  `ocr-and-documents`, `document-to-action-items`, `meeting-action-items`,
  `maps`, `product-price-monitor`, `teams-meeting-pipeline`,
  `weekly-review-planning`
- **Research/data:** `arxiv`, `blogwatcher`, `competitor-news-monitor`,
  `grounded-citations`, `llm-wiki`, `polymarket`, `research-paper-writing`,
  `jupyter-live-kernel`
- **MLOps/infra:** `evaluating-llms-harness`, `weights-and-biases`,
  `huggingface-hub`, `llama-cpp`, `serving-llms-vllm`, `audiocraft`,
  `segment-anything`
- **Platforms/agents/misc:** `apple-notes`, `apple-reminders`, `findmy`,
  `imessage`, `openhue`, `himalaya`, `email-inbox-triage`,
  `gif-search`, `heartmula`, `songsee`, `youtube-content`, `xurl`,
  `claude-code`, `codex`, `computer-use`, `merge-reconciler`,
  `opencode`, `yuanbao`
- **Kept enabled beyond the strict five:** `hermes-agent` (agent
  self-configuration — needed to perform this very skill setup).

## Failures

None. Every step of the setup completed; no install failed, no workaround
needed.
