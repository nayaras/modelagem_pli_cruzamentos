from pathlib import Path

from tcc.load_data import ConexaoCruzamentos, load_csv_conexao


def test_load_csv_conexao() -> None:
    """conn.csv
    cruzamento_inicial;cruzamento_final;grupo_mov_saida;grupo_mov_chegada;fracao;dist;vel
    0;1;0;0;1;200;40
    0;1;1;2;0.5;200;40
    """
    assert load_csv_conexao(path=Path("tests/files/conn.csv")) == {
        ConexaoCruzamentos(cruzamento_inicial=0, cruzamento_final=1): [
            (0, 0, 1.0, 18.0),
            (1, 2, 0.5, 18.0),
        ]
    }
