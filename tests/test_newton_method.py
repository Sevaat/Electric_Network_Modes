import numpy
import pytest
from pydantic import ValidationError

from src.numerical_methods.newton_method.models.parameters import Parameters
from src.numerical_methods.newton_method.newton_method import NewtonMethod
from src.numerical_methods.newton_method.models.branch import Branch
from src.numerical_methods.newton_method.models.node import Node


def test_node(test_data):
    nodes = [Node(node) for node in test_data['nodes']]

    # проверка инициализации
    assert len(nodes) == 3
    assert nodes[2].name == "3"
    assert nodes[2].type_node == "НАГР"
    assert nodes[2].real_power == 46.188
    assert nodes[2].imaginary_power == 23.094
    assert nodes[2].real_voltage == 110
    assert nodes[2].imaginary_voltage == 0

    # отсутствуют данные
    node = {}
    with pytest.raises(ValidationError):
        Node(node)

    # неверный тип данных
    node = {
        "name": True,
        "type_node": "ИП",
        "real_power": 0,
        "imaginary_power": 0,
        "real_voltage": 115,
        "imaginary_voltage": 0
    }
    with pytest.raises(ValidationError):
        Node(node)

    # проверка сравнения
    assert nodes[0] != nodes[1]
    assert nodes[0] == nodes[0]

    # проверка свойств
    assert abs(nodes[1].full_power - complex(28.8675, 17.3205)) < 0.01
    assert abs(nodes[1].voltage - complex(110, 0)) < 0.01

    # метод коррекции напряжения
    nodes[1].voltage_correction(complex(10, 0))
    assert nodes[1].voltage == complex(120, 0)


def test_branch(test_data):
    nodes = [Node(node) for node in test_data['nodes']]
    for branch in test_data['branches']:
        for node in nodes:
            if not isinstance(branch['start'], Node):
                if branch['start'] == node.name:
                    branch['start'] = node
            if not isinstance(branch['end'], Node):
                if branch['end'] == node.name:
                    branch['end'] = node
    branches = [Branch(branch) for branch in test_data['branches']]

    # проверка инициализации
    assert len(branches) == 3
    assert branches[0].start == nodes[0]
    assert branches[0].end == nodes[1]
    assert branches[0].real_resistance == 10
    assert branches[0].imaginary_resistance == 20
    assert branches[0].real_conductivity == 0
    assert branches[0].imaginary_conductivity == 0

    # отсутствуют данные
    branch = {}
    with pytest.raises(ValidationError):
        Branch(branch)

    # неверный тип данных
    branch = {
        "start": nodes[0],
        "end": nodes[1],
        "real_resistance": 'text',
        "imaginary_resistance": 20,
        "real_conductivity": 0,
        "imaginary_conductivity": 0
    }
    with pytest.raises(ValidationError):
        Branch(branch)

    # проверка свойств
    assert branches[0].impedance == complex(10, 20)


def test_parameters(test_data):
    parameters = Parameters(test_data["parameters"])

    # проверка инициализации
    assert parameters.nominal_voltage == 110
    assert parameters.accuracy == 0.001
    assert parameters.iterations == 100

    # отсутствуют данные
    parameters = {}
    with pytest.raises(ValidationError):
        Parameters(parameters)

    # неверный тип данных
    parameters = {
        "nominal_voltage": 'text',
        "accuracy": 0.001,
        "iterations": 100
    }
    with pytest.raises(ValidationError):
        Parameters(parameters)


def test_newton_method_1(test_data, mocker):
    mock_load = mocker.patch.object(NewtonMethod, '_load')
    mock_load.return_value = test_data
    nm = NewtonMethod()

    # проверка матрицы инцидентности
    incident_matrix = nm._get_incident_matrix()
    assert str(incident_matrix) == str(numpy.array([[1., 1., 0.],[-1., 0., 1.],[0., -1., -1.]]))

    # проверка матрицы проводимостей
    conductivity_matrix = nm._get_conductivity_matrix()
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
    power_imbalance = nm._get_power_imbalance(conductivity_matrix)
    assert abs(power_imbalance[1] + complex(39.8675, 39.3205)) < 1e-3
    assert abs(power_imbalance[2] + complex(-38.8547, -8.4273)) < 1e-3

    # проверка условий по небалансу
    assert not nm._unbalance_condition(power_imbalance)
    assert nm._unbalance_condition([complex(0, 0), complex(0, 0), complex(0, 0)])

    # проверка составления матрицы Якоби
    jm = nm._get_jacobi_matrix(conductivity_matrix)
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
    delta_voltage = nm._get_delta_voltage(power_imbalance, jm)
    assert abs(delta_voltage[0] - complex(5.915, 0.308)) < 1e-3
    assert abs(delta_voltage[1] - complex(0.098, -4.227)) < 1e-3

    # коррекция напряжений
    nm._voltage_correction(delta_voltage)
    assert abs(nm.nodes[1].voltage - complex(115.915, 0.308)) < 1e-3
    assert abs(nm.nodes[2].voltage - complex(110.098, -4.227)) < 1e-3

def test_newton_method_2(test_data, mocker):
    mock_load = mocker.patch.object(NewtonMethod, '_load')
    mock_load.return_value = test_data
    nm = NewtonMethod()

    conductivity_matrix = nm._get_conductivity_matrix()
    for i in range(0, nm.parameters.iterations):
        power_imbalance = nm._get_power_imbalance(conductivity_matrix)
        if nm._unbalance_condition(power_imbalance):
            print('Точность достигнута! Расчет окончен!')
            break
        jacobi_matrix = nm._get_jacobi_matrix(conductivity_matrix)
        delta_voltage = nm._get_delta_voltage(power_imbalance, jacobi_matrix)
        nm._voltage_correction(delta_voltage)
    nm._currents()
    nm._power_losses()

    assert abs(nm.nodes[1].voltage - complex(115.415, 0.272)) < 1e-3
    assert abs(nm.nodes[2].voltage - complex(109.643, -4.126)) < 1e-3
