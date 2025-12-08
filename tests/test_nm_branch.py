import pytest

from src.numerical_methods.newton_method.models.branch import Line


def test_line_valid_creation(nodes):
    """Тест создания валидной линии"""
    line = Line(
        type_branch="Line",
        start=nodes[0],
        end=nodes[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005)
    )
    assert line.type_branch == "Line"
    assert line.start == nodes[0]
    assert line.end == nodes[1]
    assert line.impedance == complex(1.0, 5.0)

def test_line_current_and_losses(nodes):
    """Тест установки тока и потерь в линии"""
    line = Line(
        type_branch="Line",
        start=nodes[0],
        end=nodes[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005),
        current=complex(100, 50),
        power_losses=complex(10, 5)
    )
    assert line.current == complex(100, 50)
    assert line.power_losses == complex(10, 5)

def test_line_from_dict(nodes):
    """Тест создания линии из словаря"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": "Node_1",
        "Node (end)": "Node_2",
        "Impedance, Ohm": {"Real": 2.0, "Imaginary": 8.0},
        "Conductivity, S": {"Real": 0.0005, "Imaginary": -0.002}
    }
    line = Line.from_dict(dict_line, nodes)
    assert line.type_branch == "Line"
    assert line.start == nodes[0]
    assert line.end == nodes[1]
    assert line.impedance == complex(2.0, 8.0)

def test_line_from_dict_with_node_objects(nodes):
    """Тест создания линии из словаря с объектами узлов"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": nodes[0],  # уже объект Node
        "Node (end)": nodes[1],
        "Impedance, Ohm": {"Real": 1.5, "Imaginary": 7.5},
        "Conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    line = Line.from_dict(dict_line, nodes)
    assert line.start == nodes[0]
    assert line.end == nodes[1]

def test_line_from_dict_missing_impedance(nodes):
    """Тест ошибки при отсутствии сопротивления"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": "Node_1",
        "Node (end)": "Node_2",
        "Conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    with pytest.raises(KeyError):
        Line.from_dict(dict_line, nodes)

def test_line_to_dict(nodes):
    """Тест преобразования линии в словарь"""
    line = Line(
        type_branch="Line",
        start=nodes[0],
        end=nodes[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005),
        current=complex(100, 50),
        power_losses=complex(10, 5)
    )
    result = line.to_dict()
    assert result["Type (Line, T2, T3)"] == "Line"
    assert result["Node (start)"] == "Node_1"
    assert result["Node (end)"] == "Node_2"
    assert result["Current, A"] == abs(complex(100, 50)) * 1000
    assert result["Power losses, MVA"] == {"Real": 10, "Imaginary": 5}

def test_line_to_dict_missing_current(nodes):
    """Тест ошибки при преобразовании линии без тока"""
    line = Line(
        type_branch="Line",
        start=nodes[0],
        end=nodes[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005),
        current=None,  # не установлен
        power_losses=complex(10, 5)
    )
    with pytest.raises(TypeError):
        line.to_dict()