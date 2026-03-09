# Phase 2: Painel Analítico - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Adicionar ao dashboard existente (app.py da Fase 1): KPI cards, visualizações analíticas, configuração de limiares de GAP e blocos de receita projetada. Tudo organizado em tabs e recalculando em tempo real ao ajustar os limiares. Tabela de prioridade de contato e deploy pertencem à Fase 3.

</domain>

<decisions>
## Implementation Decisions

### Layout da página
- Estrutura em **3 tabs** após o cálculo: "Painel", "Receita" e "Configuração"
- Não usar sidebar — toda a interface fica nas tabs

### Tab "Painel"
- KPI cards no topo: total de clientes no RMR, % com GAP negativo, receita em risco (GAP < 0), ritmo médio da base
- Lista de segmentos RMR: contagem de clientes por segmento (substitui heatmap 5×5 — heatmap não necessário)
- Histograma de distribuição de GAP por faixas (barras com quantidade de clientes por faixa)

### Tab "Receita"
- Bloco 1 — Receita semanal: soma do ticket médio dos clientes com GAP entre -5 e +5 dias
- Bloco 2 — Projeção estratégica (separado do bloco semanal): receita projetada para 30, 60 e 90 dias por cliente (ticket médio × compras esperadas no período)

### Tab "Configuração"
- 4 sliders para os limiares de GAP: crítico_max, atrasado_max, hora_max, em_breve_max
- Ao alterar qualquer limiar, os KPIs e visualizações recalculam automaticamente (Streamlit re-run com os novos thresholds)

### Recálculo em tempo real
- Limiares de GAP ficam em `st.session_state` — mudança nos sliders dispara re-run do Streamlit
- Apenas `apply_segmentation()` é re-chamada com os novos limiares (não re-executa `compute_rmr()`)
- `rmr_result_base` (sem segmentação) armazenado em session_state; segmentação aplicada on-the-fly

### Claude's Discretion
- Cores dos KPI cards e gráficos
- Formato exato dos valores monetários (R$)
- Ordenação da lista de segmentos
- Design visual dos blocos de receita

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/segmentation.py`: `apply_segmentation(rmr_df, gap_thresholds=None)` — aceita thresholds customizados, pronto para Fase 2
- `src/segmentation.py`: `DEFAULT_GAP_THRESHOLDS` — dict com limiares padrão para inicializar os sliders
- `src/segmentation.py`: `classify_gap_status(gap_value, thresholds)` — reutilizável para recálculo por cliente
- `src/app.py`: `st.session_state["rmr_result"]` — já armazena resultado pós-segmentação

### Established Patterns
- `st.session_state` para evitar re-execução do pipeline pesado — padrão já estabelecido
- Streamlit layout com `st.columns()` para uploads lado a lado — reutilizável para KPI cards
- Pipeline: `load_base_bu → load_historico → get_valid_transactions → compute_rmr → apply_segmentation`

### Integration Points
- `app.py` precisará armazenar `rmr_df` (pré-segmentação) separado de `result_df` (pós-segmentação) para permitir recálculo eficiente ao mudar limiares
- Tabs criadas com `st.tabs(["Painel", "Receita", "Configuração"])` após o bloco de upload/cálculo existente
- `DEFAULT_GAP_THRESHOLDS` importado de `segmentation.py` para inicializar valores dos sliders na Tab Configuração

</code_context>

<specifics>
## Specific Ideas

- Receita semanal e projeção estratégica em blocos visualmente separados dentro da Tab "Receita"
- Lista de segmentos com contagem simples (não heatmap) — mais legível para o vendedor

</specifics>

<deferred>
## Deferred Ideas

- Heatmap R × Ritmo — descartado pelo usuário (não necessário para v1)

</deferred>

---

*Phase: 02-painel-analitico*
*Context gathered: 2026-03-09*
