# Retrospective: RMR Dashboard — LigueLead

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-09
**Phases:** 3 | **Plans:** 10

### What Was Built

- Pandas xlsx ingestion pipeline with 4-stage chained filters and case-insensitive column normalization
- Per-PlayG quintil RMR scoring engine (Recência/Monetário/Ritmo/GAP) with NaN propagation for single-purchase clients
- 8-segment RMR classifier + 5-range configurable GAP classifier connected to Streamlit entrypoint
- Painel Analítico: reactive GAP sliders, 4 KPI cards, horizontal segment chart, dual-bar GAP histogram
- Receita Projetada: semanal ±5-day window + 30/60/90-day strategic projections
- Tab Lista de Prioridade: GAP-sorted contact table with multi-axis filters, dark theme, Streamlit Cloud deploy

### What Worked

- **TDD discipline** — red-green cycle on every module kept code correct from first run; 84 tests gave confidence to refactor during Phase 3 restructuring without regressions
- **Modular architecture** — `data_loader → rmr_engine → segmentation → app.py` separation made per-plan execution clean and each plan independently testable
- **NaN propagation strategy** — deciding early (01-02) to keep ineligible clients in the DataFrame instead of filtering them out made segment classification and display logic cleaner downstream
- **session_state split** (rmr_df vs rmr_result) — separating the expensive computation result from the display slice eliminated all recompute-on-slider-change issues in one decision

### What Was Inefficient

- **ROADMAP status not updated in real time** — ROADMAP.md showed Phases 2 and 3 as incomplete even after all plans finished; traceability table in REQUIREMENTS.md was stale with "Pending" rows that were actually complete
- **Plan count mismatch** — Phase 2 originally had 3 plans but a gap-closure plan (02-04) was inserted mid-milestone to address VIZ-02 and VIZ-04; planning didn't anticipate the visualization scope needed
- **VIZ-03 (heatmap)** — planned but removed by user decision during execution; could have been identified as lower priority during phase planning to avoid scope churn

### Patterns Established

- `groupby('PlayG').transform(lambda x: pd.qcut(..., duplicates='drop'))` — per-group quintil scoring pattern, resilient to small groups
- `classify_rmr_segment(row)` with priority-ordered if/elif — segment priority order documented and enforced structurally
- `calcular_projecao()` with Ritmo > 0 guard — division-by-zero prevention pattern for per-client revenue projection
- Tab structure always visible (no conditional on session_state) — orientation messages per tab on empty state instead

### Key Lessons

- Define visualization requirements (chart type + dual-series vs single) precisely in phase planning — "barras de distribuição" is ambiguous between a table and a chart
- Gap-closure plans (like 02-04) are a natural output of verification; budget 1 plan per phase for corrections
- `st.rerun()` must be guarded against threshold equality to avoid infinite rerun loops — document this pattern in any Streamlit phase plan
- Streamlit Cloud runtime dependencies must be audited before deploy — pytest in requirements.txt caused unnecessary payload

### Cost Observations

- Sessions: ~6 execution sessions across 1 day
- Notable: all 10 plans completed in a single day; TDD cycles averaged 2-8 min each

---

## Cross-Milestone Trends

| Milestone | Phases | Plans | LOC | Tests | Days |
|-----------|--------|-------|-----|-------|------|
| v1.0 MVP | 3 | 10 | 1,779 | 84 | 1 |
