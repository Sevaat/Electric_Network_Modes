import pytest

from src.numerical_methods.newton_method.models.node import Node


@pytest.fixture
def nodes():
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
