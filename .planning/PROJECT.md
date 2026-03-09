# RMR Dashboard — LigueLead

## What This Is

Dashboard operacional em Streamlit para o time comercial da LigueLead priorizar contatos com clientes com base no modelo RMR (Recência / Monetário / Ritmo) — uma adaptação proprietária do RFM clássico. A ferramenta lê dois arquivos `.xlsx` exportados dos sistemas internos, calcula o RMR completo e apresenta os clientes ordenados por urgência de contato (GAP).

## Core Value

O vendedor abre o dashboard e sabe exatamente quem ligar hoje — ordenado por quem está mais atrasado para comprar, com telefone e ticket médio na mesma tela.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ingestão de dois arquivos .xlsx: Base B.U. (ID, Nome, PlayG, Telefone) e Histórico de Crédito (transações)
- [ ] Cálculo completo do modelo RMR: Recência, Monetário, Ritmo, GAP, Scores por quintis por PlayG, 8 segmentos RMR
- [ ] Painel de configuração dos limiares de cada faixa de GAP (Crítico, Atrasado, Hora de Comprar, Em Breve, Folgado)
- [ ] KPI cards: total clientes no RMR, % com GAP negativo, receita em risco (monetário dos clientes com GAP < 0)
- [ ] Visualização: distribuição por segmento RMR (barras — clientes e receita)
- [ ] Visualização: Matriz R × Ritmo (heatmap 5×5)
- [ ] Visualização: distribuição de GAP por faixas (histograma)
- [ ] Bloco de Receita Projetada: semanal (GAP entre -5 e +5 dias) e estratégica (30/60/90 dias via ticket médio × compras esperadas por ritmo)
- [ ] Tabela de prioridade de contato ordenada por GAP ascendente
- [ ] Colunas da tabela: ID, Nome, Telefone, GAP, Classificação GAP, Ticket Médio
- [ ] Filtros: PlayG, Classificação GAP, busca por texto (nome/ID)
- [ ] Design dark theme, referência visual no HTML RFM existente
- [ ] Deploy no Streamlit Cloud (link compartilhado para 5 vendedores)

### Out of Scope

- Registro de contatos ou CRM — não precisa
- Integração com WhatsApp, e-mail ou telefonia — não precisa
- Autenticação/login por vendedor — todos veem a base completa
- Cálculo de RFM clássico (Frequency) — substituído pelo Ritmo

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

## Constraints

- **Tech Stack**: Python + Streamlit + pandas — sem backend customizado
- **Dados**: entrada exclusivamente via upload de .xlsx no próprio dashboard
- **Deploy**: Streamlit Cloud (gratuito), repositório GitHub
- **Usuários**: 5 vendedores, acesso simultâneo via navegador
- **Manutenção**: arquivos atualizados pelo gestor, sem necessidade de intervenção técnica

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|------------|
| Streamlit em vez de HTML puro | Cálculo de quintis por PlayG é complexo para JS; pandas simplifica e garante fidelidade ao modelo | — Pending |
| Quintis calculados por PlayG | Comportamento de compra difere muito entre PGs; quintis globais perderiam valor analítico | — Pending |
| GAP como ordenação principal da tabela | Responde diretamente "quem ligar hoje" sem análise adicional | — Pending |
| Limiares de GAP configuráveis via UI | Permite ajuste fino sem alterar código | — Pending |

---
*Last updated: 2026-03-09 after initialization*
