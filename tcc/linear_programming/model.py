# first import the Model class from docplex.mp
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from docplex.mp.constants import WriteLevel
from docplex.mp.dvar import Var
from docplex.mp.model import Model

from tcc.calculos import calc_num_paradas, calc_tempo_fluxo_pelotao
from tcc.cruzamento import Cruzamento
from tcc.grafo import Grafo
from tcc.linear_programming.print_infos import print_model, soma_atraso_por_cruzamento
from tcc.load_data import ConexaoCruzamentos, ParesFluxos

M = 4800  # constante de folga
CruzamentoId = int  # alias for int


def create_var_and_restricoes_por_cruzamento(
    model: Model,
    grafo_incomp: Grafo,
    tempo_ciclo: int,
    fluxos: List[float],
    fluxos_sat: List[float],
    tempos_amarelo: List[int],
    cruzamento_id: int,
) -> Tuple[Var, Var]:
    # variaveis de tempo de inicio e fim de verde
    fim = model.continuous_var_dict((len(grafo_incomp.get_vertices())), name=f"f{cruzamento_id}")
    ini = model.continuous_var_dict((len(grafo_incomp.get_vertices())), name=f"i{cruzamento_id}")

    vm_geral = 2  # vermelho geral

    # restrições para os inicios e fins de verde
    for i in range(len(grafo_incomp.get_vertices())):
        model.add(ini[i] >= 0)
        model.add(fim[i] >= 0)
        # model.add(ini[i] <= fim[i])

        model.add(
            fim[i] <= (tempo_ciclo - (tempos_amarelo[i] + vm_geral))
        )  # + fim <= tempo_ciclo - (amar + vm_g)

    # add restricao grau_sat < 1
    for i in range(len(fluxos)):
        model.add(fluxos_sat[i] * (fim[i] - ini[i]) >= fluxos[i] * tempo_ciclo)

    # restricoes incompatibilidade
    for (i, j) in grafo_incomp.get_arestas():
        nq = model.binary_var(f"nq{cruzamento_id}_{i}_{j}")
        model.add(fim[i] <= (ini[j] - (tempos_amarelo[i] + vm_geral)) + M * nq)
        model.add(
            fim[j] <= (ini[i] - (tempos_amarelo[i] + vm_geral)) + M * (1 - nq)
        )  # ini - (amar + vm_g) + MQ

    return (ini, fim)


def get_max(model: Model, ini_entrada: Var, ini_saida: Var, label: str) -> Var:
    ini_max = model.continuous_var(lb=0.0, name=label)
    model.add(ini_max >= ini_entrada)
    model.add(ini_max >= ini_saida)
    b1 = model.binary_var(f"b1_{label}")
    model.add(ini_max <= ((1 - b1) * M + ini_entrada))
    model.add(ini_max <= (b1 * M + ini_saida))
    return ini_max


def get_min(model: Model, fim_entrada: Var, fim_saida: Var, label: str) -> Var:
    fim_min = model.continuous_var(lb=0.0, name=label)
    model.add(fim_min <= fim_entrada)
    model.add(fim_min <= fim_saida)
    b2 = model.binary_var(f"b2_{label}")
    model.add(fim_min >= (-(1 - b2) * M + fim_entrada))
    model.add(fim_min >= (-b2 * M + fim_saida))
    return fim_min


def get_tam_fila(
    model: Model,
    tempo_ciclo: int,
    ini_verde: Var,
    fim_verde: Var,
    fluxo_chegada: float,
) -> float:
    return (tempo_ciclo - (fim_verde - ini_verde)) * fluxo_chegada


def get_quase_tempo_pelotao(tam_fila: float, capacidade_via: float) -> float:
    return tam_fila * 1 / capacidade_via


def calc_primeira_parte_num_paradas(
    fluxos: List[float], fluxos_sat: List[float], exclude_vertices: Optional[Set[int]] = None
) -> List[float]:
    # calcula (F x FS)/(FS - F)
    calc = [((fluxos[i] * fluxos_sat[i]) / (fluxos_sat[i] - fluxos[i])) for i in range(len(fluxos))]
    if exclude_vertices:
        return [calc[i] for i in range(len(calc)) if i not in exclude_vertices]
    return calc


def calc_sum_numero_paradas(
    cruzamento: Cruzamento,
    vertices_chegada: Dict[CruzamentoId, Set[int]],
    fluxo: List[float],
    fluxo_sat: List[float],
    ini: List[Var],
    fim: List[Var],
    model: Model,
    tempo_ciclo: int,
) -> float:
    np: float = 0.0
    vertices: Set[int] = set()
    if vertices_chegada.get(cruzamento.id) is not None:
        vertices = vertices_chegada[cruzamento.id]
    for i in range(len(fluxo)):
        if i not in vertices:
            np += calc_num_paradas(tempo_ciclo, (fim[i] - ini[i]), fluxo[i], fluxo_sat[i])
    return np


def get_tamanho_intersecao(model, ini_1, fim_1, ini_2, fim_2, saida, chegada, nome) -> float:
    # max de quem tá saindo de um semaforo + seu tempo de deslocamento
    # e quem ta chegando no outro cruz
    ini_max = get_max(
        model,
        ini_1,
        ini_2,
        f"ini_max_{nome}_{saida}_{chegada}",
    )

    fim_min = get_min(
        model,
        fim_1,
        fim_2,
        f"fim_min_{nome}_{saida}_{chegada}",
    )

    # fim min tem q ser menor q ini_max
    return get_max(model, 0, fim_min - ini_max, f"tv_sinc_{nome}_{saida}_{chegada}")


def run_model_semaforo(
    cruzamentos: List[Cruzamento],
    conexao_cruzamentos: Dict[ConexaoCruzamentos, ParesFluxos],
    tempo_ciclo: int,
    solucao_inicial: Optional[Dict[str, Any]] = None,
    print_detalhes: bool = True,
) -> Model:
    # create one model instance, with a name
    model: Model = Model(name="semaforo")
    model.parameters.timelimit = 120

    # variaveis indexadas pelo cruzamento
    tempos_amarelo: Dict[CruzamentoId, List[int]] = defaultdict(list)
    fluxos: Dict[CruzamentoId, List[float]] = defaultdict(list)
    fluxos_sat: Dict[CruzamentoId, List[float]] = defaultdict(list)
    fim: Dict[CruzamentoId, Var] = defaultdict(list)
    ini: Dict[CruzamentoId, Var] = defaultdict(list)
    vertices_chegada: Dict[CruzamentoId, Set[int]] = defaultdict(set)
    np_fluxo_comum: Dict[CruzamentoId, float] = defaultdict(float)

    # cria as variaveis ini e fim para cada grupo de movimento
    for cruzamento in cruzamentos:
        tempos_amarelo[cruzamento.id] = cruzamento.get_tempos_amarelo()
        fluxos[cruzamento.id] = cruzamento.get_fluxos()
        fluxos_sat[cruzamento.id] = cruzamento.get_fluxos_saturacao()
        (ini[cruzamento.id], fim[cruzamento.id]) = create_var_and_restricoes_por_cruzamento(
            model=model,
            grafo_incomp=cruzamento.grafo_incompatibilidade,
            tempo_ciclo=tempo_ciclo,
            fluxos=cruzamento.get_fluxos(),
            fluxos_sat=cruzamento.get_fluxos_saturacao(),
            tempos_amarelo=tempos_amarelo[cruzamento.id],
            cruzamento_id=cruzamento.id,
        )

    # listas dos numeros de paradas do fluxo comum (que segue direto)
    # e fluxo pelotão (galera que ta chegando quando semaforo ta aberto)
    list_np_pel = defaultdict(list)
    list_np_pos_pel = defaultdict(list)

    for cruzamento in cruzamentos:
        # print(f"Cruzamento {cruzamento.id}")

        # somente cruzamentos que possuem saida de fluxo
        # para outros cruzamentos possuem pares de vértices
        for (saida, chegada, fracao, desloc) in cruzamento.pares_vertices:
            print(f"desloc:: {desloc}")
            # (vertice de saida do cruzamento atual,
            # vertice de chegada no proximo cruzamento,
            # fracao do fluxo que vai de um cruzamento para outro [default = 1])
            delta = model.integer_var(
                name=f"delta_{cruzamento.id}_{cruzamento.id_prox_cruzamento}_{saida}_{chegada}"
            )
            if cruzamento.id_prox_cruzamento is not None:

                # tempo para dissipar pelotao
                tempo_pelotao = calc_tempo_fluxo_pelotao(
                    fluxos[cruzamento.id][saida],
                    fluxos_sat[cruzamento.id][saida],
                    tempo_ciclo,
                    ini[cruzamento.id][saida],
                    fim[cruzamento.id][saida],
                )
                print(f"tempo_pel::{tempo_pelotao}")
                tv_sincronizado_pelotao = get_tamanho_intersecao(
                    model,
                    ini_1=ini[cruzamento.id][saida] + desloc - delta,
                    fim_1=ini[cruzamento.id][saida] + desloc + tempo_pelotao - delta,
                    ini_2=ini[cruzamento.id_prox_cruzamento][chegada],
                    fim_2=fim[cruzamento.id_prox_cruzamento][chegada],
                    saida=saida,
                    chegada=chegada,
                    nome=f"{cruzamento.id}_pel",
                )

                # tempo_verde_pos_pel
                tv_sincronizado_pos_pelotao = get_tamanho_intersecao(
                    model,
                    ini_1=ini[cruzamento.id][saida] + desloc + tempo_pelotao - delta,
                    fim_1=fim[cruzamento.id][saida] + desloc - delta,
                    ini_2=ini[cruzamento.id_prox_cruzamento][chegada],
                    fim_2=fim[cruzamento.id_prox_cruzamento][chegada],
                    saida=saida,
                    chegada=chegada,
                    nome=f"{cruzamento.id}_pos_pel",
                )

                # quantidade de carros no pelotao que não conseguiram atravessar no verde do pelotao
                qtd_veiculos_nao_atravessaram_verde_pel = get_max(
                    model,
                    0,
                    (
                        (tempo_pelotao - tv_sincronizado_pelotao)
                        * (fluxos_sat[cruzamento.id][saida] / 3600)
                    ),
                    f"qtd_veiculos_nao_atravessaram_verde_{cruzamento.id}_pel_{saida}_{chegada}",
                )

                # qtd de veiculos que nao atravessam o verde sincronizado
                tempo_nao_pelotao = (
                    fim[cruzamento.id][saida] - ini[cruzamento.id][saida]
                ) - tempo_pelotao

                qtd_veiculos_nao_atravessaram_verde_nao_pel = get_max(
                    model,
                    0,
                    (
                        (tempo_nao_pelotao - tv_sincronizado_pos_pelotao)
                        * (fluxos[cruzamento.id][saida] / 3600)
                    ),
                    f"qtd_veiculos_nao_atravessam_verde_{cruzamento.id}_pos_pel_{saida}_{chegada}",
                )

                list_np_pel[cruzamento.id].append(qtd_veiculos_nao_atravessaram_verde_pel)
                list_np_pos_pel[cruzamento.id].append(qtd_veiculos_nao_atravessaram_verde_nao_pel)

                vertices_chegada[cruzamento.id_prox_cruzamento].add(chegada)

        np_fluxo_comum[cruzamento.id] = calc_sum_numero_paradas(
            cruzamento,
            vertices_chegada,
            fluxos[cruzamento.id],
            fluxos_sat[cruzamento.id],
            ini[cruzamento.id],
            fim[cruzamento.id],
            model,
            tempo_ciclo,
        )
        # fim for cruzamentos

    sum_n_paradas_fluxo_comum: float = 0.0
    sum_n_paradas_fluxo_pel: float = 0.0
    sum_n_paradas_fluxo_pos_pel: float = 0.0
    for cruzamento in cruzamentos:
        sum_n_paradas_fluxo_comum += np_fluxo_comum[cruzamento.id]
        sum_n_paradas_fluxo_pel += sum(list_np_pel[cruzamento.id])
        sum_n_paradas_fluxo_pos_pel += sum(list_np_pos_pel[cruzamento.id])

        sum_n_paradas_fluxo_comum_hora = sum_n_paradas_fluxo_comum / tempo_ciclo * 3600
        sum_n_paradas_fluxo_pel_hora = sum_n_paradas_fluxo_pel / tempo_ciclo * 3600
        sum_n_paradas_fluxo_pos_pel_hora = sum_n_paradas_fluxo_pos_pel / tempo_ciclo * 3600

    model.minimize(
        sum_n_paradas_fluxo_comum_hora
        + sum_n_paradas_fluxo_pel_hora
        + sum_n_paradas_fluxo_pos_pel_hora
    )

    if solucao_inicial:
        warmstart = model.new_solution()
        for i in range(len(cruzamentos)):
            warmstart.add_var_value(ini[i][0], solucao_inicial[f"grupo_mov {i}"]["inicio"])
            warmstart.add_var_value(fim[i][0], solucao_inicial[f"grupo_mov {i}"]["final"])

        model.add_mip_start(warmstart, write_level=WriteLevel.AllVars, complete_vars=True)

    model.solve()
    print(model.get_solve_status())

    sum_atraso: float = 0.0
    for cruzamento in cruzamentos:
        sum_atraso += soma_atraso_por_cruzamento(
            ini[cruzamento.id],
            fim[cruzamento.id],
            tempo_ciclo,
            fluxos[cruzamento.id],
            fluxos_sat[cruzamento.id],
        )

    print(f"soma atraso por hora = {round(sum_atraso/tempo_ciclo*3600,3)} sec de atraso por hora")
    if print_detalhes:
        model.print_solution()
        model.get_solve_details()

        for cruzamento in cruzamentos:
            print(f"Dados do cruzamento {cruzamento.id}:")
            print_model(
                ini[cruzamento.id],
                fim[cruzamento.id],
                tempo_ciclo,
                fluxos[cruzamento.id],
                fluxos_sat[cruzamento.id],
            )

    return model
