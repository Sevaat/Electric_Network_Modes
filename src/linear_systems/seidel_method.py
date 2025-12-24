from abc import ABC
from copy import deepcopy
from typing import List, Tuple

import numpy as np

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class SeidelMethod(ABC):
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
        node_s = SeidelMethod._get_node_s(nodes)
        for i, node in enumerate(nodes):
            if i != node_s:
                s = node.power
                if node.type_node != "LS":
                    s = -s
                b = s.conjugate() / parameters.nominal_voltage - conductivity_matrix[node_s, i] * nodes[
                    node_s].voltage
                matrix_b.append(b)
        return np.array(matrix_b)

    @staticmethod
    def _condition(matrix_u: List[complex], matrix_y: np.ndarray, matrix_b: np.ndarray, parameters: Parameters) -> bool:
        """Проверять на достижение точности расчета"""
        new_matrix_b = matrix_y.dot(matrix_u)
        for i in range(len(matrix_b)):
            if (new_matrix_b[i] - matrix_b[i]) > parameters.accuracy:
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
        node_s = SeidelMethod._get_node_s(nodes)

        # матрица проводимостей без столбца и строки базисного узла
        matrix_y = np.delete(np.delete(conductivity_matrix, node_s, axis=0), node_s, axis=1)
        # матрица свободных членов без базисного узла
        matrix_b = SeidelMethod._get_matrix_b(nodes, parameters, conductivity_matrix)
        # матрица начальных приближений напряжений
        matrix_u = [node.voltage for node in nodes if node.type_node != "S"]

        for iteration in range(parameters.iterations):
            for i in range(len(matrix_u)):
                k = 1 / matrix_y[i, i]
                u_i = 0
                for j in range(len(matrix_u)):
                    if j != i:
                        u_i -= matrix_y[i, j] * k * matrix_u[j]
                u_i += matrix_b[i] * k
                matrix_u[i] = u_i

            if SeidelMethod._condition(matrix_u, matrix_y, matrix_b, parameters):
                print(f"Точность достигнута! Расчет окончен на итерации №{iteration}!")
                break

        j = 0
        for i, node in enumerate(nodes):
            if i != node_s:
                node.voltage = matrix_u[j]
                j += 1

        for branch in branches:
            if branch.type_branch != "T3":
                branch.calculate_current_losses()
            else:
                branch.calculate_current_losses(nodes, conductivity_matrix)

        return nodes, branches