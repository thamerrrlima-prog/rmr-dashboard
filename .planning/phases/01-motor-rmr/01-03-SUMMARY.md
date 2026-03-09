---
phase: 01-motor-rmr
plan: 03
subsystem: segmentation-and-ui
tags: [segmentation, streamlit, rmr, gap, tdd, pandas, pipeline]

requires:
  - phase: 01-motor-rmr/01-01
    provides: get_valid_transactions() returning filtered DataFrame
  - phase: 01-motor-rmr/01-02
    provides: compute_rmr() returning DataFrame with score_R, score_M, score_Ritmo, GAP

provides:
  - src/segmentation.py with classify_rmr_segment(), classify_gap_status(), apply_segmentation()
  - DEFAULT_GAP_THRESHOLDS exported for Fase 2 UI config
  - src/app.py Streamlit entrypoint connecting full upload → table pipeline

affects: [phase-2-dashboard-config, phase-3-export]

tech-stack:
  added: [streamlit]
  patterns: [TDD red-green, priority-ordered if/elif segment classification, NaN detection via math.isnan, session_state for recompute prevention]

key-files:
  created:
    - src/segmentation.py
    - src/app.py
    - tests/test_segmentation.py
  modified: []

key-decisions:
  - "Priority order: Campeões → Não Pode Perder → Leais → Novos Clientes → Potenciais Leais → Em Risco → Hibernando → Precisam Atenção — ensures Não Pode Perder takes precedence over Em Risco for R<=2,M=5"
  - "DEFAULT_GAP_THRESHOLDS exported as module-level constant — Fase 2 UI imports and overrides via user input without modifying segmentation.py"
  - "math.isnan() used instead of pd.isna() for pure float compatibility in row-level functions called via apply()"
  - "st.session_state stores result after calculation — prevents pipeline rerun on each UI interaction"
  - "Pipeline fully connected in app.py: load_base_bu + load_historico → get_valid_transactions → compute_rmr → apply_segmentation → st.dataframe"

patterns-established:
  - "classify_rmr_segment(row) receives pd.Series, checks NaN first, then applies priority-ordered conditions"
  - "classify_gap_status(gap_value, thresholds=None) is pure function with optional threshold override — Fase 2 passes user-configured thresholds"

requirements-completed: [RMR-08, RMR-09]

duration: 8min
completed: 2026-03-09
---

# Phase 1 Plan 03: Segmentation and Streamlit App Summary

**Priority-ordered 8-segment RMR classifier and 5-range GAP classifier, connected to a Streamlit entrypoint that takes two Excel uploads and renders the full client table.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-09T18:09:31Z
- **Completed:** 2026-03-09T18:17:51Z
- **Tasks:** 2 automated + 1 human-verify checkpoint
- **Files created:** 3

## Accomplishments

- `classify_rmr_segment(row)` applies 8 segments in documented priority order — Não Pode Perder (R<=2, M=5) correctly takes precedence over Em Risco
- `classify_gap_status(gap_value, thresholds)` classifies into 5 ranges using configurable thresholds, ready for Fase 2 UI override
- `apply_segmentation(rmr_df)` adds Segmento_RMR and Faixa_GAP columns; ineligible clients (NaN scores) receive "Inelegível" in both columns
- `src/app.py` closes the Phase 1 loop: user uploads two Excel files, clicks "Calcular RMR", sees full result table with all 13 columns
- 39 new tests; 84 total tests (45 from Plans 01-02 + 39 from Plan 03) all passing

## Task Commits

1. **Task 1 RED: Failing tests for segmentation** (TDD RED) — implicit in test file creation
2. **Task 1 GREEN: segmentation module** - `11dc7ad` (feat)
3. **Task 2: Streamlit app** - `e12cd1e` (feat)

## Files Created

- `src/segmentation.py` — `classify_rmr_segment()`, `classify_gap_status()`, `apply_segmentation()`, `DEFAULT_GAP_THRESHOLDS`
- `tests/test_segmentation.py` — 39 tests: segment classification (16), GAP ranges (17), apply_segmentation (6)
- `src/app.py` — Streamlit entrypoint with upload, pipeline call, session state, result table

## Decisions Made

1. **Priority order for segments**: Não Pode Perder comes before Leais and Em Risco in the if/elif chain — a client with R=2, M=5 must be "Não Pode Perder", not "Em Risco" (R<=2, M>=3 would also match Em Risco)
2. **DEFAULT_GAP_THRESHOLDS as exported constant**: Fase 2 will import this dict and let user override values in the UI without editing segmentation.py
3. **math.isnan over pd.isna**: Row-level functions called via apply() receive plain Python floats; math.isnan handles this without importing pandas in the check path
4. **st.session_state for result storage**: Prevents the expensive pipeline from re-running when user scrolls or interacts with the dataframe widget
5. **Pipeline fully in app.py**: No abstraction layer added between app.py and the module functions — Fase 2 will refactor if needed, keeping Phase 1 minimal

## Deviations from Plan

None — plan executed exactly as written.

## Checkpoint: Human Verification Required

**Status:** Awaiting human verification of the Streamlit app with real Excel files.

**To verify:**
1. `pip install -r requirements.txt`
2. `streamlit run src/app.py`
3. Open http://localhost:8501
4. Upload Base B.U. (.xlsx) and Histórico de Crédito (.xlsx)
5. Click "Calcular RMR"
6. Verify table shows all columns including Segmento_RMR and Faixa_GAP
7. Verify PG1 clients absent, single-purchase clients show "Inelegível"

## Self-Check

Files verified:
- `src/segmentation.py` — FOUND
- `src/app.py` — FOUND
- `tests/test_segmentation.py` — FOUND

Commits verified:
- `11dc7ad` — feat(01-03): implement segmentation (FOUND)
- `e12cd1e` — feat(01-03): add Streamlit entrypoint (FOUND)

Test results: 84 passed, 0 failed.

## Self-Check: PASSED

---
*Phase: 01-motor-rmr*
*Completed: 2026-03-09 (awaiting human-verify checkpoint)*
