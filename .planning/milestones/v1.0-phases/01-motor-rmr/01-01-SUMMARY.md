---
phase: 01-motor-rmr
plan: 01
subsystem: data-ingestion
tags: [data-loader, pandas, xlsx, filtering, tdd]
dependency_graph:
  requires: []
  provides: [src/data_loader.py, load_base_bu, load_historico, get_valid_transactions, validate_columns]
  affects: [phase-1-rmr-engine, phase-2-dashboard]
tech_stack:
  added: [pandas>=2.1.0, openpyxl>=3.1.0, pytest>=7.0.0]
  patterns: [TDD red-green, canonical column mapping, inner-join for PG1 exclusion]
key_files:
  created:
    - src/__init__.py
    - src/data_loader.py
    - tests/__init__.py
    - tests/test_data_loader.py
    - requirements.txt
  modified: []
decisions:
  - validate_columns uses alias map (dict[str, list[str]]) for case-insensitive column normalization
  - PG1 exclusion via inner join in get_valid_transactions (not explicit filter) — keeps logic DRY
  - DATA_MINIMA and TIPOS_VALIDOS as module-level constants for easy maintenance
metrics:
  duration: 2 minutes
  completed: 2026-03-09
  tasks_completed: 2
  files_created: 5
  tests_count: 26
---

# Phase 1 Plan 01: Data Ingestion Layer Summary

**One-liner:** Pandas-based xlsx ingestion pipeline with alias-mapped column normalization, chained transaction filters (type/value/date/PG1), and 26 pytest tests covering all filter paths.

## What Was Built

`src/data_loader.py` implements the complete data ingestion layer for the RMR Dashboard:

- `load_base_bu(file)`: reads Base B.U. xlsx (path or BytesIO), normalizes columns via alias map, excludes PG1 clients
- `load_historico(file)`: reads Historico de Credito xlsx, normalizes columns, parses dates to datetime, coerces values to numeric
- `get_valid_transactions(base_df, hist_df)`: chains four filters (tipo IN [Nova Compra, Pagamento], valor > 0, data >= 2024-01-01, inner join with base_df) returning a clean DataFrame ready for RMR calculations
- `validate_columns(df, canonical_map, filename_hint)`: case-insensitive alias matching with descriptive ValueError on missing required columns

`tests/test_data_loader.py` has 26 tests organized in 5 test classes covering all filter paths and edge cases.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | TDD failing tests | c368e27 | tests/test_data_loader.py, tests/__init__.py, requirements.txt |
| 1 (GREEN) | data_loader implementation | cf60574 | src/data_loader.py, src/__init__.py |
| 2 | Column validation tests | a447d02 | tests/test_data_loader.py |

## Deviations from Plan

None — plan executed exactly as written. `validate_columns` was implemented as part of Task 1 (TDD cycle) since its tests were included in the behavior spec; Task 2 added the additional `TestColunaRenomeada` integration tests as specified.

## Decisions Made

1. **alias map pattern for validate_columns**: `dict[str, list[str]]` (canonical -> aliases) gives extensibility without regex complexity
2. **PG1 exclusion via inner join**: `get_valid_transactions` excludes PG1 implicitly through the inner join with `base_df` (already filtered), keeping the logic DRY
3. **Module-level constants** `COLUNAS_BASE_BU`, `COLUNAS_HISTORICO`, `TIPOS_VALIDOS`, `DATA_MINIMA`: facilitates maintenance and future configuration

## Test Results

```
26 passed in 0.32s
```

All filter paths verified:
- "Troca de Credito" and "Bonus/Desconto" discarded
- Valor = 0 discarded
- Data 2023-12-31 discarded
- PG1 client (ID=3) not in result
- "Nova Compra" 500.0 2024-06-01 kept
- "Pagamento" valid kept
- Columns [ID, Nome, PlayG, Telefone, Tipo, Valor] all present in result

## Self-Check: PASSED
