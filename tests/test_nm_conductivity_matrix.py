import numpy as np
import pytest

from src.models.branch import Line
from src.models.conductivity_matrix import get_conductivity_matrix
from src.models.node import Node


def test_conductivity_matrix_size(simple_network):
    """Тест размера матрицы проводимостей"""
    nodes, branches = simple_network
    Y = get_conductivity_matrix(nodes, branches)
    assert Y.shape == (2, 2)


def test_conductivity_matrix_type(simple_network):
    """Тест типа результирующей матрицы"""
    nodes, branches = simple_network
    Y = get_conductivity_matrix(nodes, branches)
    assert isinstance(Y, np.ndarray)


def test_conductivity_matrix_line_symmetry(simple_network):
    """Тест симметрии матрицы для линии"""
    nodes, branches = simple_network
    Y = get_conductivity_matrix(nodes, branches)
    # Для линии: Y[i,j] должна равняться Y[j,i]
    assert Y[0, 1] == Y[1, 0]


def test_conductivity_matrix_line_diagonal(simple_network):
    """Тест диагональных элементов для линии"""
    nodes, branches = simple_network
    Y = get_conductivity_matrix(nodes, branches)
    # Диагональные элементы должны быть положительными
    assert Y[0, 0] > 0
    assert Y[1, 1] > 0


def test_conductivity_matrix_transformer2_diagonal(network_with_transformer2):
    """Тест матрицы для двухобмоточного трансформатора"""
    nodes, branches = network_with_transformer2
    Y = get_conductivity_matrix(nodes, branches)
    # Проверяем размер и наличие данных
    assert Y.shape == (2, 2)
    assert Y[0, 0] != 0
    assert Y[1, 1] != 0


def test_conductivity_matrix_zero_impedance_line():
    """Тест ошибки при нулевом сопротивлении линии"""
    nodes = [
        Node(
            name="Bus_1",
            type_node="S",
            power=complex(0, 0),
            voltage=complex(110, 0),
            shunt_conductivity = complex(0, 0)
        ),
        Node(
            name="Bus_2",
            type_node="L",
            power=complex(50, 25),
            voltage=complex(108, 5),
            shunt_conductivity = complex(0, 0)
        )
    ]
    branches = [
        Line(
            type_branch="Line",
            start=nodes[0],
            end=nodes[1],
            impedance=0,  # нулевое сопротивление - ошибка!
            conductivity=complex(0.001, -0.005)
        )
    ]
    with pytest.raises(ValueError):
        get_conductivity_matrix(nodes, branches)


def test_conductivity_matrix_complex_network():
    """Тест матрицы для более сложной сети (3 узла)"""
    nodes = [
        Node(
            name="Bus_1",
            type_node="S",
            power=complex(0, 0),
            voltage=complex(110, 0),
            shunt_conductivity = complex(0, 0)
        ),
        Node(
            name="Bus_2",
            type_node="L",
            power=complex(50, 25),
            voltage=complex(108, 5),
            shunt_conductivity = complex(0, 0)
        ),
        Node(
            name="Bus_3",
            type_node="L",
            power=complex(30, 15),
            voltage=complex(107, 3),
            shunt_conductivity = complex(0, 0)
        )
    ]
    branches = [
        Line(
            type_branch="Line",
            start=nodes[0],
            end=nodes[1],
            impedance=complex(1.0, 5.0),
            conductivity=complex(0.001, -0.005)
        ),
        Line(
            type_branch="Line",
            start=nodes[1],
            end=nodes[2],
            impedance=complex(0.5, 2.5),
            conductivity=complex(0.002, -0.008)
        )
    ]
    Y = get_conductivity_matrix(nodes, branches)
    assert Y.shape == (3, 3)
    # Проверяем диагональные элементы
    assert Y[0, 0] > 0
    assert Y[1, 1] > 0
    assert Y[2, 2] > 0


def test_conductivity_matrix_values_line():
    """Тест конкретных значений в матрице для линии"""
    nodes = [
        Node(
            name="Bus_1",
            type_node="S",
            power=complex(0, 0),
            voltage=complex(110, 0),
            shunt_conductivity = complex(0, 0)
        ),
        Node(
            name="Bus_2",
            type_node="L",
            power=complex(50, 25),
            voltage=complex(108, 5),
            shunt_conductivity = complex(0, 0)
        )
    ]
    impedance = complex(2.0, 10.0)
    conductivity = complex(0.0, 0.0)

    branches = [
        Line(
            type_branch="Line",
            start=nodes[0],
            end=nodes[1],
            impedance=impedance,
            conductivity=conductivity
        )
    ]
    Y = get_conductivity_matrix(nodes, branches)
    y = 1 / impedance
    assert Y[0, 1] == -y
    assert Y[1, 0] == -y
    assert Y[0, 0] == y
    assert Y[1, 1] == y