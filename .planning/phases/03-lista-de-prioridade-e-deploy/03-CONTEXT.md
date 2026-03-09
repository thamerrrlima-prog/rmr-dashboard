# Phase 3: Lista de Prioridade e Deploy - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Adicionar a tabela de prioridade de contato com filtros e busca, aplicar dark theme consistente em toda a app e fazer deploy no Streamlit Cloud via GitHub. KPIs, gráficos e configuração de limiares pertencem à Fase 2.

</domain>

<decisions>
## Implementation Decisions

### Placement da tabela de prioridade
- Nova **4ª tab "Lista"** adicionada à estrutura existente
- Ordem das tabs: **Lista | Painel | Receita | Configuração** — Lista fica em primeiro para o vendedor cair direto no essencial
- Tabela com **sort interativo por coluna** (comportamento nativo do `st.dataframe()` — sem implementação extra)
- **Sem botão de exportar** — V2-01 no backlog, fora do escopo da Fase 3

### Colunas da tabela
- ID, Nome, Telefone, GAP (em dias), Classificação GAP, Ticket Médio — conforme LST-02
- Ordenação padrão: GAP ascendente (mais negativos = mais urgentes no topo)

### Filtros e busca
- Filtro por PlayG (Todos / PG2 / PG3 / PG8) — LST-03
- Filtro por Classificação GAP (Crítico / Atrasado / Hora de Comprar / Em Breve / Folgado) — LST-04
- Busca por texto livre (nome ou ID, case-insensitive) — LST-05
- Claude's Discretion: posicionamento dos filtros (acima da tabela recomendado), comportamento de filtros combinados (AND lógico)

### Dark theme
- Claude's Discretion: implementar via `.streamlit/config.toml` com `[theme] base = "dark"` — mais simples e cobre toda a app uniformemente
- Referência visual: HTML RFM existente mencionado nos requisitos (UI-01)

### Deploy
- Streamlit Cloud, repositório GitHub, link único para 5 vendedores — sem login (DEP-01)
- Claude's Discretion: preparar `requirements.txt`, verificar se `.streamlit/config.toml` está no repo, documentar passos de deploy

### Claude's Discretion
- Posicionamento e layout dos filtros dentro da tab Lista
- Estilo visual do dark theme (cores, contraste) — inspirado na referência HTML existente
- `requirements.txt` com versões exatas das dependências
- Processo de deploy no Streamlit Cloud (secrets, configurações)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `st.session_state["rmr_result"]`: DataFrame com colunas GAP, Faixa_GAP, Nome, Telefone, PlayG, Monetario, Segmento_RMR — prontas para a tabela
- Tab Receita já usa `st.dataframe(..., use_container_width=True, hide_index=True)` com `sort_values("GAP")` — padrão reutilizável para a tab Lista
- Filtros por PlayG e Faixa_GAP já implementados na Tab Receita (`st.multiselect`) — padrão estabelecido

### Established Patterns
- `st.tabs(["Painel", "Receita", "Configuração"])` em `app.py:95` — adicionar "Lista" como primeiro elemento
- `elegíveis = result_df[result_df["Segmento_RMR"] != "Inelegível"]` — filtro padrão para excluir inelegíveis
- Formatação monetária: `f"R$ {valor:,.0f}".replace(",", ".")` — padrão consistente
- `st.multiselect()` para filtros com opções dinâmicas extraídas do DataFrame

### Integration Points
- `app.py:95` — mudar `st.tabs(["Painel", "Receita", "Configuração"])` para `st.tabs(["Lista", "Painel", "Receita", "Configuração"])`
- Adicionar `with tab_lista:` block antes do bloco `with tab_painel:`
- `.streamlit/config.toml` — criar arquivo se não existir (provavelmente não existe ainda)
- `requirements.txt` na raiz do projeto — necessário para deploy no Streamlit Cloud

</code_context>

<specifics>
## Specific Ideas

- Vendedor abre o dashboard e a primeira coisa que vê é a lista de quem ligar — sem navegar para outra tab
- Sort interativo é bonus: o vendedor pode reordenar por Ticket Médio para priorizar clientes de maior valor

</specifics>

<deferred>
## Deferred Ideas

- Exportar lista filtrada para .xlsx/.csv — V2-01 no backlog
- Heatmap R × Ritmo — descartado na Fase 2, não reabre aqui

</deferred>

---

*Phase: 03-lista-de-prioridade-e-deploy*
*Context gathered: 2026-03-09*
