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
    def _currents(nodes: List[Node], branches: List[Line | Transformer2 | Transformer3],
                  conductivity_matrix: np.ndarray) -> List[Line | Transformer2 | Transformer3]:
        """Рассчитывать комплексные токи в ветвях"""
        for branch in branches:
            if isinstance(branch, Line):
                branch.current = (branch.start.voltage - branch.end.voltage) / branch.impedance
            elif isinstance(branch, Transformer2):
                branch.current = (branch.high.voltage - branch.low.voltage) / branch.impedance
            elif isinstance(branch, Transformer3):
                h = nodes.index(branch.high)
                m = nodes.index(branch.middle)
                l = nodes.index(branch.low)
                i_hm = (branch.high.voltage - branch.middle.voltage) * conductivity_matrix[h, m]
                i_hl = (branch.high.voltage - branch.low.voltage) * conductivity_matrix[h, l]
                i_ml = (branch.middle.voltage - branch.low.voltage) * conductivity_matrix[m, l]
                i_h = i_hm + i_hl
                i_m = i_hm - i_ml
                i_l = i_hl + i_ml
                if isinstance(i_h, complex) and isinstance(i_m, complex) and isinstance(i_l, complex):
                    branch.high_current = i_h
                    branch.middle_current = i_m
                    branch.low_current = i_l
            else:
                raise TypeError
        return branches

    @staticmethod
    def _power_losses(branches: List[Line | Transformer2 | Transformer3]) -> List[Line | Transformer2 | Transformer3]:
        """Рассчитывать потери мощности в элементах сети"""
        for branch in branches:
            if isinstance(branch, Line) and isinstance(branch.current, complex):
                branch.power_losses = branch.current ** 2 * branch.impedance
            elif isinstance(branch, Transformer2) and isinstance(branch.current, complex):
                branch.power_losses = branch.current ** 2 * branch.impedance + branch.high.voltage ** 2 * branch.conductivity
            elif (
                    isinstance(branch, Transformer3)
                    and isinstance(branch.high_current, complex)
                    and isinstance(branch.middle_current, complex)
                    and isinstance(branch.low_current, complex)
            ):
                s_h = branch.high.voltage * branch.high_current.conjugate() + branch.high.voltage ** 2 * branch.high_conductivity
                s_m = branch.middle.voltage * (-branch.middle_current).conjugate()
                s_l = branch.low.voltage * (-branch.low_current).conjugate()
                ds = s_h + s_m + s_l
                branch.power_losses = ds
            else:
                raise TypeError
        return branches

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

        branches = SeidelMethod._currents(nodes, branches, conductivity_matrix)
        branches = SeidelMethod._power_losses(branches)
        return nodes, branches