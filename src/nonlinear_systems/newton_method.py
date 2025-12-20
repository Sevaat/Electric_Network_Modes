from abc import ABC
from typing import List, Optional, Tuple

import numpy

from src.models.branch import Line, Transformer2, Transformer3
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node
from src.models.parameters import Parameters


class NewtonMethod(ABC):

    @staticmethod
    def _get_power_imbalance(nodes: List[Node], conductivity_matrix: numpy.ndarray) -> List[complex]:
        """Получить небалансы мощности в узлах"""
        node_count = len(nodes)
        power_imbalance: List[complex] = []
        for i in range(node_count):
            full_power: Optional[complex] = None
            if nodes[i].type_node == "S":
                full_power = complex(0, 0)
            elif nodes[i].type_node == "LS":
                full_power = -nodes[i].power
            else:
                full_power = nodes[i].power
            real_power: List[int | float | complex] = [0, 0, 0]
            real_power[0] = full_power.real + conductivity_matrix[i, i].real * abs(nodes[i].voltage) ** 2
            imaginary_power: List[int | float | complex] = [0, 0, 0]
            imaginary_power[0] = full_power.imag - conductivity_matrix[i, i].imag * abs(nodes[i].voltage) ** 2
            for j in range(node_count):
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
    def _unbalance_condition(nodes: List[Node], parameters: Parameters, power_imbalance: List[complex]) -> bool:
        """Проверка, что все небалансы меньше заданной точности"""
        for i, p_imb in enumerate(power_imbalance):
            if nodes[i].type_node != "S":
                if abs(p_imb.real) > parameters.accuracy and abs(p_imb.imag) > parameters.accuracy:
                    return False
        return True

    @staticmethod
    def _get_dpi_du(nodes: List[Node], i: int, j: int, conductivity_matrix: numpy.ndarray) -> Tuple[float, float]:
        """Получить значения производных dpi/du"""
        if i == j:
            dpi_dui_real: List[float] = [0.0, 0.0]
            dpi_dui_imag: List[float] = [0.0, 0.0]
            dpi_dui_real[0] = 2 * conductivity_matrix[i, i].real * nodes[i].voltage.real
            dpi_dui_imag[0] = 2 * conductivity_matrix[i, i].real * nodes[i].voltage.imag
            for k in range(len(nodes)):  # номер позиции под знаком суммы
                if k != i:
                    dpi_dui_real[1] += conductivity_matrix[i, k].real * nodes[k].voltage.real
                    dpi_dui_real[1] -= conductivity_matrix[i, k].imag * nodes[k].voltage.imag
                    dpi_dui_imag[1] += conductivity_matrix[i, k].real * nodes[k].voltage.imag
                    dpi_dui_imag[1] += conductivity_matrix[i, k].imag * nodes[k].voltage.real
            return sum(dpi_dui_real), sum(dpi_dui_imag)
        else:
            dpi_duj_real: float = conductivity_matrix[i, j].real * nodes[i].voltage.real
            dpi_duj_real += conductivity_matrix[i, j].imag * nodes[i].voltage.imag
            dpi_duj_imag: float = conductivity_matrix[i, j].real * nodes[i].voltage.imag
            dpi_duj_imag -= conductivity_matrix[i, j].imag * nodes[i].voltage.real
            return dpi_duj_real, dpi_duj_imag

    @staticmethod
    def _get_row_pi(nodes: List[Node], i: int, conductivity_matrix: numpy.ndarray) -> List[float]:
        """Получить строку значений производных dpi/du"""
        row_pi_jm = []
        for j in range(len(nodes)):  # номер напряжения
            if nodes[j].type_node != "S":
                dpi_du = NewtonMethod._get_dpi_du(nodes, i, j, conductivity_matrix)
                row_pi_jm.append(dpi_du[0])
                row_pi_jm.append(dpi_du[1])
        return row_pi_jm

    @staticmethod
    def _get_dqi_du(nodes: List[Node], i: int, j: int, conductivity_matrix: numpy.ndarray) -> Tuple[float, float]:
        """Получить значения производных dqi/du"""
        if i == j:
            dqi_dui_real: List[float] = [0, 0]
            dqi_dui_imag: List[float] = [0, 0]
            dqi_dui_real[0] = -2 * conductivity_matrix[i, i].imag * nodes[i].voltage.real
            dqi_dui_imag[0] = -2 * conductivity_matrix[i, i].imag * nodes[i].voltage.imag
            for k in range(len(nodes)):  # номер позиции под знаком суммы
                if k != i:
                    dqi_dui_real[1] += conductivity_matrix[i, k].real * nodes[k].voltage.imag
                    dqi_dui_real[1] += conductivity_matrix[i, k].imag * nodes[k].voltage.real
                    dqi_dui_imag[1] += conductivity_matrix[i, k].real * nodes[k].voltage.real
                    dqi_dui_imag[1] -= conductivity_matrix[i, k].imag * nodes[k].voltage.imag
            dqi_dui_real[1] = -dqi_dui_real[1]
            return sum(dqi_dui_real), sum(dqi_dui_imag)
        else:
            dqi_duj_real: float = conductivity_matrix[i, j].real * nodes[i].voltage.imag
            dqi_duj_real -= conductivity_matrix[i, j].imag * nodes[i].voltage.real
            dqi_duj_imag: float = -conductivity_matrix[i, j].real * nodes[i].voltage.real
            dqi_duj_imag -= conductivity_matrix[i, j].imag * nodes[i].voltage.imag
        return dqi_duj_real, dqi_duj_imag

    @staticmethod
    def _get_row_qi(nodes: List[Node], i: int, conductivity_matrix: numpy.ndarray) -> List[float]:
        """Получить строку значений производных dqi/du"""
        row_qi_jm = []
        for j in range(len(nodes)):  # номер напряжения
            if nodes[j].type_node != "S":
                dqi_du = NewtonMethod._get_dqi_du(nodes, i, j, conductivity_matrix)
                row_qi_jm.append(dqi_du[0])
                row_qi_jm.append(dqi_du[1])
        return row_qi_jm

    @staticmethod
    def _get_jacobi_matrix(nodes: List[Node], conductivity_matrix: numpy.ndarray) -> numpy.ndarray:
        """Получить матрицу Якоби"""
        jacobi_matrix = []
        for i in range(len(nodes)):  # номер мощности
            if nodes[i].type_node != "S":
                row_pi = NewtonMethod._get_row_pi(nodes, i, conductivity_matrix)
                jacobi_matrix.append(row_pi)
                row_qi = NewtonMethod._get_row_qi(nodes, i, conductivity_matrix)
                jacobi_matrix.append(row_qi)
        return numpy.array(jacobi_matrix)

    @staticmethod
    def _get_delta_voltage(
        nodes: List[Node], power_imbalance: List[complex], jacobi_matrix: numpy.ndarray
    ) -> List[complex]:
        """Решить СЛАУ для нахождения приращений напряжений в узлах"""
        delta = []
        for i, p_imb in enumerate(power_imbalance):
            if nodes[i].type_node != "S":
                delta.append(-p_imb.real)
                delta.append(-p_imb.imag)
        delta_voltage = numpy.linalg.solve(jacobi_matrix, delta)
        return [complex(delta_voltage[i], delta_voltage[i + 1]) for i in range(0, len(delta_voltage), 2)]

    @staticmethod
    def _voltage_correction(nodes: List[Node], delta_voltage: List[complex]) -> List[Node]:
        """Скорректировать напряжения в узлах"""
        j = 0
        for i in range(len(nodes)):
            if nodes[i].type_node != "S":
                nodes[i].voltage_correction(delta_voltage[j])
                j += 1
        return nodes

    @staticmethod
    def _currents(nodes: List[Node], branches: List[Line | Transformer2 | Transformer3], conductivity_matrix: numpy.ndarray) -> List[Line | Transformer2 | Transformer3]:
        """Расчет комплексных токов в ветвях"""
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
        """Расчет потерь мощности в элементах сети"""
        for branch in branches:
            if isinstance(branch, Line) and isinstance(branch.current, complex):
                branch.power_losses = branch.current ** 2 * branch.impedance
            elif isinstance(branch, Transformer2) and isinstance(branch.current, complex):
                branch.power_losses = branch.current ** 2 * branch.impedance + branch.high.voltage**2 * branch.conductivity
            elif (
                isinstance(branch, Transformer3)
                and isinstance(branch.high_current, complex)
                and isinstance(branch.middle_current, complex)
                and isinstance(branch.low_current, complex)
            ):
                s_h = branch.high.voltage * branch.high_current.conjugate() + branch.high.voltage**2 * branch.high_conductivity
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
        Произвести расчет установившегося режима методом Ньютона
        :param nodes: список узлов
        :param branches: список ветвей
        :param parameters: список параметров расчета
        :return: список узлов и ветвей
        """
        conductivity_matrix = get_conductivity_matrix(nodes, branches)
        for iteration in range(0, parameters.iterations):
            power_imbalance = NewtonMethod._get_power_imbalance(nodes, conductivity_matrix)
            if NewtonMethod._unbalance_condition(nodes, parameters, power_imbalance):
                print(f"Точность достигнута! Расчет окончен на итерации №{iteration}!")
                break
            jacobi_matrix = NewtonMethod._get_jacobi_matrix(nodes, conductivity_matrix)
            delta_voltage = NewtonMethod._get_delta_voltage(nodes, power_imbalance, jacobi_matrix)
            nodes = NewtonMethod._voltage_correction(nodes, delta_voltage)
        branches = NewtonMethod._currents(nodes, branches, conductivity_matrix)
        branches = NewtonMethod._power_losses(branches)
        return nodes, branches
