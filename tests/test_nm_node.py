import pytest
from pydantic import ValidationError

from src.numerical_methods.newton_method.models.node import Node


def test_node(test_data):
    nodes = [Node.from_dict(node) for node in test_data['NODES']]

    # проверка инициализации
    assert len(nodes) == 3
    assert nodes[2].name == "3"
    assert nodes[2].type_node == "L"
    assert nodes[2].power == complex(46.188, 23.094)
    assert nodes[2].voltage == complex(110, 0)

    # отсутствуют данные
    node = {}
    with pytest.raises(KeyError):
        Node.from_dict(node)

    # неверный тип данных
    node = {
        "Name": True,
        "Node type (L, S, LS)": "S",
        "Power, MVA": {'Real': 0, 'Imaginary': 0},
        "Voltage, kV": {'Real': 115, 'Imaginary': 0}
    }
    with pytest.raises(ValidationError):
        Node.from_dict(node)

    # проверка сравнения
    assert nodes[0] != nodes[1]
    assert nodes[0] == nodes[0]

    # проверка свойств
    assert abs(nodes[1].power - complex(28.8675, 17.3205)) < 0.01
    assert abs(nodes[1].voltage - complex(110, 0)) < 0.01

    # метод коррекции напряжения
    nodes[1].voltage_correction(complex(10, 0))
    assert nodes[1].voltage == complex(120, 0)