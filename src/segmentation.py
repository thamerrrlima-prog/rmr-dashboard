"""
segmentation.py — Classificação RMR e GAP do Dashboard LigueLead.

Funções públicas:
    classify_rmr_segment(row) -> str
    classify_gap_status(gap_value, thresholds=None) -> str
    apply_segmentation(rmr_df, gap_thresholds=None) -> pd.DataFrame

Constantes:
    DEFAULT_GAP_THRESHOLDS
"""

import math
import pandas as pd


# ─── Constantes ───────────────────────────────────────────────────────────────

DEFAULT_GAP_THRESHOLDS = {
    "critico_max": -30,    # GAP < -30 → Crítico
    "atrasado_max": -8,    # -30 <= GAP < -8 → Atrasado
    "hora_max": 0,         # -8 <= GAP <= 0 → Hora de Comprar
    "em_breve_max": 7,     # 0 < GAP <= 7 → Em Breve
    # GAP > 7 → Folgado
}


# ─── Segmentação RMR ──────────────────────────────────────────────────────────

def classify_rmr_segment(row) -> str:
    """
    Classifica um cliente em um dos 8 segmentos RMR (ou Inelegível).

    Parâmetros
    ----------
    row : pd.Series
        Linha do DataFrame RMR com colunas score_R, score_M, score_Ritmo.
        Scores devem estar na escala 1–5 (float). NaN indica inelegível.

    Retorna
    -------
    str : nome do segmento.

    Ordem de prioridade:
        Campeões → Não Pode Perder → Leais → Novos Clientes →
        Potenciais Leais → Em Risco → Hibernando → Precisam Atenção
    """
    r = row["score_R"]
    m = row["score_M"]
    ritmo = row["score_Ritmo"]

    # Inelegível: qualquer score NaN
    if _is_nan(r) or _is_nan(m) or _is_nan(ritmo):
        return "Inelegível"

    # 1. Campeões: R >= 4 e M >= 4 e Ritmo >= 4
    if r >= 4 and m >= 4 and ritmo >= 4:
        return "Campeões"

    # 2. Não Pode Perder: R <= 2 e M == 5
    if r <= 2 and m == 5:
        return "Não Pode Perder"

    # 3. Leais: R >= 3 e M >= 3 e Ritmo >= 3
    if r >= 3 and m >= 3 and ritmo >= 3:
        return "Leais"

    # 4. Novos Clientes: R == 5 e (M <= 2 ou Ritmo <= 2)
    if r == 5 and (m <= 2 or ritmo <= 2):
        return "Novos Clientes"

    # 5. Potenciais Leais: R >= 3 e M >= 2
    if r >= 3 and m >= 2:
        return "Potenciais Leais"

    # 6. Em Risco: R <= 2 e M >= 3
    if r <= 2 and m >= 3:
        return "Em Risco"

    # 7. Hibernando: R <= 2 e M <= 2
    if r <= 2 and m <= 2:
        return "Hibernando"

    # 8. Precisam Atenção: todos os demais elegíveis
    return "Precisam Atenção"


# ─── Faixas de GAP ────────────────────────────────────────────────────────────

def classify_gap_status(gap_value, thresholds=None) -> str:
    """
    Classifica um valor de GAP em uma das 5 faixas (ou Inelegível).

    Parâmetros
    ----------
    gap_value : float
        Valor de GAP (pode ser NaN).
    thresholds : dict, optional
        Dicionário com limiares. Padrão: DEFAULT_GAP_THRESHOLDS.
        Chaves: critico_max, atrasado_max, hora_max, em_breve_max.

    Retorna
    -------
    str : faixa de GAP.
    """
    if thresholds is None:
        thresholds = DEFAULT_GAP_THRESHOLDS

    # Inelegível: GAP é NaN
    if _is_nan(gap_value):
        return "Inelegível"

    critico_max = thresholds["critico_max"]    # -30
    atrasado_max = thresholds["atrasado_max"]  # -8
    hora_max = thresholds["hora_max"]          # 0
    em_breve_max = thresholds["em_breve_max"]  # 7

    if gap_value < critico_max:
        return "Crítico"
    elif gap_value < atrasado_max:
        return "Atrasado"
    elif gap_value <= hora_max:
        return "Hora de Comprar"
    elif gap_value <= em_breve_max:
        return "Em Breve"
    else:
        return "Folgado"


# ─── Aplicar segmentação ao DataFrame ─────────────────────────────────────────

def apply_segmentation(rmr_df: pd.DataFrame, gap_thresholds=None) -> pd.DataFrame:
    """
    Adiciona colunas Segmento_RMR e Faixa_GAP ao DataFrame RMR.

    Parâmetros
    ----------
    rmr_df : pd.DataFrame
        Output de compute_rmr() com colunas score_R, score_M, score_Ritmo, GAP.
    gap_thresholds : dict, optional
        Limiares de GAP. Padrão: DEFAULT_GAP_THRESHOLDS.

    Retorna
    -------
    pd.DataFrame com as duas novas colunas adicionadas.
    """
    result = rmr_df.copy()
    result["Segmento_RMR"] = result.apply(classify_rmr_segment, axis=1)
    result["Faixa_GAP"] = result["GAP"].apply(
        lambda v: classify_gap_status(v, thresholds=gap_thresholds)
    )
    return result


# ─── Utilitários internos ─────────────────────────────────────────────────────

def _is_nan(value) -> bool:
    """Verifica se valor é NaN (compatível com float e numpy)."""
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False
