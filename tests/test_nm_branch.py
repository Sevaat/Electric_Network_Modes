import pytest
from pydantic import ValidationError

from src.numerical_methods.newton_method.models.branch import Line, T2, T3
from src.numerical_methods.newton_method.models.node import Node


def test_line(test_data):
    nodes = [Node.from_dict(node) for node in test_data['NODES']]
    for branch in test_data['BRANCHES']:
        if branch['Type (LINE, T2, T3)'] == 'Line':
            for node in nodes:
                if not isinstance(branch['Node (start)'], Node):
                    if branch['Node (start)'] == node.name:
                        branch['Node (start)'] = node
                if not isinstance(branch['Node (end)'], Node):
                    if branch['Node (end)'] == node.name:
                        branch['Node (end)'] = node
        if branch['Type (LINE, T2, T3)'] == 'T2' or branch['Type (LINE, T2, T3)'] == 'T3':
            for node in nodes:
                if not isinstance(branch['Node (HV)'], Node):
                    if branch['Node (HV)'] == node.name:
                        branch['Node (HV)'] = node
                if not isinstance(branch['Node (LV)'], Node):
                    if branch['Node (LV)'] == node.name:
                        branch['Node (LV)'] = node
                if branch['Type (LINE, T2, T3)'] == 'T3':
                    if not isinstance(branch['Node (MV)'], Node):
                        if branch['Node (MV)'] == node.name:
                            branch['Node (MV)'] = node
    branches = []
    for branch in test_data['BRANCHES']:
        if branch['Type (LINE, T2, T3)'] == 'Line':
            branches.append(Line.from_dict(branch))
        if branch['Type (LINE, T2, T3)'] == 'T2':
            branches.append(T2.from_dict(branch))
        if branch['Type (LINE, T2, T3)'] == 'T3':
            branches.append(T3.from_dict(branch))

    # проверка инициализации
    assert len(branches) == 3
    assert branches[0].high == nodes[0]
    assert branches[0].low == nodes[1]
    assert branches[0].impedance == complex(10, 20)
    assert branches[0].conductivity == complex(0, 0)

    # отсутствуют данные
    branch = {}
    with pytest.raises(KeyError):
        Line.from_dict(branch)

    # неверный тип данных
    branch = {
                "Type (LINE, T2, T3)": True,
                "Node (start)": "1",
                "Node (end)": "2",
                "Impedance, Ohm": {'Real': 10, "Imaginary": 20},
                "Conductivity, S": {'Real': 0, "Imaginary": 0}
            }
    with pytest.raises(ValidationError):
        Line.from_dict(branch)

    # проверка свойств
    assert branches[0].impedance == complex(10, 20)