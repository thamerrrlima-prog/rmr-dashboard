---
phase: 03-lista-de-prioridade-e-deploy
plan: "02"
subsystem: ui
tags: [streamlit, dark-theme, deploy, requirements, streamlit-cloud]

# Dependency graph
requires:
  - phase: 02-painel-analitico
    provides: Streamlit app structure (app.py, tabs, charts) that will receive the dark theme
provides:
  - Dark theme via .streamlit/config.toml (base = "dark", no custom CSS needed)
  - Clean requirements.txt with only runtime dependencies for Streamlit Cloud deploy
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - ".streamlit/config.toml committed to repo enables theme consistency without CSS overrides"
    - "requirements.txt contains runtime-only deps — dev tools (pytest) excluded for cloud deploy"

key-files:
  created:
    - .streamlit/config.toml
  modified:
    - requirements.txt

key-decisions:
  - "python-calamine kept in requirements.txt — _read_excel_robust() uses engine='calamine' as fallback in data_loader.py"
  - "pytest removed from requirements.txt — dev dependency not needed on Streamlit Cloud"
  - "[server] headless = true added to config.toml to suppress email prompt on Streamlit Cloud"

patterns-established:
  - "Streamlit theme config in .streamlit/config.toml — no custom CSS, base dark theme applied globally"

requirements-completed: [UI-01, UI-02, DEP-01]

# Metrics
duration: 1min
completed: 2026-03-09
---

# Phase 3 Plan 02: Dark Theme and Deploy Requirements Summary

**Streamlit dark theme via .streamlit/config.toml and clean runtime-only requirements.txt ready for Streamlit Cloud deploy**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-09T21:18:19Z
- **Completed:** 2026-03-09T21:19:07Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `.streamlit/config.toml` with `base = "dark"` applying dark theme across the entire app without any custom CSS
- Removed `pytest` from `requirements.txt` — only runtime dependencies remain for Streamlit Cloud
- Kept `python-calamine` after confirming it is used as a fallback engine in `_read_excel_robust()` in data_loader.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Criar .streamlit/config.toml com dark theme** - `9af1b56` (feat)
2. **Task 2: Verificar e finalizar requirements.txt para deploy no Streamlit Cloud** - `e447fb1` (chore)

## Files Created/Modified

- `.streamlit/config.toml` — Streamlit dark theme config: base dark, primaryColor #1f77b4, headless server mode
- `requirements.txt` — Runtime-only dependencies: streamlit, pandas, openpyxl, python-calamine, plotly

## Decisions Made

- **python-calamine retained:** `_read_excel_robust()` in `data_loader.py` (line 122) uses `engine="calamine"` as a fallback when openpyxl fails. Removing it would break file uploads with certain xlsx style issues.
- **pytest removed:** Dev-only dependency that Streamlit Cloud doesn't need and shouldn't install in production.
- **headless = true:** Added to `[server]` section to suppress the "enter email" prompt when deploying on Streamlit Cloud.

## Deviations from Plan

None — plan executed exactly as written. The plan itself specified: "Remover python-calamine apenas se confirmar que não é usado em data_loader.py. Se for usado, mantê-lo." — it was used, so it was kept.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `.streamlit/config.toml` committed and trackable by git — ready for Streamlit Cloud deployment
- `requirements.txt` contains only runtime dependencies — Streamlit Cloud will install exactly what is needed
- Both files ready for the deployment step (03-03 or similar)

---
*Phase: 03-lista-de-prioridade-e-deploy*
*Completed: 2026-03-09*
