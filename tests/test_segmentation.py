"""
test_segmentation.py — Testes para src/segmentation.py

Cobre:
- 8 segmentos RMR baseados em score_R, score_M, score_Ritmo
- 5 faixas de GAP + Inelegível
- Cliente inelegível (scores NaN) → "Inelegível"
"""

import math
import pandas as pd
import pytest

from src.segmentation import (
    classify_rmr_segment,
    classify_gap_status,
    apply_segmentation,
    DEFAULT_GAP_THRESHOLDS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _row(score_r, score_m, score_ritmo):
    """Cria uma linha de DataFrame simulando saída do rmr_engine."""
    return pd.Series({
        "score_R": score_r,
        "score_M": score_m,
        "score_Ritmo": score_ritmo,
    })


# ─── Testes: classify_rmr_segment ─────────────────────────────────────────────

class TestClassifyRMRSegment:

    def test_campeoes_scores_5_5_5(self):
        row = _row(score_r=5, score_m=5, score_ritmo=5)
        assert classify_rmr_segment(row) == "Campeões"

    def test_campeoes_scores_minimos(self):
        """R=4, M=4, Ritmo=4 → Campeões (limiar mínimo)."""
        row = _row(score_r=4, score_m=4, score_ritmo=4)
        assert classify_rmr_segment(row) == "Campeões"

    def test_nao_pode_perder_r1_m5(self):
        """R=1, M=5 → Não Pode Perder (prioridade sobre Em Risco)."""
        row = _row(score_r=1, score_m=5, score_ritmo=3)
        assert classify_rmr_segment(row) == "Não Pode Perder"

    def test_nao_pode_perder_r2_m5(self):
        """R=2, M=5 → Não Pode Perder."""
        row = _row(score_r=2, score_m=5, score_ritmo=2)
        assert classify_rmr_segment(row) == "Não Pode Perder"

    def test_leais_r3_m3_ritmo3(self):
        """R=3, M=3, Ritmo=3 → Leais (não é Campeões)."""
        row = _row(score_r=3, score_m=3, score_ritmo=3)
        assert classify_rmr_segment(row) == "Leais"

    def test_leais_r4_m3_ritmo3(self):
        row = _row(score_r=4, score_m=3, score_ritmo=3)
        assert classify_rmr_segment(row) == "Leais"

    def test_novos_clientes_r5_m1(self):
        """R=5, M=1 → Novos Clientes (M<=2 ou Ritmo<=2)."""
        row = _row(score_r=5, score_m=1, score_ritmo=3)
        assert classify_rmr_segment(row) == "Novos Clientes"

    def test_novos_clientes_r5_ritmo1(self):
        """R=5, Ritmo=1 → Novos Clientes."""
        row = _row(score_r=5, score_m=3, score_ritmo=1)
        assert classify_rmr_segment(row) == "Novos Clientes"

    def test_potenciais_leais_r3_m2(self):
        """R=3, M=2 → Potenciais Leais (não nas anteriores)."""
        row = _row(score_r=3, score_m=2, score_ritmo=2)
        assert classify_rmr_segment(row) == "Potenciais Leais"

    def test_em_risco_r2_m3(self):
        """R=2, M=3 → Em Risco."""
        row = _row(score_r=2, score_m=3, score_ritmo=3)
        assert classify_rmr_segment(row) == "Em Risco"

    def test_em_risco_r1_m4(self):
        """R=1, M=4 → Em Risco (M>=3, R<=2, não é Não Pode Perder)."""
        row = _row(score_r=1, score_m=4, score_ritmo=2)
        assert classify_rmr_segment(row) == "Em Risco"

    def test_hibernando_r1_m2(self):
        """R=1, M=2 → Hibernando."""
        row = _row(score_r=1, score_m=2, score_ritmo=1)
        assert classify_rmr_segment(row) == "Hibernando"

    def test_hibernando_r2_m2(self):
        row = _row(score_r=2, score_m=2, score_ritmo=2)
        assert classify_rmr_segment(row) == "Hibernando"

    def test_precisam_atencao_demais(self):
        """Scores que não se encaixam em nenhuma outra categoria → Precisam Atenção."""
        row = _row(score_r=3, score_m=1, score_ritmo=3)
        assert classify_rmr_segment(row) == "Precisam Atenção"

    def test_inelegivel_scores_nan(self):
        """Qualquer score NaN → Inelegível."""
        row = _row(score_r=float("nan"), score_m=float("nan"), score_ritmo=float("nan"))
        assert classify_rmr_segment(row) == "Inelegível"

    def test_inelegivel_score_ritmo_nan(self):
        """score_Ritmo NaN (cliente 1 compra) → Inelegível."""
        row = _row(score_r=5, score_m=5, score_ritmo=float("nan"))
        assert classify_rmr_segment(row) == "Inelegível"

    def test_inelegivel_score_r_nan(self):
        """score_R NaN → Inelegível."""
        row = _row(score_r=float("nan"), score_m=3, score_ritmo=3)
        assert classify_rmr_segment(row) == "Inelegível"


# ─── Testes: classify_gap_status ──────────────────────────────────────────────

class TestClassifyGAPStatus:

    def test_critico_gap_menos_40(self):
        """GAP=-40 → Crítico."""
        assert classify_gap_status(-40) == "Crítico"

    def test_critico_gap_exato_limite(self):
        """GAP=-31 → Crítico (< -30)."""
        assert classify_gap_status(-31) == "Crítico"

    def test_atrasado_gap_menos_15(self):
        """GAP=-15 → Atrasado."""
        assert classify_gap_status(-15) == "Atrasado"

    def test_atrasado_gap_menos_30(self):
        """GAP=-30 → Atrasado (limite inferior: -30 <= GAP < -8)."""
        assert classify_gap_status(-30) == "Atrasado"

    def test_atrasado_gap_menos_9(self):
        """GAP=-9 → Atrasado."""
        assert classify_gap_status(-9) == "Atrasado"

    def test_hora_de_comprar_gap_0(self):
        """GAP=0 → Hora de Comprar."""
        assert classify_gap_status(0) == "Hora de Comprar"

    def test_hora_de_comprar_gap_menos_8(self):
        """GAP=-8 → Hora de Comprar (limite: -8 <= GAP <= 0)."""
        assert classify_gap_status(-8) == "Hora de Comprar"

    def test_em_breve_gap_5(self):
        """GAP=5 → Em Breve."""
        assert classify_gap_status(5) == "Em Breve"

    def test_em_breve_gap_7(self):
        """GAP=7 → Em Breve (limite: 0 < GAP <= 7)."""
        assert classify_gap_status(7) == "Em Breve"

    def test_em_breve_gap_1(self):
        """GAP=1 → Em Breve."""
        assert classify_gap_status(1) == "Em Breve"

    def test_folgado_gap_20(self):
        """GAP=20 → Folgado."""
        assert classify_gap_status(20) == "Folgado"

    def test_folgado_gap_8(self):
        """GAP=8 → Folgado (> 7)."""
        assert classify_gap_status(8) == "Folgado"

    def test_inelegivel_gap_nan(self):
        """GAP=NaN → Inelegível."""
        assert classify_gap_status(float("nan")) == "Inelegível"

    def test_inelegivel_gap_nan_math(self):
        """GAP=math.nan → Inelegível."""
        assert classify_gap_status(math.nan) == "Inelegível"

    def test_default_thresholds_exportados(self):
        """DEFAULT_GAP_THRESHOLDS deve existir e ter as chaves corretas."""
        assert "critico_max" in DEFAULT_GAP_THRESHOLDS
        assert "atrasado_max" in DEFAULT_GAP_THRESHOLDS
        assert "hora_max" in DEFAULT_GAP_THRESHOLDS
        assert "em_breve_max" in DEFAULT_GAP_THRESHOLDS

    def test_custom_thresholds(self):
        """Limiares customizados devem ser respeitados."""
        custom = {
            "critico_max": -60,
            "atrasado_max": -20,
            "hora_max": 0,
            "em_breve_max": 14,
        }
        # GAP=-40 com limiar critico_max=-60 → Atrasado (não Crítico)
        assert classify_gap_status(-40, thresholds=custom) == "Atrasado"


# ─── Testes: apply_segmentation ───────────────────────────────────────────────

class TestApplySegmentation:

    def _make_rmr_df(self):
        """Cria DataFrame mínimo simulando saída de compute_rmr + assign_scores."""
        data = {
            "Nome": ["Alice", "Bob", "Carlos"],
            "PlayG": ["PG2", "PG3", "PG2"],
            "Telefone": ["11111", "22222", "33333"],
            "Recencia": [5, 30, 100],
            "Monetario": [500.0, 200.0, 800.0],
            "Ritmo": [10.0, 25.0, float("nan")],
            "GAP": [5.0, -5.0, float("nan")],
            "score_R": [5.0, 3.0, float("nan")],
            "score_M": [5.0, 2.0, float("nan")],
            "score_Ritmo": [5.0, 3.0, float("nan")],
        }
        return pd.DataFrame(data, index=pd.Index([101, 102, 103], name="ID"))

    def test_adiciona_coluna_segmento_rmr(self):
        df = self._make_rmr_df()
        result = apply_segmentation(df)
        assert "Segmento_RMR" in result.columns

    def test_adiciona_coluna_faixa_gap(self):
        df = self._make_rmr_df()
        result = apply_segmentation(df)
        assert "Faixa_GAP" in result.columns

    def test_cliente_inelegivel_segmento_inelegivel(self):
        """Carlos tem scores NaN → Segmento_RMR = Inelegível."""
        df = self._make_rmr_df()
        result = apply_segmentation(df)
        assert result.loc[103, "Segmento_RMR"] == "Inelegível"

    def test_cliente_inelegivel_faixa_inelegivel(self):
        """Carlos tem GAP NaN → Faixa_GAP = Inelegível."""
        df = self._make_rmr_df()
        result = apply_segmentation(df)
        assert result.loc[103, "Faixa_GAP"] == "Inelegível"

    def test_nao_altera_outras_colunas(self):
        """apply_segmentation não deve modificar colunas existentes."""
        df = self._make_rmr_df()
        original_recencia = df["Recencia"].copy()
        result = apply_segmentation(df)
        pd.testing.assert_series_equal(result["Recencia"], original_recencia)

    def test_retorna_dataframe(self):
        df = self._make_rmr_df()
        result = apply_segmentation(df)
        assert isinstance(result, pd.DataFrame)
