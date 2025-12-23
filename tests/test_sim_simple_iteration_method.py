from src.linear_systems.gauss_method import GaussMethod
from src.linear_systems.simple_iteration_method import SimpleIterationMethod
from src.models.branch import new_branch
from src.models.node import Node
from src.models.parameters import Parameters


def test_simple_iteration_method_line(test_data_line):
    """Проверка расчета методом простой итерации для сети, содержащей только линии"""
    nodes = [Node.from_dict(node) for node in test_data_line["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_line["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_line["PARAMETERS"])

    nodes, branches = SimpleIterationMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(115.719, 0.271)) < 1e-3
    assert abs(nodes[2].voltage - complex(109.977, -4.329)) < 1e-3

def test_simple_iteration_method_t2(test_data_t2):
    """Проверка расчета методом простой итерации для сети, содержащей только двухобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t2["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t2["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t2["PARAMETERS"])
    nodes, branches = SimpleIterationMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(11.45, -0.042)) < 1e-3

def test_simple_iteration_method_t3(test_data_t3):
    """Проверка расчета методом простой итерации для сети, содержащей только трехобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t3["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t3["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t3["PARAMETERS"])

    nodes, branches = SimpleIterationMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(124.210, -2.743)) < 1e-3
    assert abs(nodes[2].voltage - complex(11.279, -0.282)) < 1e-3