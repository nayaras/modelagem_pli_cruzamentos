from tcc.grafo import Grafo


def test_get_vertices() -> None:
    arestas = [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]
    g = Grafo(arestas=arestas, vertices_isolados=[])
    assert g.get_vertices() == [0, 1, 2]


def test_get_arestas() -> None:
    arestas = [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]
    g = Grafo(arestas=arestas, vertices_isolados=[])
    assert g.get_arestas() == [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]


def test_adiciona_arestas() -> None:
    arestas = [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]
    g = Grafo(arestas=arestas, vertices_isolados=[])
    g.adiciona_arestas([(0, 3), (3, 0)])
    assert g.get_arestas() == [(0, 1), (0, 2), (0, 3), (1, 0), (1, 2), (2, 0), (2, 1), (3, 0)]


def test_adiciona_arco() -> None:
    g = Grafo(arestas=[], vertices_isolados=[])
    g.adiciona_arco(0, 1)
    assert g.get_arestas() == [(0, 1), (1, 0)]


def test_adiciona_vertice_isolado() -> None:
    g = Grafo(arestas=[], vertices_isolados=[0, 1])
    assert g.get_arestas() == []
    assert g.get_vertices() == [0, 1]


def test_existe_aresta() -> None:
    arestas = [(0, 1), (0, 2), (1, 2)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.existe_aresta(0, 1) is True
    assert g.existe_aresta(1, 0) is True
    assert g.existe_aresta(0, 3) is False


def test_qtd_vertices() -> None:
    arestas = [(0, 1), (0, 2), (1, 2)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.qtd_vertices() == 3


def test_get_list_adj() -> None:
    arestas = [(0, 1), (0, 2), (1, 2)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.get_list_adj(0) == [1, 2]


def test_get_coloracoes() -> None:
    arestas = [(0, 1), (0, 3), (1, 0), (1, 2), (2, 1), (2, 3), (3, 0)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    # set max colors 4
    coloracoes_minimais = g.get_coloracoes([-1, -1, -1, -1], g.qtd_vertices() - 1, 0, 4, [])
    assert len(coloracoes_minimais) == 1
    assert [0, 1, 0, 1] in coloracoes_minimais


def test_colapsa() -> None:
    arestas = [(0, 1), (0, 3), (1, 0), (1, 2), (2, 1), (2, 3), (3, 0)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    # set max colors 4
    coloracoes_minimais = g.get_coloracoes([-1, -1, -1, -1], g.qtd_vertices() - 1, 0, 4, [])
    for cor in coloracoes_minimais:
        assert g.colapsa(cor) == {0: {0, 2}, 1: {1, 3}}


def test_get_num_colors_greedy_coloring() -> None:
    arestas = [(0, 1), (0, 3), (1, 0), (1, 2), (2, 1), (2, 3), (3, 0)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.get_num_colors_greedy_coloring() == 2


def test_get_num_colors_greedy_coloring_only_two_colors() -> None:
    arestas = [(0, 1), (1, 0)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.get_num_colors_greedy_coloring() == 2


def test_get_greedy_coloring_only_two_colors() -> None:
    arestas = [(0, 1), (1, 0)]
    g = Grafo(arestas=arestas, vertices_isolados=[], direcionado=False)
    assert g.get_greedy_coloring() == [0, 1]
