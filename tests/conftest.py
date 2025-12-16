import pytest

from src.numerical_methods.newton_method.models.branch import Line, Transformer2
from src.numerical_methods.newton_method.models.node import Node


@pytest.fixture
def nodes_line():
    """Фикстура с двумя узлами для тестирования линий"""
    node1 = Node(
        name="Node_1",
        type_node="S",
        power=complex(0, 0),
        voltage=complex(110, 0)
    )
    node2 = Node(
        name="Node_2",
        type_node="L",
        power=complex(50, 25),
        voltage=complex(108, 5)
    )
    return [node1, node2]


@pytest.fixture
def nodes_t2():
    """Фикстура с узлами ВН и НН"""
    hv = Node(
        name="HV_Bus",
        type_node="S",
        power=complex(0, 0),
        voltage=complex(110, 0)
    )
    lv = Node(
        name="LV_Bus",
        type_node="L",
        power=complex(50, 25),
        voltage=complex(10, 0)
    )
    return [hv, lv]


@pytest.fixture
def nodes_t3():
    """Фикстура с узлами для трехобмоточного трансформатора"""
    hv = Node(
        name="HV_Bus",
        type_node="S",
        power=complex(0, 0),
        voltage=complex(110, 0)
    )
    mv = Node(
        name="MV_Bus",
        type_node="L",
        power=complex(30, 15),
        voltage=complex(35, 2)
    )
    lv = Node(
        name="LV_Bus",
        type_node="L",
        power=complex(50, 25),
        voltage=complex(10, 0)
    )
    return [hv, mv, lv]


@pytest.fixture
def simple_network():
    """Фикстура простой сети из 2 узлов и 1 линии"""
    nodes = [
        Node(
            name="Bus_1",
            type_node="S",
            power=complex(0, 0),
            voltage=complex(110, 0)
        ),
        Node(
            name="Bus_2",
            type_node="L",
            power=complex(50, 25),
            voltage=complex(108, 5)
        )
    ]
    branches = [
        Line(
            type_branch="Line",
            start=nodes[0],
            end=nodes[1],
            impedance=complex(1.0, 5.0),
            conductivity=complex(0.001, -0.005)
        )
    ]
    return nodes, branches


@pytest.fixture
def network_with_transformer2():
    """Фикстура сети с двухобмоточным трансформатором"""
    nodes = [
        Node(
            name="HV",
            type_node="S",
            power=complex(0, 0),
            voltage=complex(110, 0)
        ),
        Node(
            name="LV",
            type_node="L",
            power=complex(50, 25),
            voltage=complex(10, 0)
        )
    ]
    branches = [
        Transformer2(
            type_branch="T2",
            high=nodes[0],
            low=nodes[1],
            impedance=complex(0.1, 1.5),
            conductivity=complex(0.001, -0.002),
            tr_rat_high_low=11.0
        )
    ]
    return nodes, branches


@pytest.fixture
def test_data_line():
    return {
        "NODES": [
            {
                "Name": "1",
                "Node type (L, S, LS)": "S",
                "Power, MVA": {
                    "Real": 0,
                    "Imaginary": 0
                },
                "Voltage, kV": {
                    "Real": 115,
                    "Imaginary": 0
                }
            },
            {
                "Name": "2",
                "Node type (L, S, LS)": "LS",
                "Power, MVA": {
                    "Real": 28.8675,
                    "Imaginary": 17.3205
                },
                "Voltage, kV": {
                    "Real": 110,
                    "Imaginary": 0
                }
            },
            {
                "Name": "3",
                "Node type (L, S, LS)": "L",
                "Power, MVA": {
                    "Real": 46.1880,
                    "Imaginary": 23.0940
                },
                "Voltage, kV": {
                    "Real": 110,
                    "Imaginary": 0
                }
            }
        ],
        "BRANCHES": [
            {
                "Node (start)": "1",
                "Node (end)": "2",
                "Type (Line, T2, T3)": "Line",
                "Impedance, Ohm": {
                    "Real": 10,
                    "Imaginary": 20
                },
                "Conductivity, S": {
                    "Real": 0,
                    "Imaginary": 0
                }
            },
            {
                "Node (start)": "1",
                "Node (end)": "3",
                "Type (Line, T2, T3)": "Line",
                "Impedance, Ohm": {
                    "Real": 15,
                    "Imaginary": 30
                },
                "Conductivity, S": {
                    "Real": 0,
                    "Imaginary": 0
                }
            },
            {
                "Node (start)": "2",
                "Node (end)": "3",
                "Type (Line, T2, T3)": "Line",
                "Impedance, Ohm": {
                    "Real": 10,
                    "Imaginary": 25
                },
                "Conductivity, S": {
                    "Real": 0,
                    "Imaginary": 0
                }
            }
        ],
        "PARAMETERS": {
            "Nominal voltage, kV": 110,
            "Accuracy": 0.001,
            "Max iterations": 100
        }
    }

@pytest.fixture
def test_data_t2():
    return {
        "NODES": [
            {
                "Name": "1",
                "Node type (L, S, LS)": "S",
                "Power, MVA": {
                    "Real": 0,
                    "Imaginary": 0
                },
                "Voltage, kV": {
                    "Real": 115,
                    "Imaginary": 0
                }
            },
            {
                "Name": "2",
                "Node type (L, S, LS)": "L",
                "Power, MVA": {
                    "Real": 1,
                    "Imaginary": 1
                },
                "Voltage, kV": {
                    "Real": 10,
                    "Imaginary": 0
                }
            }
        ],
        "BRANCHES": [
            {
                "Node (HV)": "1",
                "Node (LV)": "2",
                "Type (Line, T2, T3)": "T2",
                "Impedance, Ohm": {
                    "Real": 42.6,
                    "Imaginary": 508.2
                },
                "Conductivity, S": {
                    "Real": 0.455e-6,
                    "Imaginary": 3.1e-6
                },
                "Transformation ratio HV-LV": 10
            }
        ],
        "PARAMETERS": {
            "Nominal voltage, kV": 110,
            "Accuracy": 0.001,
            "Max iterations": 100
        }
    }

@pytest.fixture
def test_data_t3():
    return {
        "NODES": [
            {
                "Name": "1",
                "Node type (L, S, LS)": "S",
                "Power, MVA": {
                    "Real": 0,
                    "Imaginary": 0
                },
                "Voltage, kV": {
                    "Real": 240,
                    "Imaginary": 0
                }
            },
            {
                "Name": "2",
                "Node type (L, S, LS)": "L",
                "Power, MVA": {
                    "Real": 40,
                    "Imaginary": 30
                },
                "Voltage, kV": {
                    "Real": 110,
                    "Imaginary": 0
                }
            },
            {
                "Name": "3",
                "Node type (L, S, LS)": "L",
                "Power, MVA": {
                    "Real": 30,
                    "Imaginary": 10
                },
                "Voltage, kV": {
                    "Real": 10,
                    "Imaginary": 0
                }
            }
        ],
        "BRANCHES": [
            {
                "Type (Line, T2, T3)": "T3",
                "Node (HV)": "1",
                "Node (MV)": "2",
                "Node (LV)": "3",
                "High_impedance, Ohm": {
                    "Real": 0.7,
                    "Imaginary": 52
                },
                "High_conductivity, S": {
                    "Real": 0.85e-6,
                    "Imaginary": 5.95e-6
                },
                "Middle_impedance, Ohm": {
                    "Real": 0.7,
                    "Imaginary": 0
                },
                "Low_impedance, Ohm": {
                    "Real": 1.4,
                    "Imaginary": 98
                },
                "Transformation ratio HV-MV": 1.9,
                "Transformation ratio HV-LV": 20.91
            }
        ],
        "PARAMETERS": {
            "Nominal voltage, kV": 220,
            "Accuracy": 0.001,
            "Max iterations": 100
        }
    }
