import numpy

from src.numerical_methods.newton_method.models.branch import new_branch
from src.numerical_methods.newton_method.models.conductivity_matrix import get_conductivity_matrix
from src.numerical_methods.newton_method.models.node import Node
from src.numerical_methods.newton_method.models.parameters import Parameters
from src.numerical_methods.newton_method.newton_method import NewtonMethod


def test_newton_method_line(test_data_line):
    """Проверка расчета методом Ньютона для сети, содержащей только линии"""
    nodes = [Node.from_dict(node) for node in test_data_line["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_line["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_line["PARAMETERS"])

    # проверка матрицы проводимостей
    conductivity_matrix = get_conductivity_matrix(nodes, branches)
    assert abs(conductivity_matrix[0, 0] - complex(0.033, -0.067)) < 1e-3
    assert abs(conductivity_matrix[0, 1] - complex(-0.020, 0.040)) < 1e-3
    assert abs(conductivity_matrix[0, 2] - complex(-0.013, 0.027)) < 1e-3
    assert abs(conductivity_matrix[1, 0] - complex(-0.020, 0.040)) < 1e-3
    assert abs(conductivity_matrix[1, 1] - complex(0.034, -0.074)) < 1e-3
    assert abs(conductivity_matrix[1, 2] - complex(-0.014, 0.034)) < 1e-3
    assert abs(conductivity_matrix[2, 0] - complex(-0.013, 0.027)) < 1e-3
    assert abs(conductivity_matrix[2, 1] - complex(-0.014, 0.034)) < 1e-3
    assert abs(conductivity_matrix[2, 2] - complex(0.027, -0.061)) < 1e-3

    # проверка небалансов мощности
    power_imbalance = NewtonMethod._get_power_imbalance(nodes, conductivity_matrix)
    assert abs(power_imbalance[1] + complex(39.8675, 39.3205)) < 1e-3
    assert abs(power_imbalance[2] + complex(-38.8547, -8.4273)) < 1e-3

    # проверка условий по небалансу
    assert not NewtonMethod._unbalance_condition(nodes, parameters, power_imbalance)
    assert NewtonMethod._unbalance_condition(nodes, parameters, [complex(0, 0), complex(0, 0), complex(0, 0)])

    # проверка составления матрицы Якоби
    jm = NewtonMethod._get_jacobi_matrix(nodes, conductivity_matrix)
    assert abs(jm[0, 0] - 3.617) < 1e-3
    assert abs(jm[0, 1] - 8.393) < 1e-3
    assert abs(jm[0, 2] + 1.517) < 1e-3
    assert abs(jm[0, 3] + 3.793) < 1e-3
    assert abs(jm[1, 0] - 7.993) < 1e-3
    assert abs(jm[1, 1] + 3.817) < 1e-3
    assert abs(jm[1, 2] + 3.793) < 1e-3
    assert abs(jm[1, 3] - 1.517) < 1e-3
    assert abs(jm[2, 0] + 1.517) < 1e-3
    assert abs(jm[2, 1] + 3.793) < 1e-3
    assert abs(jm[2, 2] - 2.917) < 1e-3
    assert abs(jm[2, 3] - 6.860) < 1e-3
    assert abs(jm[3, 0] + 3.793) < 1e-3
    assert abs(jm[3, 1] - 1.517) < 1e-3
    assert abs(jm[3, 2] - 6.593) < 1e-3
    assert abs(jm[3, 3] + 3.051) < 1e-3

    # проверка приращений напряжений
    delta_voltage = NewtonMethod._get_delta_voltage(nodes, power_imbalance, jm)
    assert abs(delta_voltage[0] - complex(5.915, 0.308)) < 1e-3
    assert abs(delta_voltage[1] - complex(0.098, -4.227)) < 1e-3

    # коррекция напряжений
    nodes = NewtonMethod._voltage_correction(nodes, delta_voltage)
    assert abs(nodes[1].voltage - complex(115.915, 0.308)) < 1e-3
    assert abs(nodes[2].voltage - complex(110.098, -4.227)) < 1e-3

    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_line["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_line["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_line["PARAMETERS"])
    conductivity_matrix = get_conductivity_matrix(nodes, branches)
    nodes, branches = NewtonMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(115.415, 0.272)) < 1e-3
    assert abs(nodes[2].voltage - complex(109.643, -4.126)) < 1e-3

def test_newton_method_t2(test_data_t2):
    """Проверка расчета методом Ньютона для сети, содержащей только двухобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t2["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t2["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t2["PARAMETERS"])
    conductivity_matrix = get_conductivity_matrix(nodes, branches)
    nodes, branches = NewtonMethod.run(nodes, branches, parameters)

    assert abs(nodes[0].voltage - complex(115, 0)) < 1e-3
    assert abs(nodes[1].voltage - complex(10.985, -0.405)) < 1e-3



