import csv
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from tcc.grafo import Grafo
from tcc.grupo_movimento import GrupoMovimento


def load_grafo_incompatibilidade(path: Path) -> Grafo:
    logging.info("Carregando grafo de incompatilidade")
    arestas: List[Tuple[int, int]] = []
    vertices_isolados: List[int] = []

    # importando grafo de compatibilidades
    f = open(path, "r")
    fim_file = 0
    while fim_file == 0:
        for line in f:
            if len(list(map(int, line.split()))) == 1:
                u = list(map(int, line.split()))[0]
                print("u", u)
                vertices_isolados.append(u)
            else:
                u, v = map(int, line.split())
                arestas.append((u, v))
        else:
            fim_file = 1

        grafo = Grafo(arestas, vertices_isolados, direcionado=False)
    f.close()

    return grafo


def load_csv_fluxo(path: Path) -> List[GrupoMovimento]:
    logging.info("Carregando dados de fluxos")
    lista_semaforos: List[GrupoMovimento] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        # next(reader, None)  # skip header
        for row in reader:
            # inicializa semaforos com fluxo, fluxo sat e velocidade da via
            fluxo = float(row["fluxo_total"].replace(",", "."))
            fluxo_sat = float(row["fluxo_sat"].replace(",", "."))
            vel = int(row["vel_via"])
            labels = (row["semaforo_label_ini"], row["semaforo_label_fim"])
            lista_semaforos.append(
                GrupoMovimento(int(row["semaforo"]), fluxo, fluxo_sat, vel, labels)
            )

    return lista_semaforos


def read_files_from_folder(p: Path, ext: str) -> List[Path]:
    files = list(p.glob(ext))
    files.sort()
    return files


def read_grafos_incompatibilidade(p: Path, ext: str) -> List[Grafo]:
    files: List[Path] = read_files_from_folder(p, ext)
    grafos: List[Grafo] = []
    for file in files:
        grafos.append(load_grafo_incompatibilidade(file))
    return grafos


def read_fluxos_from_file(p: Path, ext: str) -> List[List[GrupoMovimento]]:
    files: List[Path] = read_files_from_folder(p, ext)
    fluxos: List[List[GrupoMovimento]] = []
    for file in files:
        fluxo = load_csv_fluxo(file)
        fluxos.append(fluxo)
    return fluxos


def read_distancia_vel_vias(p: Path) -> Tuple[int, int]:
    with open(p) as f:
        d, v = f.read().split(" ")

    return (int(d), int(v))


@dataclass
class ConexaoCruzamentos:
    cruzamento_inicial: int
    cruzamento_final: int

    def __hash__(self) -> int:
        return hash((self.cruzamento_inicial, self.cruzamento_final))

    def get_cruzamento_inicial(self) -> int:
        return self.cruzamento_inicial


grupo_mov_saida = int
grupo_mov_chegada = int
fracao_mov = float
desloc = float
ParesFluxos = List[Tuple[grupo_mov_saida, grupo_mov_chegada, fracao_mov, desloc]]


def load_csv_conexao(path: Path) -> Dict[ConexaoCruzamentos, ParesFluxos]:

    cruzamentos_conexao = defaultdict(list)
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            desloc = float(row["dist"]) / (float(row["vel"]) / 3.6)
            cruzamentos_conexao[
                ConexaoCruzamentos(
                    cruzamento_inicial=int(row["cruzamento_inicial"]),
                    cruzamento_final=int(row["cruzamento_final"]),
                )
            ].append(
                (
                    int(row["grupo_mov_saida"]),
                    int(row["grupo_mov_chegada"]),
                    float(row["fracao"]),
                    desloc,
                )
            )

    return cruzamentos_conexao
