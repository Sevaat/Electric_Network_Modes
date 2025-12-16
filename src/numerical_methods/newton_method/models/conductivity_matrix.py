from typing import List

import numpy

from src.numerical_methods.newton_method.models.branch import Line, Transformer2, Transformer3
from src.numerical_methods.newton_method.models.node import Node


def get_conductivity_matrix(nodes: List[Node], branches: List[Line | Transformer2 | Transformer3]) -> numpy.ndarray:
    """
    Составить матрицу собственных и взаимных проводимостей с учетом вида линии
    :param nodes: список узлов
    :param branches: список ветвей (линии, двух- и трехобмоточные трансформаторы
    :return: матрица собственных и взаимных проводимостей
    """
    lines = [branch for branch in branches if isinstance(branch, Line)]
    transformer2 = [branch for branch in branches if isinstance(branch, Transformer2)]
    transformer3 = [branch for branch in branches if isinstance(branch, Transformer3)]

    conductivity_matrix = numpy.zeros((len(nodes), len(nodes)), dtype=complex)

    for line in lines:
        if line.impedance != 0:
            i = nodes.index(line.start)
            j = nodes.index(line.end)
            y0 = line.conductivity
            y = 1 / line.impedance
            conductivity_matrix[i, j] = -y
            conductivity_matrix[j, i] = -y
            conductivity_matrix[i, i] += y + y0 / 2
            conductivity_matrix[j, j] += y + y0 / 2
        else:
            raise ValueError

    for t2 in transformer2:
        if t2.impedance != 0:
            i = nodes.index(t2.high)
            j = nodes.index(t2.low)
            y0 = t2.conductivity
            y = 1 / t2.impedance
            k = t2.tr_rat_high_low
            conductivity_matrix[i, j] = -y * k
            conductivity_matrix[j, i] = -y * k
            conductivity_matrix[i, i] += y + y0.conjugate()
            conductivity_matrix[j, j] += k**2 * y
        else:
            raise ValueError

    for t3 in transformer3:
        if isinstance(t3.neutral_node, Node):
            if t3.high_impedance != 0 and t3.middle_impedance != 0 and t3.low_impedance != 0:
                i = nodes.index(t3.high)
                j = nodes.index(t3.middle)
                k = nodes.index(t3.low)
                m = nodes.index(t3.neutral_node)
                y0 = t3.high_conductivity
                yi = 1 / t3.high_impedance
                yj = 1 / t3.middle_impedance
                yk = 1 / t3.low_impedance
                kij = t3.tr_rat_high_middle
                kik = t3.tr_rat_high_low
                # обмотка ВН (от узла i к нейтральному узлу m)
                conductivity_matrix[i, m] = -yi
                conductivity_matrix[m, i] = -yi
                conductivity_matrix[i, i] += yi + y0.conjugate()
                conductivity_matrix[m, m] += yi
                # обмотка СН (от нейтрального узла m к узлу j)
                conductivity_matrix[m, j] = -yj * kij
                conductivity_matrix[j, m] = -yj * kij
                conductivity_matrix[m, m] += yj
                conductivity_matrix[j, j] += kij**2 * yj
                # обмотка СН (от нейтрального узла m к узлу k)
                conductivity_matrix[m, k] = -yk * kik
                conductivity_matrix[k, m] = -yk * kik
                conductivity_matrix[m, m] += yk
                conductivity_matrix[k, k] += kik**2 * yk
            else:
                raise ValueError
        else:
            raise TypeError

    return conductivity_matrix
