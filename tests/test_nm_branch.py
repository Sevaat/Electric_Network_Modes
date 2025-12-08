import pytest

from src.numerical_methods.newton_method.models.branch import Line, Transformer2, Transformer3


def test_line_valid_creation(nodes_line):
    """Тест создания валидной линии"""
    line = Line(
        type_branch="Line",
        start=nodes_line[0],
        end=nodes_line[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005)
    )
    assert line.type_branch == "Line"
    assert line.start == nodes_line[0]
    assert line.end == nodes_line[1]
    assert line.impedance == complex(1.0, 5.0)

def test_line_current_and_losses(nodes_line):
    """Тест установки тока и потерь в линии"""
    line = Line(
        type_branch="Line",
        start=nodes_line[0],
        end=nodes_line[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005),
        current=complex(100, 50),
        power_losses=complex(10, 5)
    )
    assert line.current == complex(100, 50)
    assert line.power_losses == complex(10, 5)

def test_line_from_dict(nodes_line):
    """Тест создания линии из словаря"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": "Node_1",
        "Node (end)": "Node_2",
        "Impedance, Ohm": {"Real": 2.0, "Imaginary": 8.0},
        "Conductivity, S": {"Real": 0.0005, "Imaginary": -0.002}
    }
    line = Line.from_dict(dict_line, nodes_line)
    assert line.type_branch == "Line"
    assert line.start == nodes_line[0]
    assert line.end == nodes_line[1]
    assert line.impedance == complex(2.0, 8.0)

def test_line_from_dict_with_node_objects(nodes_line):
    """Тест создания линии из словаря с объектами узлов"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": nodes_line[0],  # уже объект Node
        "Node (end)": nodes_line[1],
        "Impedance, Ohm": {"Real": 1.5, "Imaginary": 7.5},
        "Conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    line = Line.from_dict(dict_line, nodes_line)
    assert line.start == nodes_line[0]
    assert line.end == nodes_line[1]

def test_line_from_dict_missing_impedance(nodes_line):
    """Тест ошибки при отсутствии сопротивления"""
    dict_line = {
        "Type (Line, T2, T3)": "Line",
        "Node (start)": "Node_1",
        "Node (end)": "Node_2",
        "Conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    with pytest.raises(KeyError):
        Line.from_dict(dict_line, nodes_line)

def test_line_to_dict(nodes_line):
    """Тест преобразования линии в словарь"""
    line = Line(
        type_branch="Line",
        start=nodes_line[0],
        end=nodes_line[1],
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

def test_line_to_dict_missing_current(nodes_line):
    """Тест ошибки при преобразовании линии без тока"""
    line = Line(
        type_branch="Line",
        start=nodes_line[0],
        end=nodes_line[1],
        impedance=complex(1.0, 5.0),
        conductivity=complex(0.001, -0.005),
        current=None,  # не установлен
        power_losses=complex(10, 5)
    )
    with pytest.raises(TypeError):
        line.to_dict()

def test_transformer2_valid_creation(nodes_t2):
    """Тест создания валидного двухобмоточного трансформатора"""
    t2 = Transformer2(
        type_branch="T2",
        high=nodes_t2[0],
        low=nodes_t2[1],
        impedance=complex(0.1, 1.5),
        conductivity=complex(0.001, -0.002),
        tr_rat_high_low=11.0
    )
    assert t2.type_branch == "T2"
    assert t2.high == nodes_t2[0]
    assert t2.low == nodes_t2[1]
    assert t2.tr_rat_high_low == 11.0

def test_transformer2_from_dict(nodes_t2):
    """Тест создания T2 из словаря"""
    dict_t2 = {
        "Type (Line, T2, T3)": "T2",
        "Node (HV)": "HV_Bus",
        "Node (LV)": "LV_Bus",
        "Impedance, Ohm": {"Real": 0.2, "Imaginary": 3.0},
        "Conductivity, S": {"Real": 0.002, "Imaginary": -0.003},
        "Transformation ratio HV-LV": 11.0
    }
    t2 = Transformer2.from_dict(dict_t2, nodes_t2)
    assert t2.high == nodes_t2[0]
    assert t2.low == nodes_t2[1]
    assert t2.tr_rat_high_low == 11.0

def test_transformer2_with_current_and_losses(nodes_t2):
    """Тест T2 с установленными током и потерями"""
    t2 = Transformer2(
        type_branch="T2",
        high=nodes_t2[0],
        low=nodes_t2[1],
        impedance=complex(0.1, 1.5),
        conductivity=complex(0.001, -0.002),
        tr_rat_high_low=11.0,
        current=complex(100, 50),
        power_losses=complex(5, 2)
    )
    result = t2.to_dict()
    assert result["Current, A"] == abs(complex(100, 50)) * 1000
    assert result["Power losses, MVA"]["Real"] == 5

def test_transformer2_fractional_ratio(nodes_t2):
    """Тест T2 с дробным коэффициентом трансформации"""
    t2 = Transformer2(
        type_branch="T2",
        high=nodes_t2[0],
        low=nodes_t2[1],
        impedance=complex(0.1, 1.5),
        conductivity=complex(0.001, -0.002),
        tr_rat_high_low=10.5
    )
    assert t2.tr_rat_high_low == 10.5

def test_transformer3_valid_creation(nodes_t3):
    """Тест создания валидного трехобмоточного трансформатора"""
    t3 = Transformer3(
        type_branch="T3",
        high=nodes_t3[0],
        high_impedance=complex(0.1, 1.5),
        high_conductivity=complex(0.001, -0.002),
        middle=nodes_t3[1],
        middle_impedance=complex(0.15, 2.0),
        low=nodes_t3[2],
        low_impedance=complex(0.2, 2.5),
        tr_rat_high_middle=3.14,
        tr_rat_high_low=11.0,
        neutral_node=nodes_t3[3]
    )
    assert t3.type_branch == "T3"
    assert t3.high == nodes_t3[0]
    assert t3.middle == nodes_t3[1]
    assert t3.low == nodes_t3[2]
    assert t3.neutral_node == nodes_t3[3]

def test_transformer3_without_neutral(nodes_t3):
    """Тест T3 без нейтрального узла (None)"""
    t3 = Transformer3(
        type_branch="T3",
        high=nodes_t3[0],
        high_impedance=complex(0.1, 1.5),
        high_conductivity=complex(0.001, -0.002),
        middle=nodes_t3[1],
        middle_impedance=complex(0.15, 2.0),
        low=nodes_t3[2],
        low_impedance=complex(0.2, 2.5),
        tr_rat_high_middle=3.14,
        tr_rat_high_low=11.0,
        neutral_node=None
    )
    assert t3.neutral_node is None

def test_transformer3_impedance_types(nodes_t3):
    """Тест различных типов данных для сопротивлений T3"""
    t3 = Transformer3(
        type_branch="T3",
        high=nodes_t3[0],
        high_impedance=complex(0.1, 1.5),
        high_conductivity=complex(0.001, -0.002),
        middle=nodes_t3[1],
        middle_impedance=complex(0.15, 2.0),
        low=nodes_t3[2],
        low_impedance=complex(0.2, 2.5),
        tr_rat_high_middle=3,  # int
        tr_rat_high_low=11.0,  # float
        neutral_node=nodes_t3[3]
    )
    assert isinstance(t3.tr_rat_high_middle, int)
    assert isinstance(t3.tr_rat_high_low, float)
