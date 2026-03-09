# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-09)

**Core value:** O vendedor abre o dashboard e sabe exatamente quem ligar hoje — ordenado por quem esta mais atrasado para comprar, com telefone e ticket medio na mesma tela.
**Current focus:** Phase 1 — Motor RMR

## Current Position

Phase: 1 of 3 (Motor RMR)
Plan: 3 of 3 in current phase (next: 01-03)
Status: In progress
Last activity: 2026-03-09 — Plan 01-02 completed: RMR engine with scores (19 new tests, 45 total passing)

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**
- Total plans completed: 2
- Average duration: 4 min
- Total execution time: 7 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 1 — Motor RMR | 2 | 7 min | 4 min |

**Recent Trend:**
- Last 5 plans: 2 min, 5 min
- Trend: baseline

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Streamlit + pandas em vez de HTML puro (quintis por PlayG sao complexos para JS)
- Quintis calculados separadamente por PlayG (comportamento de compra difere entre PGs)
- GAP como ordenacao principal da tabela (responde diretamente "quem ligar hoje")
- Limiares de GAP configuráveis via UI (permite ajuste sem alterar codigo)
- validate_columns usa alias map dict[str, list[str]] para normalização case-insensitive de colunas (01-01)
- Exclusão do PG1 via inner join em get_valid_transactions — mantém lógica DRY (01-01)
- Constantes COLUNAS_BASE_BU, COLUNAS_HISTORICO, TIPOS_VALIDOS, DATA_MINIMA no topo do módulo (01-01)
- Ritmo usa drop_duplicates em datas antes do diff — evita inflação de frequência por múltiplas transações no mesmo dia (01-02)
- assign_scores() como função separada — permite Plan 03 chamar independentemente sem recomputar agregações base (01-02)
- Inversão de scores via labels=[5,4,3,2,1] no pd.qcut — mais idiomático que reversão pós-cálculo (01-02)
- Clientes com Ritmo=NaN mantidos no DataFrame de saída — exclusão é responsabilidade do Plan 03 (01-02)

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-03-09
Stopped at: Completed 01-02-PLAN.md — RMR engine (src/rmr_engine.py, 45 tests passing)
Resume file: None
