from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from tcc.grafo import Grafo
from tcc.grupo_movimento import GrupoMovimento

Coloracao = List[int]


class Cruzamento:
    grupos_movimento: List[GrupoMovimento]
    grafo_incompatibilidade: Grafo
    pares_vertices: List[Tuple[int, int, float, float]] = []
    vertices_saindo_cruzamento_atual: List[int] = []
    list_verdes: Dict[Tuple[int, ...], List[Tuple[int, ...]]] = defaultdict(list)
    id_prox_cruzamento: Optional[int] = None
    tempo_ciclo: float
    id: int

    def __init__(
        self,
        grupos_movimento: List[GrupoMovimento],
        grafo_incompatibilidade: Grafo,
        id: int,
        pares_vertices: List[List[Tuple[int, int, float, float]]] = [],
        vertices_saindo_cruzamento_atual: List[int] = [],
        id_prox_cruzamento: Optional[int] = None,
    ) -> None:
        self.grupos_movimento = grupos_movimento
        self.grafo_incompatibilidade = grafo_incompatibilidade
        self.id = id
        self.pares_vertices = pares_vertices[0] if pares_vertices else []
        self.vertices_saindo_cruzamento_atual = vertices_saindo_cruzamento_atual
        self.id_prox_cruzamento = id_prox_cruzamento

    def __eq__(self, value):
        return self.id == value

    def get_fluxos(self) -> List[float]:
        fluxos: List[float] = []
        for grupo_mov in self.grupos_movimento:
            fluxos.append(grupo_mov.fluxo)
        return fluxos

    def get_fluxos_saturacao(self) -> List[float]:
        fluxos_saturacao: List[float] = []
        for grupo_mov in self.grupos_movimento:
            fluxos_saturacao.append(grupo_mov.fluxo_saturacao)
        return fluxos_saturacao

    def get_tempos_amarelo(self) -> List[int]:
        amarelos: List[int] = []
        for grupo_mov in self.grupos_movimento:
            amarelos.append(grupo_mov.tempo_amarelo)
        return amarelos

    def get_num_grupos_movimento(self) -> int:
        return len(self.grupos_movimento)
