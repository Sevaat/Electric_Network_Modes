from abc import ABC
from copy import deepcopy
from typing import List, Optional, Tuple

import numpy as np

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class IterativeGaussianMethod(ABC):
    @staticmethod
    def _get_matrix_b(nodes: List[Node], conductivity_matrix: np.ndarray) -> np.ndarray:
        """Получить матрицу B из уравнения AX=B"""
        node_s = next(i for i, node in enumerate(nodes) if node.type_node == "S")
        matrix_b = []
        for i, node in enumerate(nodes):
            if node.type_node != "S":
                s = node.power
                if node.type_node != "LS":
                    s = -s
                b = s.conjugate() / node.voltage.conjugate() - conductivity_matrix[node_s, i] * nodes[node_s].voltage
                matrix_b.append(b)
        return np.array(matrix_b)

    @staticmethod
    def _get_power_imbalance(nodes: List[Node], conductivity_matrix: np.ndarray) -> List[complex]:
        """Получить небалансы мощности в узлах"""
        power_imbalance: List[complex] = []
        for i in range(len(nodes)):
            full_power: Optional[complex] = None
            if nodes[i].type_node == "S":
                full_power = complex(0, 0)
            elif nodes[i].type_node == "LS":
                full_power = -nodes[i].power
            else:
                full_power = nodes[i].power
            # S_i_imb_0=S+Y_ii.conjugate*U_i^2
            s_imb: List[int | float | complex] = [0, 0, 0]
            s_imb[0] = full_power + conductivity_matrix[i, i].conjugate() * abs(nodes[i].voltage) ** 2
            # S_i_imb_1=SUM[(Y_ij.real*U_j.real-Y_ij.imag*U_j.imag)+j*(Y_ij.real*U_j.real-Y_ij.imag*U_j.imag)]
            # S_i_imb_2=SUM[(Y_ij.real*U_j.imag+Y_ij.imag*U_j.real)+j*(Y_ij.real*U_j.imag+Y_ij.imag*U_j.real)]
            for j in range(len(nodes)):
                if j != i:
                    s_imb[1] += complex(
                        (
                            conductivity_matrix[i, j].real * nodes[j].voltage.real
                            - conductivity_matrix[i, j].imag * nodes[j].voltage.imag
                        ),
                        (
                            conductivity_matrix[i, j].real * nodes[j].voltage.real
                            - conductivity_matrix[i, j].imag * nodes[j].voltage.imag
                        ),
                    )
                    s_imb[2] += complex(
                        (
                            conductivity_matrix[i, j].real * nodes[j].voltage.imag
                            + conductivity_matrix[i, j].imag * nodes[j].voltage.real
                        ),
                        (
                            conductivity_matrix[i, j].real * nodes[j].voltage.imag
                            + conductivity_matrix[i, j].imag * nodes[j].voltage.real
                        ),
                    )
            # S_i_imb_1=U_i.real*S_i_imb_1.real+j*U_i.imag*S_i_imb_1.imag
            # S_i_imb_2=U_i.imag*S_i_imb_2.real-j*U_i.real*S_i_imb_2.imag
            s_imb[1] = complex(nodes[i].voltage.real * s_imb[1].real, nodes[i].voltage.imag * s_imb[1].imag)
            s_imb[2] = complex(
                nodes[i].voltage.imag * s_imb[2].real, nodes[i].voltage.real * s_imb[2].imag
            ).conjugate()
            power_imbalance.append(sum(s_imb))
        return power_imbalance

    @staticmethod
    def _condition(nodes: List[Node], parameters: Parameters, power_imbalance: List[complex]) -> bool:
        """Проверять на достижение точности расчета"""
        for i, p_imb in enumerate(power_imbalance):
            if nodes[i].type_node != "S":
                if abs(p_imb.real) > parameters.accuracy and abs(p_imb.imag) > parameters.accuracy:
                    return False
        return True

    @staticmethod
    def run(
        nodes: List[Node], branches: List[Line | Transformer2 | Transformer3], parameters: Parameters
    ) -> Tuple[List[Node], List[Line | Transformer2 | Transformer3]]:
        """
        Произвести расчет установившегося режима методом простой итерации
        :param nodes: список узлов
        :param branches: список ветвей
        :param parameters: список параметров расчета
        :return: список узлов и ветвей
        """
        conductivity_matrix = get_conductivity_matrix(nodes, branches)
        # матрица проводимостей без столбца и строки базисного узла
        node_s = next(i for i, node in enumerate(nodes) if node.type_node == "S")
        matrix_a = np.delete(np.delete(conductivity_matrix, node_s, axis=0), node_s, axis=1)

        for iteration in range(parameters.iterations):
            # матрица свободных членов без базисного узла на текущей итерации
            matrix_b = IterativeGaussianMethod._get_matrix_b(nodes, conductivity_matrix)
            # расчет новых напряжений
            matrix_u = np.linalg.solve(matrix_a, matrix_b)
            # занесение новых напряжений в данные узлов
            j = 0
            for i, node in enumerate(nodes):
                if i != node_s:
                    node.voltage = matrix_u[j]
                    j += 1
            # расчет новых свободных членов
            new_matrix_b = IterativeGaussianMethod._get_matrix_b(nodes, conductivity_matrix)
            for branch in branches:
                if branch.type_branch != "T3":
                    branch.calculate_current_losses()
                else:
                    branch.calculate_current_losses(nodes, conductivity_matrix)
            # проверка по условию выхода
            power_imbalance = IterativeGaussianMethod._get_power_imbalance(nodes, conductivity_matrix)
            if IterativeGaussianMethod._condition(nodes, parameters, power_imbalance):
                print(f"Точность достигнута! Расчет окончен на итерации №{iteration}!")
                break
            matrix_b = deepcopy(new_matrix_b)
        return nodes, branches
