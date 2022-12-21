from tcc.calculos import (
    calc_atraso,
    calc_deslocamento,
    calc_fila_max,
    calc_grau_sat,
    calc_num_paradas,
    calc_tempo_dissipacao,
    calc_tempo_fluxo_pelotao,
)


def test_calc_deslocamento() -> None:
    assert calc_deslocamento(100, 50) == 7.2


def test_calc_grau_sat() -> None:
    assert (
        calc_grau_sat(fluxo=100, fluxo_saturacao=1000, tempo_verde_efetivo=10, tempo_ciclo=100) == 1
    )


def test_calc_atraso() -> None:
    assert (
        calc_atraso(tempo_ciclo=100, tempo_verde_efetivo=50, grau_saturacao=0.5)
        == 16.666666666666668
    )


def test_calc_fila_max() -> None:
    assert round(calc_fila_max(tempo_ciclo=100, tempo_verde_efetivo=50, fluxo=1000), 2) == 13.89


def test_calc_tempo_dissipacao() -> None:
    assert (
        round(
            calc_tempo_dissipacao(
                tempo_ciclo=100, tempo_verde_efetivo=50, fluxo=100, fluxo_sat=1000
            ),
            3,
        )
        == 5.556
    )


def test_calc_num_paradas() -> None:
    assert (
        round(
            calc_num_paradas(tempo_ciclo=100, tempo_verde_efetivo=50, fluxo=100, fluxo_sat=1000), 3
        )
        == 1.543
    )


def test_calc_tempo_fluxo_pelotao() -> None:
    assert (
        calc_tempo_fluxo_pelotao(fluxo=100, fluxo_sat=1000, tempo_ciclo=100, ini=0, fim=20)
        == 8.88888888888889
    )
