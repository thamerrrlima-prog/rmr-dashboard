"""
app.py — Entrypoint Streamlit do Dashboard RMR LigueLead.

Pipeline: upload → data_loader → rmr_engine → segmentation → painel analítico.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.data_loader import load_base_bu, load_historico, get_valid_transactions
from src.rmr_engine import compute_rmr
from src.segmentation import apply_segmentation, DEFAULT_GAP_THRESHOLDS

# ─── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="RMR Dashboard — LigueLead",
    layout="wide",
)

st.title("RMR Dashboard — LigueLead")

# ─── Inicialização do session_state ───────────────────────────────────────────

if "gap_thresholds" not in st.session_state:
    st.session_state["gap_thresholds"] = DEFAULT_GAP_THRESHOLDS.copy()

# ─── 5 Tabs — sempre visíveis ─────────────────────────────────────────────────

tab_receita, tab_painel, tab_lista, tab_importacao, tab_config = st.tabs(
    ["Receita", "Painel", "Lista", "Importação", "Configuração"]
)

# ─── Tab Lista ────────────────────────────────────────────────────────────────

with tab_lista:
    if "rmr_result" not in st.session_state:
        st.info("Importe os dados na aba **Importação** para ver a lista de prioridade.")
    else:
        result_df = st.session_state["rmr_result"]
        elegíveis = result_df[result_df["Segmento_RMR"] != "Inelegível"].copy()

        # Garantir que ID é coluna (pode estar no índice)
        if "ID" not in elegíveis.columns:
            elegíveis = elegíveis.reset_index()
            if elegíveis.columns[0] != "ID":
                elegíveis = elegíveis.rename(columns={elegíveis.columns[0]: "ID"})

        elegíveis["Ticket Médio"] = elegíveis["Monetario"]

        # Filtros
        f1, f2, f3 = st.columns(3)
        sel_playg = f1.multiselect("PlayG", sorted(elegíveis["PlayG"].dropna().unique()), key="lista_playg")
        sel_faixa = f2.multiselect(
            "Classificação GAP",
            ["Crítico", "Atrasado", "Hora de Comprar", "Em Breve", "Folgado"],
            key="lista_faixa",
        )
        busca = f3.text_input("Buscar nome ou ID", key="lista_busca", placeholder="Digite nome ou ID...")

        # Aplicar filtros (lógica AND)
        df_lista = elegíveis.copy()
        if sel_playg:
            df_lista = df_lista[df_lista["PlayG"].isin(sel_playg)]
        if sel_faixa:
            df_lista = df_lista[df_lista["Faixa_GAP"].isin(sel_faixa)]
        if busca.strip():
            termo = busca.strip().lower()
            mask_nome = df_lista["Nome"].str.lower().str.contains(termo, na=False)
            mask_id = df_lista["ID"].astype(str).str.lower().str.contains(termo, na=False)
            df_lista = df_lista[mask_nome | mask_id]

        # Selecionar e ordenar colunas
        COLUNAS_LISTA = ["ID", "Nome", "Telefone", "GAP", "Faixa_GAP", "Ticket Médio"]
        colunas_existentes = [c for c in COLUNAS_LISTA if c in df_lista.columns]
        df_exibir = (
            df_lista[colunas_existentes]
            .rename(columns={"Faixa_GAP": "Classificação GAP"})
            .sort_values("GAP")
            .reset_index(drop=True)
        )

        st.caption(
            f"{len(df_exibir)} clientes encontrados — ordenados por urgência (GAP ascendente). "
            "Clique no cabeçalho da coluna para reordenar."
        )
        if len(df_exibir) > 0:
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cliente encontrado com os filtros atuais.")

# ─── Tab Receita ──────────────────────────────────────────────────────────────

with tab_receita:
    if "rmr_result" not in st.session_state:
        st.info("Importe os dados na aba **Importação** para ver a receita.")
    else:
        result_df = st.session_state["rmr_result"]
        elegíveis = result_df[result_df["Segmento_RMR"] != "Inelegível"].copy()

        # Ticket médio = Monetario total do cliente no período (estimativa conservadora)
        elegíveis["ticket_medio"] = elegíveis["Monetario"]

        st.subheader("Receita Semanal")

        # Filtros — Faixa GAP vem de todos os elegíveis para permitir expandir além da janela semanal
        f1, f2 = st.columns(2)
        playg_opts = sorted(elegíveis["PlayG"].dropna().unique())
        faixa_opts = sorted(elegíveis["Faixa_GAP"].dropna().unique())
        sel_playg = f1.multiselect("Filtrar por PlayG", playg_opts)
        sel_faixa = f2.multiselect(
            "Filtrar por Faixa GAP",
            faixa_opts,
            help="Sem seleção = janela imediata (-5 a +5 dias). Selecione faixas para expandir a lista.",
        )

        # Base: sem filtro de faixa usa janela semanal; com faixa usa todos os elegíveis daquelas faixas
        if sel_faixa:
            df_filtrado = elegíveis[elegíveis["Faixa_GAP"].isin(sel_faixa)].copy()
            st.caption(f"Exibindo faixas selecionadas: {', '.join(sel_faixa)}")
        else:
            semanal_mask = (elegíveis["GAP"] >= -5) & (elegíveis["GAP"] <= 5)
            df_filtrado = elegíveis[semanal_mask].copy()
            st.caption("Clientes com GAP entre -5 e +5 dias — janela imediata de compra.")

        if sel_playg:
            df_filtrado = df_filtrado[df_filtrado["PlayG"].isin(sel_playg)]

        receita_semanal = df_filtrado["ticket_medio"].sum()
        n_clientes_semanal = len(df_filtrado)

        col1, col2 = st.columns(2)
        col1.metric("Receita Potencial (semana)", f"R$ {receita_semanal:,.0f}".replace(",", "."))
        col2.metric("Clientes na Janela", f"{n_clientes_semanal}")

        if n_clientes_semanal > 0:
            colunas = ["Nome", "Telefone", "PlayG", "GAP", "Faixa_GAP", "ticket_medio"]
            colunas_existentes = [c for c in colunas if c in df_filtrado.columns]
            st.dataframe(
                df_filtrado[colunas_existentes]
                .sort_values("GAP")
                .rename(columns={"ticket_medio": "Ticket Médio (R$)"})
                .reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhum cliente na janela de -5 a +5 dias com os filtros atuais.")

# ─── Tab Painel ───────────────────────────────────────────────────────────────

with tab_painel:
    if "rmr_result" not in st.session_state:
        st.info("Importe os dados na aba **Importação** para ver o painel.")
    else:
        result_df = st.session_state["rmr_result"]
        elegíveis = result_df[result_df["Segmento_RMR"] != "Inelegível"]

        total_rmr = len(elegíveis)
        pct_gap_negativo = (elegíveis["GAP"] < 0).sum() / len(elegíveis) * 100 if len(elegíveis) > 0 else 0
        receita_risco = elegíveis[elegíveis["GAP"] < 0]["Monetario"].sum()
        ritmo_medio = elegíveis["Ritmo"].dropna().mean()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clientes no RMR", f"{total_rmr:,}")
        c2.metric("GAP Negativo", f"{pct_gap_negativo:.1f}%")
        c3.metric("Receita em Risco", f"R$ {receita_risco:,.0f}".replace(",", "."))
        c4.metric("Ritmo Médio", f"{ritmo_medio:.0f} dias" if not pd.isna(ritmo_medio) else "—")

        st.divider()
        st.subheader("Projeção Estratégica")
        st.caption(
            "Receita esperada por período — calculada por cliente como "
            "Ticket Médio × compras esperadas (período ÷ Ritmo)."
        )

        elegíveis_proj = result_df[result_df["Segmento_RMR"] != "Inelegível"].copy()
        elegíveis_proj["ticket_medio"] = elegíveis_proj["Monetario"]

        # Apenas clientes com Ritmo definido (elegíveis já exclui Inelegível, mas Ritmo pode ser NaN em edge cases)
        df_proj = elegíveis_proj[elegíveis_proj["Ritmo"].notna() & (elegíveis_proj["Ritmo"] > 0)].copy()

        def calcular_projecao(df: pd.DataFrame, periodo_dias: int) -> float:
            """Soma receita projetada: ticket_medio × floor(periodo_dias / ritmo) por cliente."""
            compras_esperadas = (periodo_dias / df["Ritmo"]).apply(lambda x: max(int(x), 0))
            return (df["ticket_medio"] * compras_esperadas).sum()

        proj_30 = calcular_projecao(df_proj, 30)
        proj_60 = calcular_projecao(df_proj, 60)
        proj_90 = calcular_projecao(df_proj, 90)

        c1, c2, c3 = st.columns(3)
        c1.metric("30 dias", f"R$ {proj_30:,.0f}".replace(",", "."))
        c2.metric("60 dias", f"R$ {proj_60:,.0f}".replace(",", "."))
        c3.metric("90 dias", f"R$ {proj_90:,.0f}".replace(",", "."))

        st.caption(
            f"Base de cálculo: {len(df_proj)} clientes com Ritmo definido "
            f"(excluídos clientes com 1 compra)."
        )

        st.divider()
        st.subheader("Distribuição por Segmento RMR")

        ORDEM_SEGMENTOS = [
            "Campeões", "Não Pode Perder", "Leais", "Novos Clientes",
            "Potenciais Leais", "Em Risco", "Hibernando", "Precisam Atenção"
        ]
        seg_data = (
            elegíveis[elegíveis["Segmento_RMR"].isin(ORDEM_SEGMENTOS)]
            .groupby("Segmento_RMR", observed=True)
            .agg(Clientes=("Segmento_RMR", "count"), Receita=("Monetario", "sum"))
            .reindex(ORDEM_SEGMENTOS, fill_value=0)
            .reset_index()
        )
        seg_data.columns = ["Segmento", "Clientes", "Receita"]
        # Inverter ordem para que o gráfico horizontal mostre Campeões no topo
        seg_data = seg_data.iloc[::-1].reset_index(drop=True)

        fig_seg = px.bar(
            seg_data,
            x="Clientes",
            y="Segmento",
            orientation="h",
            text="Clientes",
            hover_data={"Receita": ":,.0f"},
            labels={"Clientes": "Quantidade de Clientes", "Segmento": "Segmento RMR"},
            color_discrete_sequence=["#1f77b4"],
        )
        fig_seg.update_traces(textposition="outside")
        fig_seg.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis={"categoryorder": "array", "categoryarray": seg_data["Segmento"].tolist()},
            margin={"l": 160},
        )
        st.plotly_chart(fig_seg, use_container_width=True)
        st.caption(
            f"Receita total por segmento (ticket médio): "
            + " | ".join(
                f"{row['Segmento']}: R$ {row['Receita']:,.0f}".replace(",", ".")
                for _, row in seg_data.iloc[::-1].iterrows()
                if row["Clientes"] > 0
            )
        )

        st.divider()
        st.subheader("Distribuição de GAP por Faixa")

        ORDEM_FAIXAS = ["Crítico", "Atrasado", "Hora de Comprar", "Em Breve", "Folgado"]
        CORES_FAIXAS = {
            "Crítico": "#d62728",
            "Atrasado": "#ff7f0e",
            "Hora de Comprar": "#2ca02c",
            "Em Breve": "#1f77b4",
            "Folgado": "#9467bd",
        }

        gap_data = (
            elegíveis[elegíveis["Faixa_GAP"].isin(ORDEM_FAIXAS)]
            .groupby("Faixa_GAP", observed=True)
            .agg(Clientes=("Faixa_GAP", "count"), Receita=("Monetario", "sum"))
            .reindex(ORDEM_FAIXAS, fill_value=0)
            .reset_index()
        )
        gap_data.columns = ["Faixa", "Clientes", "Receita"]

        # Formato longo para px.bar com barmode='group'
        gap_long = gap_data.melt(
            id_vars="Faixa",
            value_vars=["Clientes", "Receita"],
            var_name="Métrica",
            value_name="Valor",
        )

        fig_gap = px.bar(
            gap_long,
            x="Faixa",
            y="Valor",
            color="Métrica",
            barmode="group",
            text="Valor",
            category_orders={"Faixa": ORDEM_FAIXAS, "Métrica": ["Clientes", "Receita"]},
            color_discrete_map={"Clientes": "#1f77b4", "Receita": "#2ca02c"},
            labels={"Faixa": "Faixa de GAP", "Valor": "Quantidade / Receita (R$)"},
        )
        fig_gap.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside",
        )
        fig_gap.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
        )
        st.plotly_chart(fig_gap, use_container_width=True)


# ─── Tab Importação ───────────────────────────────────────────────────────────

with tab_importacao:
    st.header("Carregar Dados")

    col1, col2 = st.columns(2)
    with col1:
        base_bu_file = st.file_uploader(
            "Base B.U.",
            type=["xlsx"],
            key="base_bu",
            help="Arquivo Excel com colunas: ID, Nome, PlayG, Telefone",
        )
    with col2:
        historico_file = st.file_uploader(
            "Histórico de Crédito",
            type=["xlsx"],
            key="historico",
            help="Arquivo Excel com colunas: ID, Tipo, Valor, Data",
        )

    if st.button("Calcular RMR", type="primary", disabled=(base_bu_file is None or historico_file is None)):
        try:
            with st.spinner("Processando dados..."):
                # 1. Carregar arquivos
                base_df = load_base_bu(base_bu_file)
                hist_df = load_historico(historico_file)

                # 2. Filtrar transações válidas (exclui PG1, tipos inválidos, etc.)
                valid_df = get_valid_transactions(base_df, hist_df)

                # 3. Calcular RMR + scores (pré-segmentação — imutável após cálculo)
                rmr_df = compute_rmr(valid_df)
                st.session_state["rmr_df"] = rmr_df

                # 4. Aplicar segmentação com limiares correntes
                st.session_state["rmr_result"] = apply_segmentation(
                    rmr_df, st.session_state.get("gap_thresholds", DEFAULT_GAP_THRESHOLDS)
                )

        except Exception as e:
            import traceback
            st.error(f"Erro ao processar os dados: {e}")
            st.code(traceback.format_exc())
            st.session_state.pop("rmr_result", None)
            st.session_state.pop("rmr_df", None)

    if "rmr_result" in st.session_state:
        result_df = st.session_state["rmr_result"]
        total_clientes = len(result_df)
        inelegiveis = (result_df["Segmento_RMR"] == "Inelegível").sum()
        st.success(f"{total_clientes} clientes no RMR ({inelegiveis} inelegíveis por 1 compra)")
        st.info("Dados carregados. Navegue pelas abas Lista, Receita e Painel.")

# ─── Tab Configuração ─────────────────────────────────────────────────────────

with tab_config:
    if "rmr_result" not in st.session_state:
        st.info("Importe os dados na aba **Importação** para configurar os limiares.")
    else:
        st.subheader("Limiares de GAP")
        st.caption("Alterar os limiares recalcula automaticamente todas as visualizações.")

        thresholds = st.session_state["gap_thresholds"]

        critico_max = st.slider(
            "Crítico: GAP abaixo de (dias)",
            min_value=-120, max_value=-5, step=1,
            value=thresholds["critico_max"],
            help="Clientes com GAP < este valor são classificados como Crítico"
        )
        atrasado_max = st.slider(
            "Atrasado: GAP abaixo de (dias)",
            min_value=-60, max_value=0, step=1,
            value=thresholds["atrasado_max"],
            help="GAP entre crítico_max e este valor = Atrasado"
        )
        hora_max = st.slider(
            "Hora de Comprar: GAP até (dias)",
            min_value=-30, max_value=15, step=1,
            value=thresholds["hora_max"],
            help="GAP entre atrasado_max e este valor = Hora de Comprar"
        )
        em_breve_max = st.slider(
            "Em Breve: GAP até (dias)",
            min_value=1, max_value=30, step=1,
            value=thresholds["em_breve_max"],
            help="GAP entre hora_max e este valor = Em Breve. Acima = Folgado"
        )

        new_thresholds = {
            "critico_max": critico_max,
            "atrasado_max": atrasado_max,
            "hora_max": hora_max,
            "em_breve_max": em_breve_max,
        }

        if new_thresholds != st.session_state["gap_thresholds"]:
            st.session_state["gap_thresholds"] = new_thresholds
            st.session_state["rmr_result"] = apply_segmentation(
                st.session_state["rmr_df"], new_thresholds
            )
            st.rerun()
