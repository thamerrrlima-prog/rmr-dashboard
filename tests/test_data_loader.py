"""
Testes automatizados para src/data_loader.py
Camada de ingestão de dados do Dashboard RMR LigueLead.
"""
import pytest
import pandas as pd
from io import BytesIO
from src.data_loader import load_base_bu, load_historico, get_valid_transactions, validate_columns


# ─── Fixtures ──────────────────────────────────────────────────────────────────

def make_base_bu_df():
    """DataFrame típico de Base B.U. com um cliente PG1 incluído."""
    return pd.DataFrame({
        "ID": [1, 2, 3, 4],
        "Nome": ["Alice", "Bob", "Carlos", "Diana"],
        "PlayG": ["PG2", "PG3", "PG1", "PG8"],
        "Telefone": ["11999990001", "11999990002", "11999990003", "11999990004"],
    })


def make_base_bu_xlsx():
    """BytesIO simulando upload de Base B.U."""
    df = make_base_bu_df()
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf


def make_historico_df():
    """DataFrame típico de Histórico de Crédito."""
    return pd.DataFrame({
        "ID": [1, 1, 2, 3, 4, 4, 2, 1],
        "Tipo": [
            "Nova Compra",      # válida
            "Troca de Crédito", # inválida: tipo errado
            "Pagamento",        # válida
            "Nova Compra",      # PG1 — excluída pelo join
            "Nova Compra",      # válida PG8
            "Bônus/Desconto",   # inválida: tipo errado
            "Nova Compra",      # inválida: valor 0
            "Pagamento",        # inválida: data anterior a 2024
        ],
        "Valor": [500.0, 200.0, 300.0, 150.0, 800.0, 100.0, 0.0, 400.0],
        "Data": [
            pd.Timestamp("2024-06-01"),
            pd.Timestamp("2024-07-01"),
            pd.Timestamp("2024-08-01"),
            pd.Timestamp("2024-09-01"),
            pd.Timestamp("2025-01-15"),
            pd.Timestamp("2024-10-01"),
            pd.Timestamp("2024-11-01"),
            pd.Timestamp("2023-12-31"),  # anterior a 2024
        ],
    })


def make_historico_xlsx():
    """BytesIO simulando upload de Histórico de Crédito."""
    df = make_historico_df()
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf


# ─── Testes: load_base_bu ──────────────────────────────────────────────────────

class TestLoadBaseBu:
    def test_retorna_dataframe(self):
        """load_base_bu deve retornar um DataFrame."""
        result = load_base_bu(make_base_bu_xlsx())
        assert isinstance(result, pd.DataFrame)

    def test_colunas_canonicas_presentes(self):
        """Resultado deve conter as colunas canônicas ID, Nome, PlayG, Telefone."""
        result = load_base_bu(make_base_bu_xlsx())
        for col in ["ID", "Nome", "PlayG", "Telefone"]:
            assert col in result.columns, f"Coluna '{col}' ausente"

    def test_exclui_pg1(self):
        """Clientes de PG1 devem ser removidos."""
        result = load_base_bu(make_base_bu_xlsx())
        assert "PG1" not in result["PlayG"].values
        assert 3 not in result["ID"].values  # ID 3 é PG1

    def test_mantem_outros_playg(self):
        """Clientes de PG2, PG3, PG8 devem ser mantidos."""
        result = load_base_bu(make_base_bu_xlsx())
        assert len(result) == 3  # 4 clientes - 1 PG1

    def test_aceita_file_like(self):
        """load_base_bu deve aceitar BytesIO (Streamlit uploader)."""
        buf = make_base_bu_xlsx()
        result = load_base_bu(buf)
        assert isinstance(result, pd.DataFrame)

    def test_erro_coluna_ausente(self):
        """Deve levantar ValueError se coluna obrigatória ausente."""
        df_invalido = pd.DataFrame({"ID": [1], "Nome": ["X"]})  # faltam PlayG e Telefone
        buf = BytesIO()
        df_invalido.to_excel(buf, index=False)
        buf.seek(0)
        with pytest.raises(ValueError, match="(?i)(coluna|obrigat)"):
            load_base_bu(buf)


# ─── Testes: load_historico ────────────────────────────────────────────────────

class TestLoadHistorico:
    def test_retorna_dataframe(self):
        """load_historico deve retornar um DataFrame."""
        result = load_historico(make_historico_xlsx())
        assert isinstance(result, pd.DataFrame)

    def test_coluna_data_e_datetime(self):
        """Coluna de data deve ser dtype datetime."""
        result = load_historico(make_historico_xlsx())
        data_col = [c for c in result.columns if "data" in c.lower()]
        assert len(data_col) >= 1, "Nenhuma coluna de data encontrada"
        assert pd.api.types.is_datetime64_any_dtype(result[data_col[0]])

    def test_aceita_file_like(self):
        """load_historico deve aceitar BytesIO."""
        result = load_historico(make_historico_xlsx())
        assert isinstance(result, pd.DataFrame)

    def test_preserva_todas_colunas(self):
        """Deve preservar todas as colunas originais do arquivo."""
        result = load_historico(make_historico_xlsx())
        for col in ["ID", "Tipo", "Valor", "Data"]:
            assert col in result.columns

    def test_erro_coluna_ausente(self):
        """Deve levantar ValueError se coluna obrigatória ausente."""
        df_invalido = pd.DataFrame({"ID": [1], "Outro": ["X"]})  # faltam Tipo, Valor, Data
        buf = BytesIO()
        df_invalido.to_excel(buf, index=False)
        buf.seek(0)
        with pytest.raises(ValueError, match="(?i)(coluna|obrigat)"):
            load_historico(buf)


# ─── Testes: get_valid_transactions ───────────────────────────────────────────

class TestGetValidTransactions:
    def setup_method(self):
        """Prepara DataFrames base para cada teste."""
        self.base_df = load_base_bu(make_base_bu_xlsx())
        self.hist_df = load_historico(make_historico_xlsx())

    def test_descarta_troca_credito(self):
        """Transação com tipo 'Troca de Crédito' deve ser descartada."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        assert "Troca de Crédito" not in result["Tipo"].str.strip().values

    def test_descarta_bonus_desconto(self):
        """Transação com tipo 'Bônus/Desconto' deve ser descartada."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        assert "Bônus/Desconto" not in result["Tipo"].str.strip().values

    def test_descarta_valor_zero(self):
        """Transação com valor 0 deve ser descartada."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        assert (result["Valor"] <= 0).sum() == 0

    def test_descarta_data_anterior_2024(self):
        """Transação com data 2023-12-31 deve ser descartada."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        data_col = [c for c in result.columns if "data" in c.lower()][0]
        assert (result[data_col] < pd.Timestamp("2024-01-01")).sum() == 0

    def test_descarta_pg1(self):
        """Clientes de PG1 não devem aparecer no resultado."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        # ID 3 é PG1 — não deve estar no resultado
        assert 3 not in result["ID"].values

    def test_mantem_nova_compra_valida(self):
        """Transação com tipo 'Nova Compra', valor 500, data 2024-06-01 deve ser mantida."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        nova_compra = result[
            (result["Tipo"].str.strip() == "Nova Compra") &
            (result["Valor"] == 500.0)
        ]
        assert len(nova_compra) == 1

    def test_mantem_pagamento_valido(self):
        """Transação com tipo 'Pagamento' válida deve ser mantida."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        assert "Pagamento" in result["Tipo"].str.strip().values

    def test_colunas_minimas_presentes(self):
        """Resultado deve conter colunas de base (ID, Nome, PlayG, Telefone) + colunas de transação."""
        result = get_valid_transactions(self.base_df, self.hist_df)
        for col in ["ID", "Nome", "PlayG", "Telefone", "Tipo", "Valor"]:
            assert col in result.columns, f"Coluna '{col}' ausente no resultado"


# ─── Testes: validate_columns ─────────────────────────────────────────────────

class TestValidateColumns:
    def test_normaliza_colunas_renomeadas(self):
        """Arquivo com coluna 'id_cliente' deve ser normalizado para 'ID'."""
        df = pd.DataFrame({
            "id_cliente": [1],
            "nome do cliente": ["Alice"],
            "playg": ["PG2"],
            "telefone": ["11999990001"],
        })
        result = validate_columns(df, {"ID": ["id", "id_cliente", "id cliente"],
                                        "Nome": ["nome", "nome do cliente"],
                                        "PlayG": ["playg", "play g", "play_g"],
                                        "Telefone": ["telefone", "fone", "celular"]},
                                   "base_bu.xlsx")
        assert "ID" in result.columns
        assert "Nome" in result.columns
        assert "PlayG" in result.columns
        assert "Telefone" in result.columns

    def test_levanta_valueerror_coluna_ausente(self):
        """Deve levantar ValueError com mensagem clara quando coluna obrigatória ausente."""
        df = pd.DataFrame({"ID": [1]})
        with pytest.raises(ValueError) as exc_info:
            validate_columns(df, {"ID": ["id"], "Nome": ["nome"]}, "arquivo_teste.xlsx")
        assert "arquivo_teste.xlsx" in str(exc_info.value)

    def test_mensagem_erro_descritiva(self):
        """Mensagem de erro deve mencionar o arquivo e as colunas esperadas."""
        df = pd.DataFrame({"outro": [1]})
        with pytest.raises(ValueError) as exc_info:
            validate_columns(df, {"ID": ["id"]}, "historico.xlsx")
        msg = str(exc_info.value)
        assert "historico.xlsx" in msg
