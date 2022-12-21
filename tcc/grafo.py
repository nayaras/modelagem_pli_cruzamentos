# import dict
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


# classe para grafo e funções pertinentes
class Grafo(object):
    """Implementação básica de um grafo."""

    def __init__(
        self,
        arestas: List[Tuple[int, int]],
        vertices_isolados: List[int] = [],
        direcionado: bool = False,
    ) -> None:
        """Inicializa as estruturas base do grafo."""
        self.adj: Dict = defaultdict(set)
        self.direcionado = direcionado
        self.adiciona_arestas(arestas)
        self.adciona_vertice_isolado(vertices_isolados)

    def get_vertices(self) -> List[int]:
        """Retorna a lista de vértices do grafo."""
        return list(self.adj.keys())

    def get_arestas(self) -> List[Tuple[int, int]]:
        """Retorna a lista de arestas do grafo."""
        return [(k, v) for k in self.adj.keys() for v in self.adj[k]]

    def adiciona_arestas(self, arestas: List[Tuple[int, int]]) -> None:
        """Adiciona arestas ao grafo."""
        for u, v in arestas:
            self.adiciona_arco(u, v)

    def adiciona_arco(self, u: int, v: int) -> None:
        """Adiciona uma ligação (arco) entre os nodos 'u' e 'v'."""
        self.adj[u].add(v)
        # Se o grafo é não-direcionado, precisamos adicionar arcos nos dois sentidos.
        if not self.direcionado:
            self.adj[v].add(u)

    def adciona_vertice_isolado(self, list_vertices: List[int]) -> None:
        for u in list_vertices:
            self.adj[u] = {}

    def existe_aresta(self, u: int, v: int) -> bool:
        """Existe uma aresta entre os vértices 'u' e 'v'?"""
        return u in self.adj and v in self.adj[u]

    def qtd_vertices(self) -> int:
        return len(self.adj)

    def get_list_adj(self, v: int) -> List[int]:
        return list(self.adj[v])

    # Coloracao gulosa
    def get_num_colors_greedy_coloring(self) -> int:
        result: Dict = {}
        for u in range(self.qtd_vertices()):
            assigned = {result.get(i) for i in self.adj[u] if i in result}
            color = 0
            for c in assigned:
                if color != c:
                    break
                color = color + 1
            result[u] = color

        return int(max(value for key, value in result.items())) + 1

    def get_greedy_coloring(self) -> List[int]:
        result: Dict = {}
        for u in range(self.qtd_vertices()):
            assigned = {result.get(i) for i in self.adj[u] if i in result}
            color = 0
            for c in assigned:
                if color != c:
                    break
                color = color + 1
            result[u] = color

        return [res for res in result.keys()]

    # colapsa coloracao. Ex:
    # [0, 0, 0, 1, 1, 1, 2, 2, 2, 2] => {0: {0, 1, 2}, 1: {3, 4, 5}, 2: {8, 9, 6, 7}}

    def colapsa(self, coloracao: List[int]) -> Dict[int, Set[int]]:
        grafo_colapsado = defaultdict(set)
        # print(f"col::{coloracao} -- {self.qtd_vertices()}")
        for i in range(self.qtd_vertices()):

            grafo_colapsado[coloracao[i]].add(i)

        return grafo_colapsado

    def get_coloracoes(
        self,
        color: List[int],
        k: int,
        v: int,
        max_color: int,
        result: List[List[int]],
    ) -> Optional[List[List[int]]]:
        COLORS: List[int] = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]  # type: ignore # noqa: E501
        # if all colors are assigned, print the solution
        N = self.qtd_vertices()
        if v == N:
            coloracao_atual = [COLORS[color[v]] for v in range(N)]
            if _eh_particao_canonica(coloracao_atual) and _eh_minimal(self, coloracao_atual, N):
                result.append(coloracao_atual)
            return None

        # try all possible combinations of available colors
        for c in range(1, k + 1):
            # if it is safe to assign color c to vertex v
            if self._is_safe(color, v, c):
                # assign color c to vertex v
                color.insert(v, c)
                if c > max_color:
                    break
                else:
                    # recur for next vertex
                    self.get_coloracoes(color, k, v + 1, max_color, result)
                # backtrack
                color.insert(v, 0)

        return result

    # Function to check if it is safe to assign color c to vertex v
    def _is_safe(self, color: List[int], v: int, c: int) -> bool:

        # check color of every adjacent vertex of v
        for u in self.get_list_adj(v):
            if color[u] == c:
                return False

        return True

    def __len__(self) -> int:
        return len(self.adj)

    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, dict(self.adj))

    def __getitem__(self, v: int) -> List[int]:
        return self.adj[v]


def _eh_particao_canonica(part: List[int]) -> bool:
    usado = [False] * len(part)
    prim = []
    for c in part:
        if not usado[c]:
            usado[c] = True
            prim.append(c)
            if len(prim) == 1 and c != 0:
                return False
            if len(prim) >= 2 and prim[len(prim) - 2] != c - 1:
                return False
    return True


def _eh_minimal(G: Grafo, cor: List[int], N: int) -> bool:
    # acessa vertices dela
    for i in range(1, N):
        cor_adjacentes = []
        list_adj_vertice = G.get_list_adj(i)
        for h in list_adj_vertice:
            cor_adjacentes.append(cor[h])
        # print("vetice:cor", i, ":", cor[i], "list", list(zip(list_adj_vertice, cor_adjacentes)))
        if len(list_adj_vertice) > 1:

            for j in range(0, max(cor) + 1):
                if j not in cor_adjacentes and cor[i] != j:
                    # print('nao eh minimal, pois cor ', j, 'pode ser atribuida ao vertice',i)
                    return False
                # print('cor', j,'nao pode ser atribuida ao vertice', i)
                if j == max(cor) and i == N - 1:
                    # print('cor', j,'nao pode ser atribuida ao vertice', i)
                    # list_coloracao.append(cor)
                    # print('coloracao minimal', cor)
                    return True
    return False
