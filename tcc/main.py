import argparse
from pathlib import Path
from typing import Dict, List

from docplex.mp.utils import DOcplexException

from tcc.cruzamento import Cruzamento
from tcc.grafo import Grafo
from tcc.grupo_movimento import GrupoMovimento
from tcc.linear_programming.model import run_model_semaforo
from tcc.load_data import (
    ConexaoCruzamentos,
    ParesFluxos,
    load_csv_conexao,
    read_fluxos_from_file,
    read_grafos_incompatibilidade,
)


def setup_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TCC")

    parser.add_argument(
        "--linear-programming",
        dest="linear_programming",
        default=False,
        action="store_true",
        help="Run linear programming",
    )
    parser.add_argument(
        "--brute-force",
        dest="brute_force",
        default=False,
        action="store_true",
        help="Run brute force",
    )

    parser.add_argument(
        "--caso-entrada",
        dest="caso_entrada",
    )

    parser.add_argument(
        "--initial-sol",
        dest="initial_solution",
    )

    return parser.parse_args()


def main() -> None:
    args = setup_arguments()
    grafos: List[Grafo] = read_grafos_incompatibilidade(
        Path(f"entradas/{args.caso_entrada}/grafos_incompatibilidades/"), "*.txt"
    )
    grupos_movimento_cruzamento: List[List[GrupoMovimento]] = read_fluxos_from_file(
        Path(f"entradas/{args.caso_entrada}/fluxos/"), "*.csv"
    )
    cruzamentos: List[Cruzamento] = []
    conexao_cruzamentos: Dict[ConexaoCruzamentos, ParesFluxos] = load_csv_conexao(
        Path(f"entradas/{args.caso_entrada}/extras/conexao.csv")
    )

    print([value for (key, value) in conexao_cruzamentos.items() if key.cruzamento_inicial != 0])
    id = 0
    for grupo, grafo in zip(grupos_movimento_cruzamento, grafos):
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

    if args.linear_programming:
        try:
            for tempo_ciclo in range(66, 67, 70):
                print(f"tempo_ciclo = {tempo_ciclo} sec")
                if args.initial_solution:
                    model = run_model_semaforo(
                        cruzamentos=cruzamentos,
                        conexao_cruzamentos=conexao_cruzamentos,
                        tempo_ciclo=tempo_ciclo,
                        solucao_inicial=args.initial_solution,
                    )
                else:
                    model = run_model_semaforo(
                        cruzamentos=cruzamentos,
                        conexao_cruzamentos=conexao_cruzamentos,
                        tempo_ciclo=tempo_ciclo,
                    )

                print(f"veiculos que param por hora = {model.objective_value} veiculos\n")
        except DOcplexException as err:
            print(err)


if __name__ == "__main__":
    main()
