# Requirements: RMR Dashboard — LigueLead

**Defined:** 2026-03-09
**Core Value:** O vendedor abre o dashboard e sabe exatamente quem ligar hoje — ordenado por quem está mais atrasado para comprar, com telefone e ticket médio na mesma tela.

## v1 Requirements

### Dados

- [x] **DAD-01**: Usuário pode fazer upload do arquivo Base B.U. (.xlsx) com colunas ID, Nome, PlayG, Telefone
- [x] **DAD-02**: Usuário pode fazer upload do arquivo Histórico de Crédito (.xlsx) com todas as transações
- [x] **DAD-03**: Sistema filtra transações válidas (tipo "Nova Compra" ou "Pagamento", valor > R$ 0,00)
- [x] **DAD-04**: Sistema exclui transações inválidas ("Troca de Crédito", "Bônus/Desconto", valor = R$ 0,00)
- [x] **DAD-05**: Sistema considera apenas transações a partir de 01/01/2024

### Cálculo RMR

- [x] **RMR-01**: Sistema calcula Recência de cada cliente (dias desde última compra até hoje)
- [x] **RMR-02**: Sistema calcula Monetário de cada cliente (soma total de transações válidas no período)
- [x] **RMR-03**: Sistema calcula Ritmo de cada cliente (intervalo médio entre compras consecutivas em dias)
- [x] **RMR-04**: Clientes com apenas 1 compra no período têm Ritmo = NULL e são excluídos do RMR
- [x] **RMR-05**: Sistema calcula GAP de cada cliente (GAP = Ritmo − Recência)
- [x] **RMR-06**: Sistema atribui Score de 1 a 5 por quintis para cada dimensão (R, M, Ritmo), calculados independentemente por PlayG
- [x] **RMR-07**: Sistema inverte score de Recência e Ritmo (menor valor = score maior)
- [x] **RMR-08**: Sistema classifica cada cliente em um dos 8 segmentos RMR com base nos scores
- [x] **RMR-09**: Sistema classifica o status do GAP em faixas (Crítico, Atrasado, Hora de Comprar, Em Breve, Folgado)

### Configuração

- [x] **CFG-01**: Usuário pode configurar os limiares de cada faixa de GAP via painel na interface
- [x] **CFG-02**: Ao alterar os limiares, dashboard recalcula as classificações e atualiza todas as visualizações em tempo real

### KPIs e Visualizações

- [x] **VIZ-01**: Cards com KPIs: total de clientes no RMR, % com GAP negativo, receita em risco (monetário dos clientes com GAP < 0), ritmo médio da base
- [x] **VIZ-02**: Barras horizontais de distribuição por segmento RMR (quantidade de clientes e receita por segmento)
- [ ] **VIZ-03**: Matriz R × Ritmo — heatmap 5×5 com quantidade de clientes por célula
- [x] **VIZ-04**: Histograma de distribuição de GAP agrupado pelas 5 faixas de status (quantidade de clientes + receita por faixa)

### Receita Projetada

- [ ] **REV-01**: Bloco de receita semanal: soma do ticket médio dos clientes com GAP entre -5 e +5 dias
- [ ] **REV-02**: Bloco de projeção estratégica: receita projetada para 30, 60 e 90 dias — calculada por cliente como ticket médio × número de compras esperadas no período (período / ritmo)

### Lista de Prioridade

- [ ] **LST-01**: Tabela de clientes ordenada por GAP ascendente (mais negativos primeiro = mais urgentes)
- [ ] **LST-02**: Colunas: ID, Nome, Telefone, GAP (em dias), Classificação GAP, Ticket Médio
- [ ] **LST-03**: Filtro por PlayG (Todos / PG2 / PG3 / PG8)
- [ ] **LST-04**: Filtro por Classificação GAP (Crítico / Atrasado / Hora de Comprar / Em Breve / Folgado)
- [ ] **LST-05**: Busca por texto livre (nome ou ID do cliente)

### Interface e Deploy

- [ ] **UI-01**: Design dark theme, inspirado no HTML de referência existente
- [ ] **UI-02**: Layout responsivo para uso em notebook dos vendedores
- [ ] **DEP-01**: Aplicação hospedada no Streamlit Cloud, acessível via link único para os 5 vendedores

## v2 Requirements

### Melhorias futuras (não no escopo v1)

- **V2-01**: Exportar lista de prioridade filtrada para .xlsx ou .csv
- **V2-02**: Histórico de uploads para comparar evolução da base entre semanas
- **V2-03**: Alertas por e-mail para clientes que entram na faixa Crítica

## Out of Scope

| Feature | Reason |
|---------|--------|
| Registro de contatos / CRM | Fora do escopo — vendedor gerencia externamente |
| Integração com WhatsApp, e-mail ou telefonia | Complexidade desnecessária para v1 |
| Login por vendedor / carteiras separadas | Todos veem a base completa |
| Cálculo de RFM clássico (Frequency) | Substituído pelo Ritmo no modelo RMR |
| Gráficos interativos avançados (drill-down) | Plotly básico é suficiente para v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DAD-01 a DAD-05 | Phase 1 | Complete |
| RMR-01 a RMR-07 | Phase 1 | Complete (01-02) |
| RMR-08, RMR-09 | Phase 1 | Complete (01-03) |
| CFG-01, CFG-02 | Phase 2 | Pending |
| VIZ-01 a VIZ-04 | Phase 2 | Pending |
| REV-01, REV-02 | Phase 2 | Pending |
| LST-01 a LST-05 | Phase 3 | Pending |
| UI-01, UI-02 | Phase 3 | Pending |
| DEP-01 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after initial definition*
