# Roadmap: RMR Dashboard — LigueLead

## Overview

Tres fases que entregam um dashboard Streamlit completo: a Fase 1 constrói o motor de dados (ingestao + calculo RMR completo), a Fase 2 adiciona toda a camada analitica visivel ao vendedor (KPIs, graficos, configuracao, projecoes), e a Fase 3 entrega a lista de prioridade de contato com filtros, tema visual e deploy em producao.

## Phases

- [x] **Phase 1: Motor RMR** - Ingestao de arquivos e calculo completo do modelo RMR (base para tudo)
- [ ] **Phase 2: Painel Analitico** - KPIs, visualizacoes, configuracao de limiares e receita projetada
- [ ] **Phase 3: Lista de Prioridade e Deploy** - Tabela de contatos com filtros, tema dark e deploy no Streamlit Cloud

## Phase Details

### Phase 1: Motor RMR
**Goal**: O sistema consegue ingerir os dois arquivos .xlsx e calcular o modelo RMR completo para todos os clientes elegíveis
**Depends on**: Nothing (first phase)
**Requirements**: DAD-01, DAD-02, DAD-03, DAD-04, DAD-05, RMR-01, RMR-02, RMR-03, RMR-04, RMR-05, RMR-06, RMR-07, RMR-08, RMR-09
**Success Criteria** (what must be TRUE):
  1. Usuario faz upload dos dois .xlsx e o sistema aceita sem erros, filtrando automaticamente transacoes invalidas e restricoes de periodo
  2. Cada cliente elegivel tem Recencia, Monetario, Ritmo, GAP e scores (1-5) calculados corretamente por PlayG
  3. Clientes com apenas 1 compra aparecem excluidos do RMR (Ritmo = NULL)
  4. Cada cliente esta classificado em um dos 8 segmentos RMR e em uma das 5 faixas de GAP
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Ingestão e filtragem dos dois arquivos .xlsx (data_loader.py)
- [x] 01-02-PLAN.md — Motor RMR: cálculo de R, M, Ritmo, GAP e scores por quintis por PlayG
- [x] 01-03-PLAN.md — Segmentação em 8 segmentos RMR + 5 faixas de GAP + entrypoint Streamlit

### Phase 2: Painel Analitico
**Goal**: O vendedor ve KPIs, graficos e projecoes de receita — tudo recalculando em tempo real ao ajustar os limiares de GAP
**Depends on**: Phase 1
**Requirements**: CFG-01, CFG-02, VIZ-01, VIZ-02, VIZ-03, VIZ-04, REV-01, REV-02
**Success Criteria** (what must be TRUE):
  1. Cards de KPI exibem total de clientes no RMR, percentual com GAP negativo, receita em risco e ritmo medio da base
  2. Dashboard mostra distribuicao por segmento RMR (barras), matriz R x Ritmo (heatmap 5x5) e histograma de GAP por faixas
  3. Usuario altera um limiar de GAP no painel e todos os graficos e KPIs atualizam imediatamente sem recarregar a pagina
  4. Bloco de receita projetada exibe valor semanal (GAP -5 a +5) e projecoes para 30, 60 e 90 dias
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — Refatoração de session_state + Tab Configuração com 4 sliders de limiares de GAP
- [ ] 02-02-PLAN.md — Tab Painel: KPI cards, lista de segmentos RMR e histograma de GAP por faixas
- [ ] 02-03-PLAN.md — Tab Receita: receita semanal (GAP ±5) e projeção estratégica 30/60/90 dias

### Phase 3: Lista de Prioridade e Deploy
**Goal**: O vendedor acessa o dashboard via link, ve a lista de quem ligar hoje e consegue filtrar e buscar clientes especificos
**Depends on**: Phase 2
**Requirements**: LST-01, LST-02, LST-03, LST-04, LST-05, UI-01, UI-02, DEP-01
**Success Criteria** (what must be TRUE):
  1. Tabela exibe clientes ordenados do GAP mais negativo para o mais positivo, com colunas ID, Nome, Telefone, GAP, Classificacao GAP e Ticket Medio
  2. Usuario filtra por PlayG ou Classificacao GAP e a tabela atualiza mostrando apenas os clientes correspondentes
  3. Busca por nome ou ID retorna o cliente correto independente de maiusculas ou minusculas
  4. Interface usa dark theme consistente com a referencia visual e funciona sem scroll horizontal em notebooks
  5. Os 5 vendedores acessam o dashboard pelo mesmo link no Streamlit Cloud sem necessidade de login
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Motor RMR | 3/3 | Complete | 2026-03-09 |
| 2. Painel Analitico | 0/3 | Not started | - |
| 3. Lista de Prioridade e Deploy | 0/TBD | Not started | - |
