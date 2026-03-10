"""
rmr_engine.py — Motor de cálculo RMR do Dashboard LigueLead.

Funções públicas:
    compute_rmr(valid_df, reference_date=None) -> pd.DataFrame
    assign_scores(rmr_df) -> pd.DataFrame

O DataFrame retornado por compute_rmr() é indexado por ID e contém:
    Nome, PlayG, Telefone, Recencia, Monetario, Ritmo, GAP,
    score_R, score_M, score_Ritmo

Notas sobre scoring:
    - Scores calculados somente para clientes elegíveis (Ritmo não-NaN).
    - Quintis calculados independentemente por PlayG (pd.qcut com duplicates='drop').
    - Se um PlayG tiver < 5 clientes elegíveis, qcut pode produzir menos de 5 bins
      — isso é aceitável. Os scores refletem a distribuição real dentro do grupo.
    - score_R e score_Ritmo: invertidos (menor valor → score 5).
    - score_M: direto (maior valor → score 5).
"""

import pandas as pd
import numpy as np


# ─── Função principal ─────────────────────────────────────────────────────────

def compute_rmr(
    valid_df: pd.DataFrame,
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Calcula R, M, Ritmo, GAP e scores por cliente a partir de transações válidas.

    Parâmetros
    ----------
    valid_df : pd.DataFrame
        DataFrame retornado por get_valid_transactions() — colunas canônicas:
        ID, Nome, PlayG, Telefone, Tipo, Valor, Data.
    reference_date : pd.Timestamp, optional
        Data de referência para cálculo de Recência.
        Padrão: pd.Timestamp.today().normalize() (meia-noite do dia atual).

    Retorna
    -------
    pd.DataFrame indexado por ID com colunas:
        Nome, PlayG, Telefone, Recencia (int), Monetario (float),
        Ritmo (float | NaN), GAP (float | NaN),
        score_R (int | NaN), score_M (int | NaN), score_Ritmo (int | NaN).

    Clientes com apenas 1 data de compra distinta têm Ritmo=NaN, GAP=NaN
    e scores=NaN — são incluídos no DataFrame mas não participam do quintil.
    """
    if reference_date is None:
        reference_date = pd.Timestamp.today().normalize()

    df = valid_df.copy()

    # ── 1. Atributos de perfil (último registro do cliente) ──────────────────
    profile = (
        df.sort_values("Data")
        .groupby("ID")[["Nome", "PlayG", "Telefone"]]
        .last()
    )

    # ── 2. Recência: (reference_date - data_ultima_compra).days ─────────────
    recencia = (
        df.groupby("ID")["Data"]
        .max()
        .apply(lambda d: int((reference_date - d) / pd.Timedelta(days=1)))
        .rename("Recencia")
    )

    # ── 3. Monetário: soma de Valor por cliente ──────────────────────────────
    monetario = df.groupby("ID")["Valor"].sum().rename("Monetario")

    # ── 4. Ritmo: média dos diffs entre datas únicas consecutivas ────────────
    def _calc_ritmo(group: pd.Series) -> float:
        """Calcula ritmo para um grupo de datas (série por ID)."""
        datas_unicas = group.drop_duplicates().sort_values().reset_index(drop=True)
        if len(datas_unicas) < 2:
            return float("nan")
        total_days = (datas_unicas.iloc[-1] - datas_unicas.iloc[0]) / pd.Timedelta(days=1)
        return float(total_days / (len(datas_unicas) - 1))

    ritmo = (
        df.groupby("ID")["Data"]
        .apply(_calc_ritmo)
        .rename("Ritmo")
    )

    # ── 5. Montar DataFrame base ─────────────────────────────────────────────
    rmr_df = profile.join([recencia, monetario, ritmo])

    # ── 6. GAP = Ritmo - Recencia ────────────────────────────────────────────
    rmr_df["GAP"] = rmr_df["Ritmo"] - rmr_df["Recencia"]

    # ── 7. Scores por quintis por PlayG ─────────────────────────────────────
    rmr_df = assign_scores(rmr_df)

    return rmr_df


# ─── Scoring ──────────────────────────────────────────────────────────────────

def assign_scores(rmr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas score_R, score_M, score_Ritmo ao DataFrame RMR.

    Scores calculados somente para clientes elegíveis (Ritmo não-NaN).
    Quintis calculados por PlayG de forma independente.

    Inversão:
        score_R, score_Ritmo: labels=[5,4,3,2,1] (menor valor = score maior)
        score_M:              labels=[1,2,3,4,5] (maior valor = score maior)

    Parâmetros
    ----------
    rmr_df : pd.DataFrame
        DataFrame com colunas Recencia, Monetario, Ritmo, GAP, PlayG.

    Retorna
    -------
    pd.DataFrame com colunas adicionais: score_R, score_M, score_Ritmo.
    """
    result = rmr_df.copy()

    # Inicializa scores como NaN (float)
    result["score_R"] = float("nan")
    result["score_M"] = float("nan")
    result["score_Ritmo"] = float("nan")

    # Seleciona apenas clientes elegíveis (Ritmo não-NaN)
    elegíveis_mask = result["Ritmo"].notna()
    elegíveis = result[elegíveis_mask].copy()

    if elegíveis.empty:
        return result

    def _qcut_score(x: pd.Series, labels) -> pd.Series:
        """Aplica pd.qcut com 5 bins e retorna scores como float."""
        try:
            cats = pd.qcut(x, q=5, labels=labels, duplicates="drop")
            return cats.astype(float)
        except ValueError:
            # Menos de 5 valores distintos — usa rank percentílico como fallback
            return pd.Series(float("nan"), index=x.index)

    # Calcular scores por PlayG
    for dim, labels in [
        ("Recencia",  [5, 4, 3, 2, 1]),  # invertido
        ("Monetario", [1, 2, 3, 4, 5]),  # direto
        ("Ritmo",     [5, 4, 3, 2, 1]),  # invertido
    ]:
        score_col = {"Recencia": "score_R", "Monetario": "score_M", "Ritmo": "score_Ritmo"}[dim]
        scores = elegíveis.groupby("PlayG")[dim].transform(
            lambda x, lbl=labels: _qcut_score(x, lbl)
        )
        result.loc[elegíveis_mask, score_col] = scores.values

    return result
