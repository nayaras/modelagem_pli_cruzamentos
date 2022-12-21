from tcc.grupo_movimento import GrupoMovimento


def test_new_semaforo() -> None:
    s = GrupoMovimento(id=0, fluxo=600, fluxo_saturacao=1200, velocidade_via=40, labels=("A", "B"))
    assert s.fluxo == 600
    assert s.fluxo_saturacao == 1200
    assert s.tempo_amarelo == 3
    assert s.labels == ("A", "B")
