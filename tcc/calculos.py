segundos = float
ucp_por_hora = float


def calc_tempo_fluxo_pelotao(
    fluxo: ucp_por_hora,
    fluxo_sat: ucp_por_hora,
    tempo_ciclo: segundos,
    ini,
    fim,
):
    tempo_nao_verde = tempo_ciclo - (fim - ini)
    tempo_pelotao = tempo_nao_verde * (fluxo / fluxo_sat) / (1 - (fluxo / fluxo_sat))
    return tempo_pelotao


def calc_deslocamento(distancia: float, velocidade: int) -> segundos:
    """distancia em metros
    velocidade em km/h
    deslocamento em segundos"""
    return distancia / (velocidade / 3.6)


def calc_grau_sat(
    fluxo: ucp_por_hora,
    fluxo_saturacao: float,
    tempo_verde_efetivo: segundos,
    tempo_ciclo: segundos,
) -> float:
    """Fluxo (ucp/h)/ capacidade (ucp/h)"""
    cap = fluxo_saturacao * (tempo_verde_efetivo / tempo_ciclo)
    return fluxo / cap


def calc_atraso(
    tempo_ciclo: segundos, tempo_verde_efetivo: segundos, grau_saturacao: float
) -> float:
    """Atraso uniforme em segundos"""
    fracao_verde = tempo_verde_efetivo / tempo_ciclo
    atraso = (tempo_ciclo * (1 - fracao_verde) * (1 - fracao_verde)) / (
        2 * (1 - fracao_verde * grau_saturacao)
    )
    return atraso


def calc_fila_max(
    tempo_ciclo: segundos, tempo_verde_efetivo: segundos, fluxo: ucp_por_hora
) -> float:
    """Fila máxima em ucp"""
    return fluxo * (tempo_ciclo - tempo_verde_efetivo) / 3600


def calc_tempo_dissipacao(
    tempo_ciclo: segundos,
    tempo_verde_efetivo: segundos,
    fluxo: ucp_por_hora,
    fluxo_sat: ucp_por_hora,
) -> segundos:
    """Tempo para dissipação da fila em segundos"""
    return (fluxo / (fluxo_sat - fluxo)) * (tempo_ciclo - tempo_verde_efetivo)


def calc_num_paradas(
    tempo_ciclo: segundos,
    tempo_verde_efetivo: segundos,
    fluxo: ucp_por_hora,
    fluxo_sat: ucp_por_hora,
) -> float:
    """Número de ucp que sofrem parada por ciclo"""
    return (fluxo * fluxo_sat) / (fluxo_sat - fluxo) * (tempo_ciclo - tempo_verde_efetivo) / 3600.0
