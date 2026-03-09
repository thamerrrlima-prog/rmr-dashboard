"""
tests/test_rmr_engine.py — Testes para o motor de cálculo RMR.

Organização:
    TestRMRBasico — Recência, Monetário, Ritmo, GAP
    TestScores    — Quintis por PlayG com inversão
"""

import math
import numpy as np
import pandas as pd
import pytest

from src.rmr_engine import compute_rmr


# ─── Fixtures ────────────────────────────────────────────────────────────────

def _make_valid_df(rows: list[dict]) -> pd.DataFrame:
    """Constrói um DataFrame no formato de saída de get_valid_transactions()."""
    df = pd.DataFrame(rows)
    df["Data"] = pd.to_datetime(df["Data"])
    df["Valor"] = df["Valor"].astype(float)
    return df


# ─── TestRMRBasico ────────────────────────────────────────────────────────────

class TestRMRBasico:
    """Testes de R, M, Ritmo e GAP — sem scoring."""

    def _base_df(self):
        """Três clientes simples, referência fixa."""
        return _make_valid_df([
            # Cliente A — 3 compras, diffs 10 e 20 dias
            {"ID": "A", "Nome": "Alice",   "PlayG": "PG2", "Telefone": "11999", "Tipo": "Nova Compra", "Valor": 100.0, "Data": "2024-01-01"},
            {"ID": "A", "Nome": "Alice",   "PlayG": "PG2", "Telefone": "11999", "Tipo": "Nova Compra", "Valor": 200.0, "Data": "2024-01-11"},
            {"ID": "A", "Nome": "Alice",   "PlayG": "PG2", "Telefone": "11999", "Tipo": "Nova Compra", "Valor":  50.0, "Data": "2024-01-31"},
            # Cliente B — 1 compra
            {"ID": "B", "Nome": "Bob",     "PlayG": "PG2", "Telefone": "11888", "Tipo": "Nova Compra", "Valor": 300.0, "Data": "2024-02-15"},
            # Cliente C — 2 compras (diff = 5 dias)
            {"ID": "C", "Nome": "Carlos",  "PlayG": "PG2", "Telefone": "11777", "Tipo": "Nova Compra", "Valor": 150.0, "Data": "2024-03-01"},
            {"ID": "C", "Nome": "Carlos",  "PlayG": "PG2", "Telefone": "11777", "Tipo": "Nova Compra", "Valor":  50.0, "Data": "2024-03-06"},
        ])

    # reference_date: 2024-02-10
    _REF = pd.Timestamp("2024-02-10")

    def test_ritmo_tres_compras(self):
        """Cliente com 3 compras com diffs 10 e 20 dias → Ritmo == 15.0."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        assert df.loc["A", "Ritmo"] == pytest.approx(15.0)

    def test_ritmo_uma_compra_nan(self):
        """Cliente com 1 compra → Ritmo is NaN."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        assert math.isnan(df.loc["B", "Ritmo"])

    def test_gap_uma_compra_nan(self):
        """Cliente com 1 compra → GAP is NaN."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        assert math.isnan(df.loc["B", "GAP"])

    def test_recencia_ultima_compra_e_referencia(self):
        """Recência = 0 quando última compra == reference_date."""
        rows = [
            {"ID": "Z", "Nome": "Zero", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 50.0, "Data": "2024-06-01"},
            {"ID": "Z", "Nome": "Zero", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 50.0, "Data": "2024-06-11"},
        ]
        ref = pd.Timestamp("2024-06-11")
        df = compute_rmr(_make_valid_df(rows), reference_date=ref)
        assert df.loc["Z", "Recencia"] == 0

    def test_monetario_soma_tres_transacoes(self):
        """Monetário de cliente com transações [100, 200, 50] → 350.0."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        assert df.loc["A", "Monetario"] == pytest.approx(350.0)

    def test_gap_ritmo_menos_recencia(self):
        """GAP = Ritmo - Recencia. Cliente C: Ritmo=5, Recencia=341 → GAP=-336."""
        # reference_date fixo em 2024-02-10 → última compra de C é 2024-03-06 (ainda no futuro)
        # Usar referência depois das compras de C
        ref = pd.Timestamp("2024-04-10")
        df = compute_rmr(self._base_df(), reference_date=ref)
        expected_recencia = (ref - pd.Timestamp("2024-03-06")).days
        expected_ritmo = 5.0
        expected_gap = expected_ritmo - expected_recencia
        assert df.loc["C", "GAP"] == pytest.approx(expected_gap)

    def test_ritmo_usa_datas_unicas(self):
        """Ritmo usa datas únicas — duas transações no mesmo dia contam como 1."""
        rows = [
            # Mesmo dia duas vezes + 10 dias depois
            {"ID": "D", "Nome": "Duda", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 50.0, "Data": "2024-01-01"},
            {"ID": "D", "Nome": "Duda", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 50.0, "Data": "2024-01-01"},
            {"ID": "D", "Nome": "Duda", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 50.0, "Data": "2024-01-11"},
        ]
        ref = pd.Timestamp("2024-02-01")
        df = compute_rmr(_make_valid_df(rows), reference_date=ref)
        # 2 datas distintas → 1 diff de 10 dias → Ritmo = 10.0
        assert df.loc["D", "Ritmo"] == pytest.approx(10.0)

    def test_colunas_resultado(self):
        """DataFrame retornado contém colunas canônicas."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        for col in ["Nome", "PlayG", "Telefone", "Recencia", "Monetario", "Ritmo", "GAP"]:
            assert col in df.columns, f"Coluna ausente: {col}"

    def test_index_e_id(self):
        """Index do DataFrame retornado é o ID do cliente."""
        df = compute_rmr(self._base_df(), reference_date=self._REF)
        assert "A" in df.index
        assert "B" in df.index
        assert "C" in df.index


# ─── TestScores ───────────────────────────────────────────────────────────────

class TestScores:
    """Testes de scoring por quintis por PlayG com inversão."""

    def _score_df(self):
        """
        10 clientes em 2 PlayGs (5 em PG2, 5 em PG3) — suficiente para 5 quintis.
        Todos com >= 2 compras para serem elegíveis.
        """
        ref = pd.Timestamp("2024-12-31")
        rows = []
        # PG2: 5 clientes
        # Recências (dias até ref): 10, 20, 30, 40, 50  (cliente R1 tem menor Recencia → score_R=5)
        # Monetários: 100, 200, 300, 400, 500            (cliente M5 tem maior → score_M=5)
        # Ritmos (via diffs): 5, 10, 15, 20, 25          (cliente T1 tem menor Ritmo → score_Ritmo=5)
        for i, (client_id, recencia_days, valor_total, ritmo) in enumerate([
            ("PG2_R1", 10, 100, 5),
            ("PG2_R2", 20, 200, 10),
            ("PG2_R3", 30, 300, 15),
            ("PG2_R4", 40, 400, 20),
            ("PG2_R5", 50, 500, 25),
        ]):
            ultima_compra = ref - pd.Timedelta(days=recencia_days)
            primeira_compra = ultima_compra - pd.Timedelta(days=ritmo)
            rows.append({
                "ID": client_id, "Nome": client_id, "PlayG": "PG2",
                "Telefone": "0", "Tipo": "Nova Compra",
                "Valor": valor_total / 2,
                "Data": primeira_compra.strftime("%Y-%m-%d"),
            })
            rows.append({
                "ID": client_id, "Nome": client_id, "PlayG": "PG2",
                "Telefone": "0", "Tipo": "Nova Compra",
                "Valor": valor_total / 2,
                "Data": ultima_compra.strftime("%Y-%m-%d"),
            })

        # PG3: 5 clientes com valores distintos (não afetam quintis de PG2)
        for client_id, recencia_days, valor_total, ritmo in [
            ("PG3_R1", 100, 1000, 50),
            ("PG3_R2", 200, 2000, 100),
            ("PG3_R3", 300, 3000, 150),
            ("PG3_R4", 400, 4000, 200),
            ("PG3_R5", 500, 5000, 250),
        ]:
            ultima_compra = ref - pd.Timedelta(days=recencia_days)
            primeira_compra = ultima_compra - pd.Timedelta(days=ritmo)
            rows.append({
                "ID": client_id, "Nome": client_id, "PlayG": "PG3",
                "Telefone": "0", "Tipo": "Nova Compra",
                "Valor": valor_total / 2,
                "Data": primeira_compra.strftime("%Y-%m-%d"),
            })
            rows.append({
                "ID": client_id, "Nome": client_id, "PlayG": "PG3",
                "Telefone": "0", "Tipo": "Nova Compra",
                "Valor": valor_total / 2,
                "Data": ultima_compra.strftime("%Y-%m-%d"),
            })

        return _make_valid_df(rows), ref

    def test_score_r_invertido_menor_recencia_score_5(self):
        """Dentro de um PlayG, cliente com menor Recencia tem score_R == 5."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R1", "score_R"] == 5

    def test_score_r_invertido_maior_recencia_score_1(self):
        """Dentro de um PlayG, cliente com maior Recencia tem score_R == 1."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R5", "score_R"] == 1

    def test_score_m_direto_maior_monetario_score_5(self):
        """Dentro de um PlayG, cliente com maior Monetario tem score_M == 5."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R5", "score_M"] == 5

    def test_score_m_direto_menor_monetario_score_1(self):
        """Dentro de um PlayG, cliente com menor Monetario tem score_M == 1."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R1", "score_M"] == 1

    def test_score_ritmo_invertido_menor_ritmo_score_5(self):
        """Dentro de um PlayG, cliente com menor Ritmo tem score_Ritmo == 5."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R1", "score_Ritmo"] == 5

    def test_score_ritmo_invertido_maior_ritmo_score_1(self):
        """Dentro de um PlayG, cliente com maior Ritmo tem score_Ritmo == 1."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        assert df.loc["PG2_R5", "score_Ritmo"] == 1

    def test_scores_independentes_por_playg(self):
        """Clientes de PlayGs diferentes têm scores calculados independentemente."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        # PG3_R1 tem menor Recencia dentro de PG3 → score_R deve ser 5
        assert df.loc["PG3_R1", "score_R"] == 5
        # PG3_R5 tem maior Monetario dentro de PG3 → score_M deve ser 5
        assert df.loc["PG3_R5", "score_M"] == 5

    def test_cliente_uma_compra_scores_nan(self):
        """Cliente com 1 compra (Ritmo NaN) tem score_R, score_M, score_Ritmo == NaN."""
        rows = [
            # 5 clientes elegíveis
            {"ID": "E1", "Nome": "E1", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 100.0, "Data": "2024-01-01"},
            {"ID": "E1", "Nome": "E1", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 100.0, "Data": "2024-01-15"},
            {"ID": "E2", "Nome": "E2", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 200.0, "Data": "2024-01-01"},
            {"ID": "E2", "Nome": "E2", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 200.0, "Data": "2024-01-20"},
            {"ID": "E3", "Nome": "E3", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 300.0, "Data": "2024-01-01"},
            {"ID": "E3", "Nome": "E3", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 300.0, "Data": "2024-01-25"},
            {"ID": "E4", "Nome": "E4", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 400.0, "Data": "2024-01-01"},
            {"ID": "E4", "Nome": "E4", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 400.0, "Data": "2024-01-30"},
            {"ID": "E5", "Nome": "E5", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 500.0, "Data": "2024-01-01"},
            {"ID": "E5", "Nome": "E5", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 500.0, "Data": "2024-02-04"},
            # 1 cliente inelegível (apenas 1 compra)
            {"ID": "SOLO", "Nome": "Solo", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 999.0, "Data": "2024-03-01"},
        ]
        ref = pd.Timestamp("2024-06-01")
        df = compute_rmr(_make_valid_df(rows), reference_date=ref)
        assert math.isnan(df.loc["SOLO", "score_R"])
        assert math.isnan(df.loc["SOLO", "score_M"])
        assert math.isnan(df.loc["SOLO", "score_Ritmo"])

    def test_colunas_score_presentes(self):
        """DataFrame retornado contém colunas score_R, score_M, score_Ritmo."""
        df_in, ref = self._score_df()
        df = compute_rmr(df_in, reference_date=ref)
        for col in ["score_R", "score_M", "score_Ritmo"]:
            assert col in df.columns, f"Coluna ausente: {col}"


# ─── Teste de integração básico ───────────────────────────────────────────────

def test_rmr_basico():
    """Smoke test: compute_rmr executa sem erros com dataset mínimo."""
    rows = [
        {"ID": "X1", "Nome": "X1", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 100.0, "Data": "2024-01-01"},
        {"ID": "X1", "Nome": "X1", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 200.0, "Data": "2024-01-15"},
        {"ID": "X2", "Nome": "X2", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 150.0, "Data": "2024-01-05"},
        {"ID": "X2", "Nome": "X2", "PlayG": "PG2", "Telefone": "0", "Tipo": "Nova Compra", "Valor": 150.0, "Data": "2024-01-20"},
    ]
    ref = pd.Timestamp("2024-06-01")
    df = compute_rmr(_make_valid_df(rows), reference_date=ref)
    assert len(df) == 2
    assert "Recencia" in df.columns
