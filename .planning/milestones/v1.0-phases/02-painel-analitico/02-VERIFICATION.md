---
phase: 02-painel-analitico
verified: 2026-03-09T20:30:00Z
status: human_needed
score: 11/11 must-haves verified
re_verification: true
  previous_status: gaps_found
  previous_score: 9/11
  gaps_closed:
    - "VIZ-02: Distribuicao por segmento RMR agora renderiza como px.bar horizontal com colunas Clientes e Receita (Monetario.sum()) por segmento — st.dataframe removido (commit bc662d7)"
    - "VIZ-04: Histograma de GAP por faixas agora exibe dois grupos por faixa (Clientes e Receita) com barmode='group' usando .melt() para formato longo (commit 511d262)"
    - "Truth 'Todos os valores refletem result_df corrente' promovida para VERIFIED — VIZ-03 e' decisao de usuario, nao lacuna tecnica"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Alterar slider 'Critico' para -50 e verificar que KPIs, grafico de segmentos, histograma de GAP e receita semanal atualizam sem recarregar a pagina"
    expected: "Todos os numeros no Painel e Receita mudam imediatamente apos ajuste do slider"
    why_human: "Comportamento de rerun/reatividade do Streamlit nao pode ser verificado estaticamente"
  - test: "Abrir Tab Receita com dados reais (Monetario > 1000) e verificar que os valores monetarios usam ponto como separador de milhar"
    expected: "Formato 'R$ X.XXX' com ponto, nao virgula (ex: R$ 1.234 nao R$ 1,234)"
    why_human: "A substituicao .replace(',', '.') esta presente no codigo (linhas 109, 224, 259-261) mas rendering final depende do browser"
  - test: "Abrir Tab Painel com dados reais e verificar que o grafico horizontal de segmentos exibe Campeoes no topo e Precisam Atencao na base"
    expected: "Ordem visual de cima para baixo: Campeoes, Nao Pode Perder, Leais, Novos Clientes, Potenciais Leais, Em Risco, Hibernando, Precisam Atencao"
    why_human: "Ordem de exibicao do eixo Y em graficos Plotly (categoryorder) nao pode ser verificada por analise estatica"
---

# Phase 2: Painel Analitico — Verification Report (Re-verification)

**Phase Goal:** O vendedor ve KPIs, graficos e projecoes de receita — tudo recalculando em tempo real ao ajustar os limiares de GAP
**Verified:** 2026-03-09T20:30:00Z
**Status:** human_needed
**Re-verification:** Yes — after gap closure (plans 02-04 closed VIZ-02 and VIZ-04)

## Re-verification Summary

Previous verification (2026-03-09T17:00:00Z) found 2 gaps:

1. VIZ-02: Segment distribution was a plain `st.dataframe` with client counts only — required `px.bar` horizontal with receita column. **Closed by commit `bc662d7`.**
2. VIZ-04: GAP histogram showed only client counts — required grouped bars with receita per faixa. **Closed by commit `511d262`.**

VIZ-03 (heatmap R x Ritmo) was flagged in the previous verification but is correctly classified as **intentionally deferred** — the user explicitly discarded it in CONTEXT.md ("Heatmap R x Ritmo — descartado pelo usuario (nao necessario para v1)"). It is not a gap.

No regressions found: all 84 tests pass, syntax valid, all previously verified items remain intact.

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | Cards de KPI exibem total de clientes no RMR, percentual com GAP negativo, receita em risco e ritmo medio | VERIFIED | Lines 106-110: c1-c4.metric() with values from elegíveis |
| 2 | Dashboard mostra distribuicao por segmento RMR como barras horizontais com clientes e receita por segmento | VERIFIED | Lines 130-155: px.bar orientation="h", groupby().agg(Clientes, Receita), st.caption with receita text |
| 3 | Dashboard mostra histograma de GAP por faixas com dois grupos por faixa (clientes e receita) | VERIFIED | Lines 169-205: groupby Faixa_GAP, .melt(), px.bar barmode="group", two series Clientes and Receita |
| 4 | Usuario altera limiar de GAP e todos os graficos/KPIs atualizam imediatamente sem recarregar a pagina | VERIFIED (human needed) | Lines 306-311: new_thresholds != session_state["gap_thresholds"] -> apply_segmentation -> st.rerun() |
| 5 | Bloco de receita projetada exibe valor semanal (GAP -5 a +5) e projecoes para 30, 60 e 90 dias | VERIFIED | Lines 217-261: semanal_mask + calcular_projecao() + proj_30/60/90 metrics |
| 6 | App.py armazena rmr_df (pre-segmentacao) e rmr_result separados no session_state | VERIFIED | Lines 69, 72-74: session_state["rmr_df"] and session_state["rmr_result"] stored and used separately |
| 7 | Interface exibe 3 tabs: Painel, Receita, Configuracao | VERIFIED | Line 95: st.tabs(["Painel", "Receita", "Configuração"]) |
| 8 | Tab Configuracao exibe 4 sliders de limiares de GAP inicializados com DEFAULT_GAP_THRESHOLDS | VERIFIED | Lines 274-297: 4 sliders (critico_max, atrasado_max, hora_max, em_breve_max) |
| 9 | Alterar qualquer slider recalcula apply_segmentation sem re-executar compute_rmr | VERIFIED | Lines 306-311: compare new_thresholds -> update session_state -> apply_segmentation(rmr_df, ...) -> st.rerun() |
| 10 | Tab Receita exibe bloco semanal: receita potencial e n clientes com GAP entre -5 e +5 | VERIFIED | Lines 217-235: semanal_mask, 2 metrics, sortable dataframe |
| 11 | Projecao por cliente calculada como ticket_medio x floor(periodo / ritmo) | VERIFIED | Lines 249-252: calcular_projecao() uses int(periodo/Ritmo) equivalent to floor for positive values |

**Score:** 11/11 truths verified (VIZ-03 heatmap intentionally absent per user decision — not counted as a truth)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/app.py` | Entrypoint com tabs, session_state split, recalculo de segmentacao por limiares | VERIFIED | 311 lines, syntax valid (ast.parse OK), all major sections present |
| `src/app.py` (tab_painel KPIs) | 4 st.metric cards calculados sobre elegíveis | VERIFIED | Lines 106-110: c1.metric through c4.metric with computed values |
| `src/app.py` (tab_painel VIZ-02) | px.bar horizontal com Clientes e Receita por segmento | VERIFIED | Lines 119-155: groupby().agg(Clientes, Receita), orientation="h", fig_seg, caption |
| `src/app.py` (tab_painel VIZ-04) | Histograma GAP com barmode='group', dois grupos por faixa | VERIFIED | Lines 169-205: groupby Faixa_GAP, .melt(), barmode="group", fig_gap |
| `src/app.py` (tab_receita) | Receita semanal + projecao 30/60/90 dias | VERIFIED | Lines 207-266: both blocks substantive and wired |
| `src/app.py` (tab_config) | 4 sliders com recalculo automatico | VERIFIED | Lines 268-311: 4 sliders, threshold comparison, apply_segmentation, st.rerun() |
| VIZ-03 heatmap | Intentionally absent | DEFERRED | User decision: "descartado pelo usuario (nao necessario para v1)" — CONTEXT.md deferred section |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Tab Configuracao sliders | session_state['rmr_result'] | apply_segmentation(session_state['rmr_df'], new_thresholds) | WIRED | Line 308-310: exact pattern present |
| src/app.py | src/segmentation.py | from src.segmentation import apply_segmentation, DEFAULT_GAP_THRESHOLDS | WIRED | Line 17: import confirmed |
| Tab Painel (KPIs) | session_state['rmr_result'] | result_df = st.session_state["rmr_result"] | WIRED | Line 98: exact assignment |
| seg_data (VIZ-02) | elegíveis['Monetario'] | groupby("Segmento_RMR").agg(Receita=("Monetario","sum")) | WIRED | Lines 120-125: agg with Receita sum confirmed |
| fig_seg (VIZ-02) | px.bar orientation="h" | px.bar(..., orientation="h") | WIRED | Line 130-138: orientation="h" confirmed |
| gap_data (VIZ-04) | elegíveis['Monetario'] | groupby("Faixa_GAP").agg(Receita=("Monetario","sum")) | WIRED | Lines 169-175: agg with Receita sum confirmed |
| gap_long (VIZ-04) | barmode="group" | .melt() then px.bar barmode="group" | WIRED | Lines 179-191: .melt() and barmode="group" confirmed |
| Tab Receita (semanal) | elegíveis com GAP entre -5 e +5 | (elegíveis['GAP'] >= -5) & (elegíveis['GAP'] <= 5) | WIRED | Line 217: exact filter implemented |
| Tab Receita (projecao) | ticket_medio e Ritmo por cliente | calcular_projecao(df_proj, periodo) | WIRED | Lines 249-256: function defined and called for 30/60/90 |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| CFG-01 | 02-01 | Usuario pode configurar limiares de faixa de GAP via painel | SATISFIED | Tab Configuracao com 4 sliders, lines 268-311 |
| CFG-02 | 02-01 | Ao alterar limiares, dashboard recalcula e atualiza em tempo real | SATISFIED | st.rerun() triggered on threshold change, line 311 |
| VIZ-01 | 02-02 | Cards KPIs: total clientes RMR, % GAP negativo, receita em risco, ritmo medio | SATISFIED | 4 st.metric cards, lines 106-110 |
| VIZ-02 | 02-04 | Barras horizontais de distribuicao por segmento RMR (qtd de clientes E receita por segmento) | SATISFIED | px.bar orientation="h" with groupby().agg(Clientes, Receita), st.caption with revenue per segment. Lines 119-155 |
| VIZ-03 | n/a | Matriz R x Ritmo — heatmap 5x5 com quantidade de clientes por celula | DEFERRED | Intentionally excluded per user decision in CONTEXT.md deferred section. Not a phase gap. |
| VIZ-04 | 02-04 | Histograma de distribuicao de GAP pelas 5 faixas (quantidade de clientes + receita por faixa) | SATISFIED | barmode="group" with Clientes and Receita per faixa via .melt(), lines 169-205 |
| REV-01 | 02-03 | Bloco de receita semanal: soma ticket medio dos clientes com GAP entre -5 e +5 dias | SATISFIED | Lines 217-235: Receita Semanal block with exact GAP filter and sum |
| REV-02 | 02-03 | Bloco de projecao estrategica: 30, 60 e 90 dias — ticket medio x compras esperadas (periodo/ritmo) | SATISFIED | Lines 249-261: calcular_projecao() + proj_30/60/90 metrics |

**VIZ-03 note:** REQUIREMENTS.md marks VIZ-03 as `[x]` (checked) but the implementation intentionally omits it per CONTEXT.md. The checkbox in REQUIREMENTS.md is incorrect — it should be tracked as deferred. No code implements this feature and none should.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | No TODOs, FIXMEs, placeholder returns, or stub implementations found | — | — |

84 tests pass. Syntax valid. No regression from previous verification.

### Human Verification Required

#### 1. Real-time slider recalculation

**Test:** Load real data files, go to Tab Configuracao, move the "Critico" slider from -30 to -50.
**Expected:** All KPIs in Tab Painel, segment bar chart, GAP histogram, and all revenue numbers in Tab Receita update immediately on the next interaction without a full page reload.
**Why human:** Streamlit rerun behavior and session_state reactivity cannot be verified by static analysis.

#### 2. Monetary formatting consistency

**Test:** Load data with clients whose Monetario > 1000. Check Tab Painel "Receita em Risco" and Tab Receita "Receita Potencial (semana)" and projection metrics.
**Expected:** Values display as "R$ X.XXX" with dots as thousands separators (not commas). Example: "R$ 1.234" not "R$ 1,234".
**Why human:** The `.replace(",", ".")` formatting is present in code (lines 109, 224, 259-261) but rendering depends on browser locale.

#### 3. Segment bar chart ordering

**Test:** Load real data and open Tab Painel. Observe the horizontal bar chart "Distribuicao por Segmento RMR".
**Expected:** Campeoes appears at the top, Precisam Atencao at the bottom. Each bar label shows the client count. Hovering shows the receita total for that segment.
**Why human:** Plotly `categoryorder="array"` axis ordering and hover_data rendering cannot be confirmed by static analysis.

### Gaps Summary

No gaps remain. All 8 requirements for Phase 2 are satisfied (VIZ-03 is intentionally deferred per user decision, not a gap). The two gaps from the initial verification (VIZ-02 and VIZ-04) were closed by plan 02-04 in commits `bc662d7` and `511d262`.

Phase goal is achieved: the dashboard shows KPIs, charts, and revenue projections that all recalculate when GAP thresholds are adjusted.

---

_Verified: 2026-03-09T20:30:00Z_
_Verifier: Claude (gsd-verifier)_
_Previous verification: 2026-03-09T17:00:00Z (gaps_found, 9/11)_
