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

        for branch in branches:
            if branch.type_branch != "T3":
                branch.calculate_current_losses()
            else:
                branch.calculate_current_losses(nodes, conductivity_matrix)

        return nodes, branches
