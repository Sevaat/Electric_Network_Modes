from abc import ABC
from typing import List, Tuple

import numpy as np

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class GaussMethod(ABC):

    @staticmethod
    def _get_node_s(nodes: List[Node]) -> int:
        """Получить номер узла-источника (S)"""
        node_s = 0
        for i in range(len(nodes)):
            if nodes[i].type_node == "S":
                node_s = i
                break
        return node_s

    @staticmethod
    def _get_matrix_b(nodes: List[Node], parameters: Parameters, conductivity_matrix: np.ndarray) -> np.ndarray:
        """Получить матрицу B из уравнения AX=B"""
        matrix_b = []
        node_s = GaussMethod._get_node_s(nodes)
        for i, node in enumerate(nodes):
            if i != node_s:
                s = node.power
                if node.type_node != "LS":
                    s = -s
                b = s.conjugate() / parameters.nominal_voltage - conductivity_matrix[node_s, i] * nodes[node_s].voltage
                matrix_b.append(b)
        return np.array(matrix_b)

    @staticmethod
    def run(
        nodes: List[Node], branches: List[Line | Transformer2 | Transformer3], parameters: Parameters
    ) -> Tuple[List[Node], List[Line | Transformer2 | Transformer3]]:
        """
        Произвести расчет установившегося режима методом Гаусса
        :param nodes: список узлов
        :param branches: список ветвей
        :param parameters: список параметров расчета
        :return: список узлов и ветвей
        """
        conductivity_matrix = get_conductivity_matrix(nodes, branches)

        node_s = GaussMethod._get_node_s(nodes)
        matrix_a = np.delete(np.delete(conductivity_matrix, node_s, axis=0), node_s, axis=1)

        matrix_b = GaussMethod._get_matrix_b(nodes, parameters, conductivity_matrix)

        matrix_x = np.linalg.solve(matrix_a, matrix_b)

        j = 0
        for i, node in enumerate(nodes):
            if i != node_s:
                node.voltage = matrix_x[j]
                j += 1

        for branch in branches:
            if branch.type_branch != "T3":
                branch.calculate_current_losses()
            else:
                branch.calculate_current_losses(nodes, conductivity_matrix)

        return nodes, branches
