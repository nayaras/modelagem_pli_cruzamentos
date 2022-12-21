from typing import Tuple


class GrupoMovimento:
    id: int
    labels: Tuple[str, str]
    tempo_amarelo: int
    tempo_verde: int
    tempo_vermelho: int
    fluxo: float = 0.0
    fluxo_saturacao: float = 0.0
    tempo_verde_min: int = 10
    tempo_verde_max: int = 0
    tempo_verde_efetivo: int = 0
    capacidade: float = 0.0
    grau_saturacao: float = 0.0
    taxa_ocupacao: float = 0.0
    tempo_dissipacao: float = 0.0
    numero_paradas: float = 0.0
    fila_max: float = 0.0
    atraso: float = 0.0
    inicio_verde: float = 0
    velocidade_via: int = 0
    fracao_verde: float = 0.0
    distancia: float = 0.0

    def __init__(
        self,
        id: int,
        fluxo: float,
        fluxo_saturacao: float,
        velocidade_via: int,
        labels: Tuple[str, str],
    ) -> None:
        self.id = id
        self.tempo_verde = 10
        self.tempo_verde_efetivo = self.tempo_verde - 2
        self.tempo_ciclo_max = 120
        self.tempo_verde_min = 10
        self.fluxo = fluxo
        self.fluxo_saturacao = fluxo_saturacao
        if velocidade_via <= 40:
            self.tempo_amarelo = 3
        elif velocidade_via >= 50 and velocidade_via <= 60:
            self.tempo_amarelo = 4
        elif velocidade_via >= 70:
            self.tempo_amarelo = 5
        self.labels = labels
