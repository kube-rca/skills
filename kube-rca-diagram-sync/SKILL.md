---
name: kube-rca-diagram-sync
description: |
  Keep Mermaid diagrams under .github/diagrams and the .github docs
  (.github/README.md, .github/PROJECT.md) aligned with the target
  code-kube-rca architecture and team goals (to-be).
  Use when revising target architecture, adding planned components,
  or changing integration paths between backend, agent, frontend, and infra.
---

# Kube-RCA Diagram Sync

## Overview

Update Mermaid diagrams under .github/diagrams and the .github docs to express
the to-be architecture that aligns the team. Use current implementation
signals only to label what is already built, not to block target design.

## Source of Truth

- .github/PROJECT.md for goals, scope, and roadmap (to-be)
- .github/ARCHITECTURE.md for current runtime flow (as-is)
- backend/main.go and backend/internal/ for implemented endpoints and Slack integration
- agent/main.go and agent/internal/ for analysis service endpoints
- frontend/src/App.tsx for whether UI uses mock data or backend APIs
- helm-charts/ and k8s-resources/ when diagrams cover deployment topology

## Files to Update

- .github/diagrams/system_context_diagram.md
- .github/diagrams/sequence_diagram.md
- .github/diagrams/entity_relationship_diagram.md
- .github/README.md
- .github/PROJECT.md

## Diagram Update Workflow

1. Review .github/PROJECT.md for target scope, then check .github/ARCHITECTURE.md
   and code to identify what is already implemented.
2. Decide which components are to-be versus implemented; mark planned items
   explicitly (label or note).
3. Update each diagram:
   - .github/diagrams/system_context_diagram.md: show target services and
     external systems; label planned components.
   - .github/diagrams/sequence_diagram.md: reflect target flow; label planned
     steps or integrations.
   - .github/diagrams/entity_relationship_diagram.md: include target data
     models; label planned storage if not implemented.
4. Update .github/README.md and .github/PROJECT.md to clarify to-be scope.
   - Keep "implemented" versus "planned" clearly separated.
   - Avoid implying planned items are already shipped.
5. Keep Mermaid syntax valid and fenced as mermaid code blocks.
6. Re-check diagrams in GitHub preview for rendering and consistency.

## Consistency Checks

- Use the same component names across diagrams.
- Align terminology with .github/PROJECT.md and .github/ARCHITECTURE.md.
- Label planned items so readers can distinguish to-be from implemented.
- Ensure README/PROJECT use the same names as diagrams and ARCHITECTURE.md.
