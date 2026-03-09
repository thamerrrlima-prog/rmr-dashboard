---
phase: 01-motor-rmr
plan: 02
subsystem: rmr-engine
tags: [rmr, pandas, quintis, scoring, tdd, groupby, qcut]

requires:
  - phase: 01-motor-rmr/01-01
    provides: get_valid_transactions() returning DataFrame with [ID, Nome, PlayG, Telefone, Tipo, Valor, Data]
provides:
  - src/rmr_engine.py with compute_rmr(valid_df, reference_date) -> DataFrame
  - assign_scores(rmr_df) as separate callable
  - Full RMR metrics: Recencia, Monetario, Ritmo, GAP (int/float/NaN)
  - Quintil scores: score_R, score_M, score_Ritmo (1-5 or NaN)
affects: [phase-1-plan-03-segmentacao, phase-2-dashboard]

tech-stack:
  added: []
  patterns: [TDD red-green, groupby-transform qcut for per-group quintils, inversion via reversed labels, unique-date diff for rhythm]

key-files:
  created:
    - src/rmr_engine.py
    - tests/test_rmr_engine.py
  modified: []

key-decisions:
  - "Ritmo uses drop_duplicates on dates before diff — prevents same-day transactions from inflating purchase frequency"
  - "assign_scores() is a separate callable to allow standalone use by Plan 03 without recomputing base metrics"
  - "Score inversion via labels=[5,4,3,2,1] in pd.qcut — cleaner than post-hoc reversal (6 - score)"
  - "Clients with Ritmo=NaN kept in output DataFrame — exclusion is Plan 03's responsibility, not the engine's"
  - "duplicates='drop' in qcut handles small PlayG groups gracefully without raising ValueError"

patterns-established:
  - "groupby('PlayG').transform(lambda x: pd.qcut(...)) for per-group quintil scoring"
  - "NaN propagation: ineligible clients initialize to NaN, only eligible rows get scores overwritten"

requirements-completed: [RMR-01, RMR-02, RMR-03, RMR-04, RMR-05, RMR-06, RMR-07]

duration: 5min
completed: 2026-03-09
---

# Phase 1 Plan 02: RMR Engine Summary

**Pandas RMR scoring engine computing Recencia/Monetario/Ritmo/GAP with per-PlayG quintil scores (1-5), inversion for R and Ritmo, and NaN propagation for single-purchase clients.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-09T17:03:15Z
- **Completed:** 2026-03-09T17:08:00Z
- **Tasks:** 2 (TDD: 3 commits — RED, GREEN tasks combined)
- **Files modified:** 2

## Accomplishments

- `compute_rmr(valid_df, reference_date=None)` consumes the output of Plan 01's `get_valid_transactions()` and returns a fully scored DataFrame indexed by client ID
- Ritmo calculation uses deduplicated dates (drop_duplicates before diff) to avoid inflating purchase frequency when multiple transactions share a date
- Quintil scoring via `groupby('PlayG').transform(pd.qcut)` ensures scores are calculated independently per PlayG, with `duplicates='drop'` for resilience with small groups
- 19 new tests covering all behavioral requirements; 45 total tests (26 Plan 01 + 19 Plan 02) all passing

## Task Commits

Each TDD cycle committed atomically:

1. **Task 1 RED: Failing tests for R, M, Ritmo, GAP, scores** - `bf1f460` (test)
2. **Task 1+2 GREEN: Full rmr_engine implementation** - `df37462` (feat)

_Note: Tasks 1 and 2 GREEN phases were combined into a single implementation commit since `compute_rmr` calls `assign_scores` internally — both behaviors implemented and verified together._

## Files Created/Modified

- `src/rmr_engine.py` — `compute_rmr()` and `assign_scores()` with full docstrings
- `tests/test_rmr_engine.py` — 19 tests: `TestRMRBasico` (9), `TestScores` (9), `test_rmr_basico` (1)

## Decisions Made

1. **Ritmo deduplication**: `drop_duplicates()` on dates before `diff()` — prevents inflated rhythms when a client makes multiple transactions on the same day (e.g., 2 transactions on Jan 1 + 1 on Jan 11 → Ritmo=10.0, not 5.0)
2. **assign_scores as separate function**: Allows Plan 03 to call it independently after filtering, without re-running the expensive aggregations
3. **Inversion via reversed labels**: `labels=[5,4,3,2,1]` passed directly to `pd.qcut` — more idiomatic than post-hoc `6 - score`
4. **NaN clients in output**: Clients with 1 distinct purchase date remain in the returned DataFrame with `Ritmo=NaN`, `GAP=NaN`, `score_*=NaN` — Plan 03 decides what to do with them (segment as "new clients", show separately, etc.)
5. **duplicates='drop' in qcut**: Handles PlayG groups with < 5 distinct values gracefully; documented in docstring

## Deviations from Plan

None — plan executed exactly as written. Both tasks implemented in a single GREEN commit since the scoring (Task 2) is called from within `compute_rmr` (Task 1), making them inseparable in a clean implementation.

## Issues Encountered

None. All 19 tests passed on first run after implementation.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `src/rmr_engine.py` exports `compute_rmr(valid_df, reference_date)` — ready for Plan 03 segmentation
- DataFrame output is indexed by ID with `[Nome, PlayG, Telefone, Recencia, Monetario, Ritmo, GAP, score_R, score_M, score_Ritmo]`
- `assign_scores()` is also available independently for Plan 03 if re-scoring after filtering is needed
- Single-purchase clients have `score_*=NaN` — Plan 03 can filter or handle them distinctly

---
*Phase: 01-motor-rmr*
*Completed: 2026-03-09*
