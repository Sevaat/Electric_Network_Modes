import pytest

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
    neutral = Node(
        name="Neutral",
        type_node="L",
        power=complex(0, 0),
        voltage=complex(0, 0)
    )
    return [hv, mv, lv, neutral]
