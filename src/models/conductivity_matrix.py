from typing import List

import numpy

from src.models.branch import Line, Transformer2, Transformer3
from src.models.node import Node


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
            conductivity_matrix[i, j] += -y
            conductivity_matrix[j, i] += -y
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
            conductivity_matrix[i, j] += -y * k
            conductivity_matrix[j, i] += -y * k
            conductivity_matrix[i, i] += y + y0.conjugate()
            conductivity_matrix[j, j] += k**2 * y
        else:
            raise ValueError

    for t3 in transformer3:
        if t3.high_impedance != 0 and t3.middle_impedance != 0 and t3.low_impedance != 0:
            y0 = t3.high_conductivity

            z_h = t3.high_impedance
            z_m = t3.middle_impedance
            z_l = t3.low_impedance

            z = z_h * z_m + z_h * z_l + z_m * z_l

            k_hm = t3.tr_rat_high_middle
            k_hl = t3.tr_rat_high_low

            y_ii = 1 / z_h - z_m * z_l / (z * z_h)
            y_jj = k_hm**2 / z_m - z_h * z_l * k_hm**2 / (z * z_m)
            y_kk = k_hl**2 / z_l - z_h * z_m * k_hl**2 / (z * z_l)

            y_ij_ji = -z_l * k_hm / z
            y_ik_ki = -z_m * k_hl / z
            y_jk_kj = -z_h * k_hm * k_hl / z

            i = nodes.index(t3.high)
            j = nodes.index(t3.middle)
            k = nodes.index(t3.low)

            conductivity_matrix[i, i] += y_ii + y0.conjugate()
            conductivity_matrix[j, j] += y_jj
            conductivity_matrix[k, k] += y_kk

            conductivity_matrix[i, j] += y_ij_ji
            conductivity_matrix[j, i] += y_ij_ji
            conductivity_matrix[i, k] += y_ik_ki
            conductivity_matrix[k, i] += y_ik_ki
            conductivity_matrix[j, k] += y_jk_kj
            conductivity_matrix[k, j] += y_jk_kj
        else:
            raise ValueError

    return conductivity_matrix
