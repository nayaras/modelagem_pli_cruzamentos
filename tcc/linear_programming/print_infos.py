import json
from typing import List

from docplex.mp.dvar import Var

from tcc.calculos import (
    calc_atraso,
    calc_fila_max,
    calc_grau_sat,
    calc_num_paradas,
    calc_tempo_dissipacao,
)


def soma_atraso_por_cruzamento(
    inis: List[Var],
    fins: List[Var],
    tempo_ciclo: float,
    fluxo: List[float],
    fluxo_sat: List[float],
) -> float:
    soma: float = 0.0
    for i in range(len(inis)):
        tempo_verde = fins[i].solution_value - inis[i].solution_value
        grau_sat = calc_grau_sat(fluxo[i], fluxo_sat[i], tempo_verde, tempo_ciclo)
        soma += calc_atraso(tempo_ciclo, tempo_verde, grau_sat)
    return soma


def print_model(
    inis: List[Var],
    fins: List[Var],
    tempo_ciclo: float,
    fluxo: List[float],
    fluxo_sat: List[float],
) -> str:
    res = {}
    for i in range(len(inis)):
        tempo_verde = fins[i].solution_value - inis[i].solution_value
        grau_sat = calc_grau_sat(fluxo[i], fluxo_sat[i], tempo_verde, tempo_ciclo)
        ini_fim = {
            "inicio": round(inis[i].solution_value, 3),
            "final": round(fins[i].solution_value, 3),
            "tempo_verde": round(tempo_verde, 3),
            "grau_sat": round(grau_sat, 3),
            "tempo_ciclo": round(tempo_ciclo, 3),
            "atraso": round(calc_atraso(tempo_ciclo, tempo_verde, grau_sat), 3),
            "tempo_dissipacao": round(
                calc_tempo_dissipacao(tempo_ciclo, tempo_verde, fluxo[i], fluxo_sat[i]), 3
            ),
            "fila_max": round(calc_fila_max(tempo_ciclo, tempo_verde, fluxo[i]), 3),
            "num_paradas": round(
                calc_num_paradas(tempo_ciclo, tempo_verde, fluxo[i], fluxo_sat[i]), 3
            ),
        }
        res[f"grupo_mov {i}"] = ini_fim

    print(json.dumps(res, indent=2))

    return json.dumps(res, indent=2)
