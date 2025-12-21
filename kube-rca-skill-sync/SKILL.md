---
name: kube-rca-skill-sync
description: |
  Use when refreshing or updating existing skills under skills/ to match the
  current code-kube-rca repository state, commands, and architecture. Triggers:
  requests to sync skill docs after repo changes, align skill descriptions with
  agent/backend/frontend/helm/terraform/full repositories, or validate that skill
  metadata reflects the current project layout.
---

# Kube-RCA Skill Sync

## Overview

Update existing skills in `skills/` so their descriptions, structure snippets,
and commands reflect the verified state of the code-kube-rca repositories.

## Workflow

1. Confirm the target skills list from the user; do not update other skills.
2. Map each target to its repository path and verify the path exists.
3. Collect current repo context with the script in `scripts/`.
4. Compare each target `SKILL.md` against the repo context and update only
   verified facts.
5. Read the updated files to ensure no TODO markers remain.
6. Record the changes in `LAST_AGENT_RUN.md`

## Target Mapping (default, verify before use)

- `kube-rca-backend` -> `backend/`
- `kube-rca-agent` -> `agent/`
- `kube-rca-frontend` -> `frontend/`
- `kube-rca-helm` -> `helm-charts/`
- `kube-rca-terraform` -> `terraform/`
- `kube-rca-full` -> repo root

If any path is missing, stop and ask for clarification.

## Repository Check Commands

Prefer direct inspection. Examples:

```bash
rg --files backend
rg --files agent
rg --files frontend
rg --files helm-charts
rg --files terraform
sed -n '1,200p' AGENTS.md
```

Never invent file names, commands, or resource identifiers. Only write what is
verified.

## Script: collect_repo_context.py

Generate a compact report per target skill to speed up updates.

```bash
python3 skills/kube-rca-skill-sync/scripts/collect_repo_context.py \
  --repo-root . \
  --skills-dir skills \
  --targets kube-rca-agent,kube-rca-backend,kube-rca-frontend
```

Read the report to confirm mapped paths, top-level entries, and verified files.

## Update Guidance

- Refresh `description` triggers to match current scope.
- Update project structure blocks only with verified paths.
- Keep commands aligned with `AGENTS.md` and actual files.
- Do not add features or roadmap items unless they exist in the repo.

## Definition of Done

- Ensure targets are updated and non-targets are untouched.
- Ensure no TODO markers remain in modified skills.
- Ensure `LAST_AGENT_RUN.md` are updated.
