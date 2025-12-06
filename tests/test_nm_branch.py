import pytest
from pydantic import ValidationError

from src.numerical_methods.newton_method.models.branch import new_branch
from src.numerical_methods.newton_method.models.node import Node


def test_line(test_data):
    nodes = [Node.from_dict(node) for node in test_data['NODES']]
    branches = [new_branch(branch, nodes) for branch in test_data['BRANCHES']]

    # проверка инициализации
    assert len(branches) == 3
    assert branches[0].high == nodes[0]
    assert branches[0].low == nodes[1]
    assert branches[0].impedance == complex(10, 20)
    assert branches[0].conductivity == complex(0, 0)

    # отсутствуют данные
    branch = {}
    with pytest.raises(KeyError):
        new_branch(branch, nodes)

    # неверный тип данных
    branch = {
                "Type (Line, T2, T3)": 'Line',
                "Node (start)": 0,
                "Node (end)": "2",
                "Impedance, Ohm": {'Real': 10, "Imaginary": 20},
                "Conductivity, S": {'Real': 0, "Imaginary": 0}
            }
    with pytest.raises(ValidationError):
        new_branch(branch, nodes)

    branch = {
        "Type (Line, T2, T3)": 'Error',
        "Node (start)": "1",
        "Node (end)": "2",
        "Impedance, Ohm": {'Real': 10, "Imaginary": 20},
        "Conductivity, S": {'Real': 0, "Imaginary": 0}
    }
    with pytest.raises(ValueError):
        new_branch(branch, nodes)

    # проверка свойств
    assert branches[0].impedance == complex(10, 20)