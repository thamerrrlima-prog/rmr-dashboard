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

# ─── Upload ───────────────────────────────────────────────────────────────────

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

# ─── Cálculo ──────────────────────────────────────────────────────────────────

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

# ─── Exibição dos resultados ──────────────────────────────────────────────────

if "rmr_result" in st.session_state:
    result_df = st.session_state["rmr_result"]

    total_clientes = len(result_df)
    inelegiveis = (result_df["Segmento_RMR"] == "Inelegível").sum()

    st.success(
        f"{total_clientes} clientes no RMR ({inelegiveis} inelegíveis por 1 compra)"
    )

    tab_painel, tab_receita, tab_config = st.tabs(["Painel", "Receita", "Configuração"])

    with tab_painel:
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
        st.subheader("Distribuição por Segmento RMR")

        ORDEM_SEGMENTOS = [
            "Campeões", "Não Pode Perder", "Leais", "Novos Clientes",
            "Potenciais Leais", "Em Risco", "Hibernando", "Precisam Atenção"
        ]
        seg_counts = (
            elegíveis["Segmento_RMR"]
            .value_counts()
            .reindex(ORDEM_SEGMENTOS, fill_value=0)
            .reset_index()
        )
        seg_counts.columns = ["Segmento", "Clientes"]
        st.dataframe(seg_counts, use_container_width=True, hide_index=True)

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

        gap_counts = (
            elegíveis[elegíveis["Faixa_GAP"].isin(ORDEM_FAIXAS)]["Faixa_GAP"]
            .value_counts()
            .reindex(ORDEM_FAIXAS, fill_value=0)
            .reset_index()
        )
        gap_counts.columns = ["Faixa", "Clientes"]

        fig = px.bar(
            gap_counts,
            x="Faixa",
            y="Clientes",
            color="Faixa",
            color_discrete_map=CORES_FAIXAS,
            labels={"Faixa": "Faixa de GAP", "Clientes": "Quantidade de Clientes"},
            text="Clientes",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tab_receita:
        st.info("Receita projetada — em construção (Plano 03)")

    with tab_config:
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
