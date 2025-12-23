from abc import ABC
from copy import deepcopy
from typing import List, Tuple, Optional

import numpy as np

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class IterativeGaussianMethod(ABC):
    @staticmethod
    def _get_matrix_b(nodes: List[Node], conductivity_matrix: np.ndarray) -> np.ndarray:
        """Получить матрицу B из уравнения AX=B"""
        node_s = next(i for i, node in enumerate(nodes) if node.type_node  == "S")
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
            power: List[int | float | complex] = [0, 0, 0]
            real_power: List[int | float | complex] = [0, 0, 0]
            real_power[0] = full_power.real + conductivity_matrix[i, i].real * abs(nodes[i].voltage) ** 2
            imaginary_power: List[int | float | complex] = [0, 0, 0]
            imaginary_power[0] = full_power.imag - conductivity_matrix[i, i].imag * abs(nodes[i].voltage) ** 2
            for j in range(len(nodes)):
                if j != i:
                    real_power[1] += conductivity_matrix[i, j].real * nodes[j].voltage.real
                    real_power[1] -= conductivity_matrix[i, j].imag * nodes[j].voltage.imag
                    real_power[2] += conductivity_matrix[i, j].real * nodes[j].voltage.imag
                    real_power[2] += conductivity_matrix[i, j].imag * nodes[j].voltage.real
                    imaginary_power[1] += conductivity_matrix[i, j].real * nodes[j].voltage.real
                    imaginary_power[1] -= conductivity_matrix[i, j].imag * nodes[j].voltage.imag
                    imaginary_power[2] += conductivity_matrix[i, j].real * nodes[j].voltage.imag
                    imaginary_power[2] += conductivity_matrix[i, j].imag * nodes[j].voltage.real
            real_power[1] = nodes[i].voltage.real * real_power[1]
            real_power[2] = nodes[i].voltage.imag * real_power[2]
            imaginary_power[1] = nodes[i].voltage.imag * imaginary_power[1]
            imaginary_power[2] = -nodes[i].voltage.real * imaginary_power[2]
            power_imbalance.append(complex(sum(real_power), sum(imaginary_power)))
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
                branch.power_losses = 3 * branch.current ** 2 * branch.impedance
            elif isinstance(branch, Transformer2) and isinstance(branch.current, complex):
                branch.power_losses = 3 * (branch.current ** 2 * branch.impedance + branch.high.voltage ** 2 * branch.conductivity)
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
            branches = IterativeGaussianMethod._currents(nodes, branches, conductivity_matrix)
            branches = IterativeGaussianMethod._power_losses(branches)
            # проверка по условию выхода
            power_imbalance = IterativeGaussianMethod._get_power_imbalance(nodes, conductivity_matrix)
            if IterativeGaussianMethod._condition(nodes, parameters, power_imbalance):
                print(f"Точность достигнута! Расчет окончен на итерации №{iteration}!")
                break
            matrix_b = deepcopy(new_matrix_b)
        return nodes, branches