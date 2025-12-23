from abc import ABC
from typing import List, Tuple

import numpy as np

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class MatrixMethod(ABC):

    @staticmethod
    def _get_node_s(nodes: List[Node]) -> int:
        """
        Получить номер узла-источника (S)
        :param nodes: список узлов
        :return: номер узла-источника (S)
        """
        node_s = 0
        for i in range(len(nodes)):
            if nodes[i].type_node == "S":
                node_s = i
                break
        return node_s

    @staticmethod
    def _get_matrix_b(nodes: List[Node], parameters: Parameters, conductivity_matrix: np.ndarray) -> np.ndarray:
        """
        Получить матрицу B из уравнения AX=B
        :param nodes: список узлов
        :param parameters: список параметров расчета
        :param conductivity_matrix: матрица собственных и взаимных проводимостей
        :return: матрица B из уравнения AX=B
        """
        matrix_b = []
        node_s = MatrixMethod._get_node_s(nodes)
        for i, node in enumerate(nodes):
            if i != node_s:
                s = node.power
                if node.type_node != "LS":
                    s = -s
                b = s.conjugate()/parameters.nominal_voltage - conductivity_matrix[node_s, i] * nodes[node_s].voltage
                matrix_b.append(b)
        return np.array(matrix_b)

    @staticmethod
    def _currents(nodes: List[Node], branches: List[Line | Transformer2 | Transformer3],
                  conductivity_matrix: np.ndarray) -> List[Line | Transformer2 | Transformer3]:
        """
        Расчет комплексных токов в ветвях
        :param nodes: список узлов
        :param branches: список ветвей
        :param conductivity_matrix: матрица собственных и взаимных проводимостей
        :return: список ветвей
        """
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
        """
        Расчет потерь мощности в элементах сети
        :param branches: список ветвей
        :return: список ветвей
        """
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
        Произвести расчет установившегося режима матричным методом
        :param nodes: список узлов
        :param branches: список ветвей
        :param parameters: список параметров расчета
        :return: список узлов и ветвей
        """
        conductivity_matrix = get_conductivity_matrix(nodes, branches)

        node_s = MatrixMethod._get_node_s(nodes)
        matrix_a = np.delete(np.delete(conductivity_matrix, node_s, axis=0), node_s, axis=1)

        matrix_b = MatrixMethod._get_matrix_b(nodes, parameters, conductivity_matrix)

        matrix_x = np.linalg.inv(matrix_a).dot(matrix_b)

        j = 0
        for i, node in enumerate(nodes):
            if i != node_s:
                node.voltage = matrix_x[j]
                j += 1

        branches = MatrixMethod._currents(nodes, branches, conductivity_matrix)
        branches = MatrixMethod._power_losses(branches)
        return nodes, branches