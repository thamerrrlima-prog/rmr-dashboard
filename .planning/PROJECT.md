# RMR Dashboard — LigueLead

## What This Is

Dashboard operacional em Streamlit para o time comercial da LigueLead priorizar contatos com clientes com base no modelo RMR (Recência / Monetário / Ritmo) — uma adaptação proprietária do RFM clássico. A ferramenta lê dois arquivos `.xlsx` exportados dos sistemas internos, calcula o RMR completo e apresenta os clientes ordenados por urgência de contato (GAP). Deployed no Streamlit Cloud e acessível via link único para os 5 vendedores.

## Core Value

O vendedor abre o dashboard e sabe exatamente quem ligar hoje — ordenado por quem está mais atrasado para comprar, com telefone e ticket médio na mesma tela.

## Requirements

### Validated

- ✓ Ingestão de dois arquivos .xlsx: Base B.U. (ID, Nome, PlayG, Telefone) e Histórico de Crédito (transações) — v1.0
- ✓ Cálculo completo do modelo RMR: Recência, Monetário, Ritmo, GAP, Scores por quintis por PlayG, 8 segmentos RMR — v1.0
- ✓ Painel de configuração dos limiares de cada faixa de GAP (Crítico, Atrasado, Hora de Comprar, Em Breve, Folgado) — v1.0
- ✓ KPI cards: total clientes no RMR, % com GAP negativo, receita em risco (monetário dos clientes com GAP < 0) — v1.0
- ✓ Visualização: distribuição por segmento RMR (barras horizontais — clientes e receita) — v1.0
- ✓ Visualização: distribuição de GAP por faixas (histograma dual Clientes/Receita) — v1.0
- ✓ Bloco de Receita Projetada: semanal (GAP entre -5 e +5 dias) e estratégica (30/60/90 dias via ticket médio × compras esperadas por ritmo) — v1.0
- ✓ Tabela de prioridade de contato ordenada por GAP ascendente — v1.0
- ✓ Colunas da tabela: ID, Nome, Telefone, GAP, Classificação GAP, Ticket Médio — v1.0
- ✓ Filtros: PlayG, Classificação GAP, busca por texto (nome/ID) — v1.0
- ✓ Design dark theme, referência visual no HTML RFM existente — v1.0
- ✓ Deploy no Streamlit Cloud (link compartilhado para 5 vendedores) — v1.0

### Active

(None — all v1 requirements shipped. Define v2 requirements via `/gsd:new-milestone`.)

### Out of Scope

- Registro de contatos ou CRM — não precisa
- Integração com WhatsApp, e-mail ou telefonia — não precisa
- Autenticação/login por vendedor — todos veem a base completa
- Cálculo de RFM clássico (Frequency) — substituído pelo Ritmo
- Matriz R × Ritmo (heatmap 5×5) — removida por decisão explícita do usuário durante v1.0

## Context

- Empresa: LigueLead — comunicação massiva (Ligação, SMS, SMS Flash), modelo de créditos pré-pagos
- PlayGs: PG1 (excluída do RMR — só 1 compra), PG2, PG3, PG8 (quintis calculados separadamente por PlayG)
- Clientes com apenas 1 compra no período: Ritmo = NULL → excluídos do RMR
- Período de análise: 01/01/2024 até data atual
- Transações válidas: tipo "Nova Compra" ou "Pagamento", valor > R$ 0,00
- Transações inválidas: "Troca de Crédito", "Bônus/Desconto", valor = R$ 0,00
- Faixas padrão de GAP (configuráveis): Crítico < -30 | Atrasado -30 a -8 | Hora de Comprar -7 a 0 | Em Breve 1 a 7 | Folgado > 7
- Arquivos exportados com frequência semanal
- 5 vendedores acessando via link (Streamlit Cloud)
- **v1.0 shipped:** 962 LOC Python source + 817 LOC tests | 84 tests passing | 13 feature commits

## Constraints

- **Tech Stack**: Python + Streamlit + pandas — sem backend customizado
- **Dados**: entrada exclusivamente via upload de .xlsx no próprio dashboard
- **Deploy**: Streamlit Cloud (gratuito), repositório GitHub
- **Usuários**: 5 vendedores, acesso simultâneo via navegador
- **Manutenção**: arquivos atualizados pelo gestor, sem necessidade de intervenção técnica

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Streamlit em vez de HTML puro | Cálculo de quintis por PlayG é complexo para JS; pandas simplifica e garante fidelidade ao modelo | ✓ Good — pipeline limpo e testável |
| Quintis calculados por PlayG | Comportamento de compra difere muito entre PGs; quintis globais perderiam valor analítico | ✓ Good — scores corretos por grupo |
| GAP como ordenação principal da tabela | Responde diretamente "quem ligar hoje" sem análise adicional | ✓ Good — core value entregue |
| Limiares de GAP configuráveis via UI | Permite ajuste fino sem alterar código | ✓ Good — sliders funcionais em Tab Configuração |
| Ritmo usa drop_duplicates antes do diff | Evita inflação de frequência por múltiplas transações no mesmo dia | ✓ Good — métrica fiel ao comportamento real |
| assign_scores() como função separada | Permite Plan 03 chamar independentemente sem recomputar agregações base | ✓ Good — separação de responsabilidades |
| NaN propagation para clientes Ritmo=NaN | Exclusão é responsabilidade do módulo de segmentação, não do engine | ✓ Good — módulos com responsabilidades claras |
| rmr_df separado de rmr_result no session_state | Evita re-execução do pipeline pesado ao ajustar limiares | ✓ Good — UI reativa sem recálculo custoso |
| st.rerun() só quando thresholds mudam | Evita loop infinito de reruns | ✓ Good — padrão necessário para sliders |
| VIZ-03 (heatmap R × Ritmo) removido | Decisão explícita do usuário durante execução | — Accepted tech debt |
| Projeção Estratégica movida para Tab Painel | Visão estratégica pertence junto com KPIs, não Tab Receita | ✓ Good — layout mais coeso |
| pytest removido do requirements.txt | Dev dependency não necessária no Streamlit Cloud | ✓ Good — deploy mais limpo |

---
*Last updated: 2026-03-09 after v1.0 milestone*
