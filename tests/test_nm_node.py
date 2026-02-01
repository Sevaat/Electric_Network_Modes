import pytest

from src.models.node import Node


def test_node_valid_creation():
    """Тест создания валидного узла"""
    node = Node(
        name="Node_1",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    assert node.name == "Node_1"
    assert node.type_node == "L"
    assert node.power == complex(10, 5)
    assert node.voltage == complex(110, 0)

def test_node_slack_bus():
    """Тест создания балансирующего узла (S)"""
    node = Node(
        name="Slack",
        type_node="S",
        power=complex(0, 0),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    assert node.type_node == "S"
    assert node.power == complex(0, 0)

def test_node_load_generation_bus():
    """Тест создания узла с нагрузкой и генерацией (LS)"""
    node = Node(
        name="Mixed",
        type_node="LS",
        power=complex(50, 25),
        voltage=complex(110, 5),
        shunt_conductivity = complex(0, 0)
    )
    assert node.type_node == "LS"

def test_node_equality():
    """Тест проверки равенства узлов по имени"""
    node1 = Node(
        name="Same",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    node2 = Node(
        name="Same",
        type_node="S",
        power=complex(20, 10),
        voltage=complex(220, 0),
        shunt_conductivity = complex(0, 0)
    )
    assert node1 == node2  # равны по имени

def test_node_inequality():
    """Тест проверки неравенства узлов"""
    node1 = Node(
        name="Node_1",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    node2 = Node(
        name="Node_2",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    assert node1 != node2

def test_node_equality_type_error():
    """Тест ошибки типа при сравнении с не-узлом"""
    node = Node(
        name="Node_1",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    with pytest.raises(TypeError):
        node == "not_a_node"

def test_node_voltage_correction():
    """Тест коррекции напряжения узла"""
    node = Node(
        name="Test",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 0),
        shunt_conductivity = complex(0, 0)
    )
    delta = complex(1, 2)
    node.voltage_correction(delta)
    assert node.voltage == complex(111, 2)

def test_node_voltage_correction_negative():
    """Тест коррекции напряжения с отрицательным приращением"""
    node = Node(
        name="Test",
        type_node="L",
        power=complex(10, 5),
        voltage=complex(110, 5),
        shunt_conductivity = complex(0, 0)
    )
    delta = complex(-5, -2)
    node.voltage_correction(delta)
    assert node.voltage == complex(105, 3)

def test_node_from_dict_load_bus():
    """Тест создания узла нагрузки из словаря"""
    dict_node = {
        "Name": "Load_Bus",
        "Node type (L, S, LS)": "L",
        "Power, MVA": {"Real": 50.0, "Imaginary": 25.0},
        "Voltage, kV": {"Real": 110.0, "Imaginary": 0.0},
        "Shunt conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    node = Node.from_dict(dict_node)
    assert node.name == "Load_Bus"
    assert node.type_node == "L"
    assert node.power == complex(50.0, 25.0)
    assert node.voltage == complex(110.0, 0.0)

def test_node_from_dict_slack_bus():
    """Тест создания балансирующего узла из словаря"""
    dict_node = {
        "Name": "Slack",
        "Node type (L, S, LS)": "S",
        "Power, MVA": {"Real": 0.0, "Imaginary": 0.0},
        "Voltage, kV": {"Real": 115.0, "Imaginary": 0.0},
        "Shunt conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    node = Node.from_dict(dict_node)
    assert node.power == complex(0, 0)  # автоматически обнуляется для типа S

def test_node_from_dict_missing_keys():
    """Тест ошибки при отсутствии ключей в словаре"""
    dict_node = {
        "Name": "Incomplete",
        # Missing required keys
    }
    with pytest.raises(KeyError):
        Node.from_dict(dict_node)

def test_node_from_dict_missing_complex_fields():
    """Тест ошибки при отсутствии Real/Imaginary в комплексных полях"""
    dict_node = {
        "Name": "Test",
        "Node type (L, S, LS)": "L",
        "Power, MVA": {"Real": 50.0},
        "Voltage, kV": {"Real": 110.0, "Imaginary": 0.0},
        "Shunt conductivity, S": {"Real": 0.0, "Imaginary": 0.0}
    }
    with pytest.raises(KeyError):
        Node.from_dict(dict_node)

def test_node_to_dict():
    """Тест преобразования узла в словарь"""
    node = Node(
        name="Test_Node",
        type_node="L",
        power=complex(30, 15),
        voltage=complex(110, 0),
        shunt_conductivity=complex(0, 0)
    )
    result = node.to_dict()
    assert result["Name"] == "Test_Node"
    assert result["Node type (L, S, LS)"] == "L"
    assert result["Power, MVA"]["Real"] == 30
    assert result["Power, MVA"]["Imaginary"] == 15
    assert result["Voltage, kV"]["Real"] == 110
    assert result["Voltage, kV"]["Imaginary"] == 0
    assert result["Shunt conductivity, S"]["Real"] == 0
    assert result["Shunt conductivity, S"]["Imaginary"] == 0
