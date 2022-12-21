import pytest
from docplex.mp.model import Model

from tcc.cruzamento import Cruzamento
from tcc.grafo import Grafo
from tcc.grupo_movimento import GrupoMovimento
from tcc.linear_programming.model import (
    calc_primeira_parte_num_paradas,
    create_var_and_restricoes_por_cruzamento,
    get_max,
    get_min,
    run_model_semaforo,
)
from tcc.load_data import ConexaoCruzamentos


def test_get_max() -> None:
    m = Model(name="semaforo")
    get_max(m, ini_entrada=0, ini_saida=10, label="test")
    m.solve()
    assert m.get_var_by_name("test").solution_value == 10


def test_get_min() -> None:
    m = Model(name="semaforo")
    get_min(m, fim_entrada=0, fim_saida=10, label="test")
    m.solve()
    assert m.get_var_by_name("test").solution_value == 0


def test_create_var_and_restricoes_por_cruzamento() -> None:
    g = Grafo([(0, 1), (1, 0)])
    m = Model(name="semaforo")

    # variaveis nao existem
    assert m.get_var_by_name("i0_0") is None
    assert m.get_var_by_name("i0_1") is None
    assert m.get_var_by_name("f0_0") is None
    assert m.get_var_by_name("f0_1") is None

    create_var_and_restricoes_por_cruzamento(
        model=m,
        grafo_incomp=g,
        tempo_ciclo=m.continuous_var(0, 100, name="tempo_ciclo"),
        fluxos=[100.0, 200.0],
        fluxos_sat=[1000, 2000],
        tempos_amarelo=[0, 0],
        cruzamento_id=0,
    )
    assert m.get_var_by_name("i0_0") is not None
    assert m.get_var_by_name("i0_1")
    assert m.get_var_by_name("f0_0")
    assert m.get_var_by_name("f0_1")


def test_calc_primeira_parte_num_paradas_without_exclude_vertices() -> None:
    calc_primeira_parte_num_paradas([10, 20], [100, 100]) == [11.11, 25]


def test_calc_primeira_parte_num_paradas_with_exclude_vertices() -> None:
    calc_primeira_parte_num_paradas([10, 20], [100, 100], [0]) == [25]


def test_calc_sum_numero_paradas() -> None:
    pass


# @pytest.mark.skip()
def test_run_model_semaforo() -> None:

    g1 = Grafo([(0, 1), (1, 0)])
    g2 = Grafo([(0, 1), (1, 0)])

    # grupos de mov for g1
    gm1_1 = GrupoMovimento(
        id=0, fluxo=120, fluxo_saturacao=1200, velocidade_via=40, labels=("A", "B")
    )
    gm1_2 = GrupoMovimento(
        id=1, fluxo=120, fluxo_saturacao=1200, velocidade_via=40, labels=("C", "D")
    )

    # grupos de mov for g2
    gm2_1 = GrupoMovimento(
        id=0, fluxo=120, fluxo_saturacao=1200, velocidade_via=40, labels=("A", "B")
    )
    gm2_2 = GrupoMovimento(
        id=1, fluxo=120, fluxo_saturacao=1200, velocidade_via=40, labels=("C", "D")
    )

    grupos_mov = []
    grupos_mov.append([gm1_1, gm1_2])
    grupos_mov.append([gm2_1, gm2_2])

    cruzamentos = []
    conexao_cruzamentos = {}
    # B do cruzamento 0 -> A do cruzamento 1
    conexao_cruzamentos[ConexaoCruzamentos(cruzamento_inicial=0, cruzamento_final=1)] = [
        (0, 0, 1.0, 10)
    ]
    id = 0
    for grupo, grafo in zip(grupos_mov, [g1, g2]):
        prox_cruz = [
            key.cruzamento_final
            for key in conexao_cruzamentos.keys()
            if key.cruzamento_inicial == id
        ]
        cruzamentos.append(
            Cruzamento(
                grupos_movimento=grupo,
                grafo_incompatibilidade=grafo,
                id=id,
                pares_vertices=[
                    value
                    for (key, value) in conexao_cruzamentos.items()
                    if key.cruzamento_inicial == id
                ],
                id_prox_cruzamento=prox_cruz[0] if len(prox_cruz) > 0 else None,
            )
        )
        id += 1
    run_model_semaforo(
        cruzamentos,
        conexao_cruzamentos,
        tempo_ciclo=100,
        solucao_inicial=None,
        print_detalhes=False,
    )
