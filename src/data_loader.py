"""
data_loader.py — Camada de ingestão de dados do Dashboard RMR LigueLead.

Funções públicas:
    load_base_bu(file) -> pd.DataFrame
    load_historico(file) -> pd.DataFrame
    get_valid_transactions(base_df, hist_df) -> pd.DataFrame
    validate_columns(df, canonical_map, filename_hint) -> pd.DataFrame
"""

import re
import pandas as pd

# ─── Constantes de colunas canônicas ──────────────────────────────────────────

# Nomes canônicos → lista de aliases aceitos (case-insensitive, strip)
COLUNAS_BASE_BU: dict[str, list[str]] = {
    "ID":       ["id", "id_cliente", "id cliente", "codigo", "código"],
    "Nome":     ["nome", "nome do cliente", "nome_cliente", "cliente"],
    "PlayG":    ["playg", "play g", "play_g", "plg", "grupo"],
    "Telefone": ["telefone", "fone", "celular", "tel", "whatsapp", "contato"],
}

COLUNAS_HISTORICO: dict[str, list[str]] = {
    "ID":    ["id", "id_cliente", "id cliente", "codigo", "código", "id do cliente"],
    "Tipo":  ["tipo", "tipo transacao", "tipo_transacao", "tipo de transação", "tipo transação"],
    "Valor": ["valor", "valor transacao", "valor_transacao", "valor (r$)", "montante"],
    "Data":  ["data", "data transacao", "data_transacao", "data de transação",
              "data transação", "data lançamento", "data lancamento", "dt"],
}

# Tipos de transação válidos (após .str.title())
TIPOS_VALIDOS = {"Nova Compra", "Pagamento"}

# Data mínima para transações válidas
DATA_MINIMA = pd.Timestamp("2024-01-01")


# ─── Funções auxiliares ────────────────────────────────────────────────────────

def _normalize_col_name(name: str) -> str:
    """Normaliza nome de coluna: lowercase + strip."""
    return str(name).strip().lower()


def validate_columns(
    df: pd.DataFrame,
    canonical_map: dict[str, list[str]],
    filename_hint: str,
) -> pd.DataFrame:
    """
    Valida e renomeia colunas do DataFrame para nomes canônicos.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame lido do arquivo .xlsx.
    canonical_map : dict
        Mapeamento {nome_canonico: [alias1, alias2, ...]}
        O próprio nome canônico também é testado como alias (normalizado).
    filename_hint : str
        Nome do arquivo (para mensagem de erro).

    Retorna
    -------
    pd.DataFrame com colunas renomeadas para os nomes canônicos.

    Levanta
    -------
    ValueError se alguma coluna obrigatória não for encontrada.
    """
    # Mapa de nome_normalizado -> nome_original no df
    df_col_map = {_normalize_col_name(c): c for c in df.columns}

    rename_dict: dict[str, str] = {}
    missing: list[str] = []

    for canonical, aliases in canonical_map.items():
        # Busca: canonical normalizado + todos os aliases normalizados
        candidates = [_normalize_col_name(canonical)] + [_normalize_col_name(a) for a in aliases]
        found = None
        for candidate in candidates:
            if candidate in df_col_map:
                found = df_col_map[candidate]
                break

        if found is None:
            missing.append(canonical)
        elif found != canonical:
            rename_dict[found] = canonical

    if missing:
        actual = list(df.columns)
        expected = list(canonical_map.keys())
        raise ValueError(
            f"Arquivo '{filename_hint}': colunas obrigatórias não encontradas — "
            f"esperado {expected}, encontrado {actual}. "
            f"Colunas ausentes: {missing}"
        )

    if rename_dict:
        df = df.rename(columns=rename_dict)

    return df


# ─── Funções públicas ──────────────────────────────────────────────────────────

def load_base_bu(file) -> pd.DataFrame:
    """
    Carrega o arquivo Base B.U. (.xlsx).

    Parâmetros
    ----------
    file : str | pathlib.Path | BytesIO
        Caminho ou file-like object (Streamlit uploader).

    Retorna
    -------
    pd.DataFrame com colunas [ID, Nome, PlayG, Telefone], sem clientes de PG1.

    Levanta
    -------
    ValueError se colunas obrigatórias ausentes.
    """
    df = pd.read_excel(file)
    df = validate_columns(df, COLUNAS_BASE_BU, filename_hint="base_bu.xlsx")

    # Selecionar apenas colunas canônicas (descartar extras)
    df = df[list(COLUNAS_BASE_BU.keys())].copy()

    # Excluir PG1 (aceita string "PG1" ou inteiro 1)
    pg_col = df["PlayG"].astype(str).str.strip()
    df = df[~pg_col.isin(["PG1", "1"])].reset_index(drop=True)

    return df


def load_historico(file) -> pd.DataFrame:
    """
    Carrega o arquivo Histórico de Crédito (.xlsx).

    Parâmetros
    ----------
    file : str | pathlib.Path | BytesIO
        Caminho ou file-like object (Streamlit uploader).

    Retorna
    -------
    pd.DataFrame com todas as colunas originais preservadas,
    com a coluna de data convertida para datetime.

    Levanta
    -------
    ValueError se colunas obrigatórias ausentes.
    """
    df = pd.read_excel(file)
    df = validate_columns(df, COLUNAS_HISTORICO, filename_hint="historico_credito.xlsx")

    # Converter coluna de data para datetime
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Converter coluna Valor para numérico (coerce strings não-numéricas para NaN)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    return df


def get_valid_transactions(base_df: pd.DataFrame, hist_df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna DataFrame com transações válidas para o motor RMR.

    Filtros aplicados:
    - Tipo IN ["Nova Compra", "Pagamento"] (via .str.title())
    - Valor > 0 (NaN descartado)
    - Data >= 2024-01-01
    - Somente clientes presentes em base_df (exclui PG1 implicitamente)

    Parâmetros
    ----------
    base_df : pd.DataFrame
        Resultado de load_base_bu() — clientes elegíveis (sem PG1).
    hist_df : pd.DataFrame
        Resultado de load_historico() — todas as transações.

    Retorna
    -------
    pd.DataFrame com colunas de base_df + colunas de hist_df (inner join por ID).
    """
    df = hist_df.copy()

    # Filtro 1: tipo válido (normaliza para Title Case)
    df = df[df["Tipo"].str.strip().str.title().isin(TIPOS_VALIDOS)]

    # Filtro 2: valor positivo (NaN já vira False na comparação)
    df = df[df["Valor"] > 0]

    # Filtro 3: data >= DATA_MINIMA
    df = df[df["Data"] >= DATA_MINIMA]

    # Filtro 4: inner join com base_df — exclui PG1 e clientes não cadastrados
    result = pd.merge(
        df,
        base_df[["ID", "Nome", "PlayG", "Telefone"]],
        on="ID",
        how="inner",
    )

    return result.reset_index(drop=True)
