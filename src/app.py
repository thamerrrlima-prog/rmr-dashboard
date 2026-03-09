"""
app.py — Entrypoint Streamlit do Dashboard RMR LigueLead (Fase 1).

Pipeline: upload → data_loader → rmr_engine → segmentation → tabela de resultado.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.data_loader import load_base_bu, load_historico, get_valid_transactions
from src.rmr_engine import compute_rmr
from src.segmentation import apply_segmentation

# ─── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="RMR Dashboard — LigueLead",
    layout="wide",
)

st.title("RMR Dashboard — LigueLead")

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

            # 3. Calcular RMR + scores
            rmr_df = compute_rmr(valid_df)

            # 4. Aplicar segmentação
            result_df = apply_segmentation(rmr_df)

        # Armazenar no session_state para evitar recálculo ao interagir
        st.session_state["rmr_result"] = result_df

    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        st.session_state.pop("rmr_result", None)

# ─── Exibição dos resultados ──────────────────────────────────────────────────

if "rmr_result" in st.session_state:
    result_df = st.session_state["rmr_result"]

    total_clientes = len(result_df)
    inelegiveis = (result_df["Segmento_RMR"] == "Inelegível").sum()

    st.success(
        f"{total_clientes} clientes no RMR ({inelegiveis} inelegíveis por 1 compra)"
    )

    # Selecionar e ordenar colunas para exibição
    display_cols = [
        "Nome", "PlayG", "Telefone",
        "Recencia", "Monetario", "Ritmo", "GAP",
        "score_R", "score_M", "score_Ritmo",
        "Segmento_RMR", "Faixa_GAP",
    ]

    # Garantir que apenas colunas existentes sejam exibidas
    existing_cols = [c for c in display_cols if c in result_df.columns]

    # Incluir ID (índice) na visualização
    display_df = result_df[existing_cols].reset_index()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )
