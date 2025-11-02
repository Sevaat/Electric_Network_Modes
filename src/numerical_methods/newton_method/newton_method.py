import json
import os
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple

import numpy

from src.numerical_methods.newton_method.models.branch import Branch
from src.numerical_methods.newton_method.models.node import Node
from src.numerical_methods.newton_method.models.parameters import Parameters


class NewtonMethod:
    nodes: List[Node]
    branches: List[Branch]
    parameters: Parameters

    def __init__(self):
        data = self._load()
        self.nodes = [Node(node) for node in data['nodes']]
        for branch in data['branches']:
            for node in self.nodes:
                if branch['start'] == node.name:
                    branch['start'] = node
                if branch['end'] == node.name:
                    branch['end'] = node
        self.branches = [Branch(branch) for branch in data['branches']]
        self.parameters = Parameters(data['parameters'])

    @staticmethod
    def _load() -> Dict[str, Any]:
        """
        Читать JSON файл
        :return:
        """
        filepath = str(Path(__file__).resolve().parent / "data")
        os.makedirs(filepath, exist_ok=True)
        filepath = f"{filepath}/data_nm.json"
        data = {}
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            print("Файл успешно загружен")
        except FileNotFoundError as e:
            print(f"Файл не найден: {e}")
        except json.JSONDecodeError as e:
            print(f"Ошибка в формате JSON: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        return data

    def _save(self) -> None:
        """
        Запись в JSON файл
        :return:
        """
        filepath = str(Path(__file__).resolve().parent / "result")
        os.makedirs(filepath, exist_ok=True)
        filepath = f"{filepath}/result_nm_{datetime.now().strftime("%d.%m.%Y_%H-%M-%S")}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                nodes_list = [node.to_dict() for node in self.nodes]
                branch_list = [branch.to_dict() for branch in self.branches]
                full_power_loss = sum([branch.power_losses for branch in self.branches])
                data = {"nodes": nodes_list, "branches": branch_list, "full_power_loss": full_power_loss}
                json.dump(data, file)
            print("Запись результатов прошла успешно")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def _get_incident_matrix(self) -> numpy.ndarray:
        """
        Получить матрицу инцидентности
        :return: матрица инцидентности
        """
        incident_matrix = numpy.zeros((len(self.nodes), len(self.branches)))
        for i, branch in enumerate(self.branches):
            number_node: List[Union[int, None]] = [None, None]
            for j, node in enumerate(self.nodes):
                if branch.start == node:
                    number_node[0] = j
                elif branch.end == node:
                    number_node[1] = j
                else:
                    continue
            incident_matrix[number_node[0], i] = 1
            incident_matrix[number_node[1], i] = -1
        return incident_matrix

    def _get_conductivity_matrix(self) -> numpy.ndarray:
        """
        Получить матрицу собственных и взаимных проводимостей
        :return: матрица собственных и взаимных проводимостей
        """
        conductivity_matrix = numpy.array([1 / branch.impedance for branch in self.branches])
        incident_matrix = self._get_incident_matrix()
        conductivity_matrix = numpy.dot(incident_matrix, numpy.diag(conductivity_matrix))
        conductivity_matrix = numpy.dot(conductivity_matrix, incident_matrix.transpose())
        imaginary_conductivity = []
        for i in range(len(self.nodes)):
            b = 0
            for j in range(len(self.branches)):
                if incident_matrix[i, j] != 0.:
                    b += self.branches[j].imaginary_conductivity
            imaginary_conductivity.append(b)
        imaginary_conductivity = [complex(0, b) for b in imaginary_conductivity]
        imaginary_conductivity = numpy.array(imaginary_conductivity)
        imaginary_conductivity = numpy.diag(imaginary_conductivity)
        conductivity_matrix = conductivity_matrix + imaginary_conductivity
        return conductivity_matrix

    def _get_power_imbalance(self, conductivity_matrix: numpy.ndarray) -> List[complex]:
        """
        Получить небалансы мощности в узлах
        :param conductivity_matrix: матрица собственных и взаимных проводимостей
        :return: небалансы мощностей по узлам
        """
        node_count = len(self.nodes)
        power_imbalance: List[complex] = []
        for i in range(node_count):
            full_power: Union[complex, None] = None
            if self.nodes[i].type_node == 'ИП':
                full_power = complex(0, 0)
            elif self.nodes[i].type_node == 'ИПО':
                full_power = -self.nodes[i].full_power
            else:
                full_power = self.nodes[i].full_power
            real_power = [0, 0, 0]
            real_power[0] = full_power.real + conductivity_matrix[i, i].real * self.nodes[i].voltage ** 2
            imaginary_power = [0, 0, 0]
            imaginary_power[0] = full_power.imag - conductivity_matrix[i, i].imag * self.nodes[i].voltage ** 2
            for j in range(node_count):
                if j != i:
                    real_power[1] += conductivity_matrix[i, j].real * self.nodes[j].real_voltage
                    real_power[1] -= conductivity_matrix[i, j].imag * self.nodes[j].imaginary_voltage
                    real_power[2] += conductivity_matrix[i, j].real * self.nodes[j].imaginary_voltage
                    real_power[2] += conductivity_matrix[i, j].imag * self.nodes[j].real_voltage
                    imaginary_power[1] += conductivity_matrix[i, j].real * self.nodes[j].real_voltage
                    imaginary_power[1] -= conductivity_matrix[i, j].imag * self.nodes[j].imaginary_voltage
                    imaginary_power[2] += conductivity_matrix[i, j].real * self.nodes[j].imaginary_voltage
                    imaginary_power[2] += conductivity_matrix[i, j].imag * self.nodes[j].real_voltage
            real_power[1] = self.nodes[i].real_voltage * real_power[1]
            real_power[2] = self.nodes[i].imaginary_voltage * real_power[2]
            imaginary_power[1] = self.nodes[i].imaginary_voltage * imaginary_power[1]
            imaginary_power[2] = - self.nodes[i].real_voltage * imaginary_power[2]
            power_imbalance.append(complex(sum(real_power), sum(imaginary_power)))
        return power_imbalance

    def _unbalance_condition(self, power_imbalance: List[complex]) -> bool:
        """
        Проверка, что все небалансы меньше заданной точности
        :param power_imbalance: небалансы мощностей по узлам
        :return: True - небалансы меньше заданного порога точности, False - иначе
        """
        for i, p_imb in enumerate(power_imbalance):
            if self.nodes[i].type_node != 'ИП':
                if abs(p_imb.real) < self.parameters.accuracy and abs(p_imb.imag) < self.parameters.accuracy:
                    return True
        return False

    class JacobiMatrix(ABC):
        @staticmethod
        def _get_dpi_du(i: int, j: int, conductivity_matrix: numpy.ndarray) -> Tuple[float, float]:
            """
            Получить значения производных dpi/du
            :param i: номер текущего узла
            :param j: номер другого узла
            :param conductivity_matrix: матрица собственных и взаимных проводимостей
            :return: значения производных dpi/du
            """
            if i == j:
                dpi_dui_real = [0, 0]
                dpi_dui_imag = [0, 0]
                dpi_dui_real[0] = 2 * conductivity_matrix[i, i].real * NewtonMethod.nodes[i].real_voltage
                dpi_dui_imag[0] = 2 * conductivity_matrix[i, i].real * NewtonMethod.nodes[i].imaginary_voltage
                for k in range(len(NewtonMethod.nodes)):  # номер позиции под знаком суммы
                    if k != i:
                        dpi_dui_real[1] += conductivity_matrix[i, k].real * NewtonMethod.nodes[k].real_voltage
                        dpi_dui_real[1] -= conductivity_matrix[i, k].imag * NewtonMethod.nodes[k].imaginary_voltage
                        dpi_dui_imag[1] += conductivity_matrix[i, k].real * NewtonMethod.nodes[k].imaginary_voltage
                        dpi_dui_imag[1] += conductivity_matrix[i, k].imag * NewtonMethod.nodes[k].real_voltage
                dpi_dui_real = dpi_dui_real[0] + dpi_dui_real[1]
                dpi_dui_imag = dpi_dui_imag[0] + dpi_dui_imag[1]
                return dpi_dui_real, dpi_dui_imag
            else:
                dpi_duj_real = conductivity_matrix[i, j].real * NewtonMethod.nodes[i].real_voltage
                dpi_duj_real += conductivity_matrix[i, j].imag * NewtonMethod.nodes[i].imaginary_voltage
                dpi_duj_imag = conductivity_matrix[i, j].real * NewtonMethod.nodes[i].imaginary_voltage
                dpi_duj_imag -= conductivity_matrix[i, j].imag * NewtonMethod.nodes[i].real_voltage
                return dpi_duj_real, dpi_duj_imag

        @staticmethod
        def _get_row_pi(i: int, conductivity_matrix: numpy.ndarray) -> List[float]:
            """
            Получить строку значений производных dpi/du
            :param i: номер текущего узла
            :param conductivity_matrix: матрица собственных и взаимных проводимостей
            :return: строка матрицы значений производных dpi/du
            """
            row_pi_jm = []
            for j in range(len(NewtonMethod.nodes)):  # номер напряжения
                if NewtonMethod.nodes[j].type_node != 'ИП':
                    dpi_du = NewtonMethod.JacobiMatrix._get_dpi_du(i, j, conductivity_matrix)
                    row_pi_jm.append(dpi_du[0])
                    row_pi_jm.append(dpi_du[1])
            return row_pi_jm

        @staticmethod
        def _get_dqi_du(i: int, j: int, conductivity_matrix: numpy.ndarray) -> Tuple[float, float]:
            """
            Получить значения производных dqi/du
            :param i: номер текущего узла
            :param j: номер другого узла
            :param conductivity_matrix: матрица собственных и взаимных проводимостей
            :return: значения производных dqi/du
            """
            if i == j:
                dqi_dui_real = [0, 0]
                dqi_dui_imag = [0, 0]
                dqi_dui_real[0] = - 2 * conductivity_matrix[i, i].imag * NewtonMethod.nodes[i].real_voltage
                dqi_dui_imag[0] = - 2 * conductivity_matrix[i, i].imag * NewtonMethod.nodes[i].imaginary_voltage
                for k in range(len(NewtonMethod.nodes)):  # номер позиции под знаком суммы
                    if k != i:
                        dqi_dui_real[1] += conductivity_matrix[i, k].real * NewtonMethod.nodes[k].imaginary_voltage
                        dqi_dui_real[1] += conductivity_matrix[i, k].imag * NewtonMethod.nodes[k].real_voltage
                        dqi_dui_imag[1] += conductivity_matrix[i, k].real * NewtonMethod.nodes[k].real_voltage
                        dqi_dui_imag[1] -= conductivity_matrix[i, k].imag * NewtonMethod.nodes[k].imaginary_voltage
                dqi_dui_real = dqi_dui_real[0] - dqi_dui_real[1]
                dqi_dui_imag = dqi_dui_imag[0] + dqi_dui_imag[1]
                return dqi_dui_real, dqi_dui_imag
            else:
                dqi_duj_real = conductivity_matrix[i, j].real * NewtonMethod.nodes[i].imaginary_voltage
                dqi_duj_real -= conductivity_matrix[i, j].imag * NewtonMethod.nodes[i].real_voltage
                dqi_duj_imag = - conductivity_matrix[i, j].real * NewtonMethod.nodes[i].real_voltage
                dqi_duj_imag -= conductivity_matrix[i, j].imag * NewtonMethod.nodes[i].imaginary_voltage
            return dqi_duj_real, dqi_duj_imag

        @staticmethod
        def _get_row_qi(i: int, conductivity_matrix: numpy.ndarray) -> List[float]:
            """
            Получить строку значений производных dqi/du
            :param i: номер текущего узла
            :param conductivity_matrix: матрица собственных и взаимных проводимостей
            :return: строка матрицы значений производных dqi/du
            """
            row_qi_jm = []
            for j in range(len(NewtonMethod.nodes)):  # номер напряжения
                if NewtonMethod.nodes[j].type_node != 'ИП':
                    dqi_du = NewtonMethod.JacobiMatrix._get_dqi_du(i, j, conductivity_matrix)
                    row_qi_jm.append(dqi_du[0])
                    row_qi_jm.append(dqi_du[1])
            return row_qi_jm

        @staticmethod
        def get_jacobi_matrix(conductivity_matrix: numpy.ndarray) -> numpy.ndarray:
            """
            Получить матрицу Якоби
            :param conductivity_matrix: матрица собственных и взаимных проводимостей
            :return: матрица Якоби
            """
            jacobi_matrix = []
            for i in range(len(NewtonMethod.nodes)):  # номер мощности
                if NewtonMethod.nodes[i].type_node != 'ИП':
                    row_pi = NewtonMethod.JacobiMatrix._get_row_pi(i, conductivity_matrix)
                    jacobi_matrix.append(row_pi)
                    row_qi = NewtonMethod.JacobiMatrix._get_row_qi(i, conductivity_matrix)
                    jacobi_matrix.append(row_qi)
            return numpy.array(jacobi_matrix)

    def _get_delta_voltage(self, power_imbalance: List[complex], jacobi_matrix: numpy.ndarray) -> List[complex]:
        """
        Решить СЛАУ для нахождения приращений напряжений в узлах
        :param power_imbalance: небалансы мощностей по узлам
        :param jacobi_matrix: матрица Якоби
        :return: приращения напряжений в узлах
        """
        delta = []
        for i, p_imb in enumerate(power_imbalance):
            if self.nodes[i].type_node != 'ИП':
                delta.append(-p_imb.real)
                delta.append(-p_imb.imag)
        delta_voltage = numpy.linalg.solve(jacobi_matrix, delta)
        return [complex(delta_voltage[i], delta_voltage[i + 1]) for i in range(0, len(delta_voltage), 2)]

    def _voltage_correction(self, delta_voltage: List[complex]) -> None:
        """
        Скорректировать напряжения в узлах
        :param delta_voltage: приращения напряжений в узлах
        :return:
        """
        j = 0
        for i in range(len(self.nodes)):
            if self.nodes[i].type_node != 'ИП':
                self.nodes[i].voltage_correction(delta_voltage[j])
                j += 1

    def _currents(self) -> None:
        for branch in self.branches:
            branch.current = (branch.start.voltage - branch.end.voltage) / branch.impedance

    def _power_losses(self) -> None:
        for branch in self.branches:
            branch.power_losses = branch.current ** 2 * branch.impedance

    def run(self) -> None:
        conductivity_matrix = self._get_conductivity_matrix()
        for i in range(0, self.parameters.number_of_iterations):
            power_imbalance = self._get_power_imbalance(conductivity_matrix)
            if self._unbalance_condition(power_imbalance):
                print('Точность достигнута! Расчет окончен!')
                break
            jacobi_matrix = self.JacobiMatrix.get_jacobi_matrix(conductivity_matrix)
            delta_voltage = self._get_delta_voltage(power_imbalance, jacobi_matrix)
            self._voltage_correction(delta_voltage)
        self._currents()
        self._power_losses()
        self._save()

