from src.models.branch import new_branch
from src.models.node import Node
from src.models.parameters import Parameters
from src.nonlinear_systems.iterative_gaussian_method import IterativeGaussianMethod


def test_igm_line(test_data_line):
    """Проверка расчета итерационным методом Гаусса для сети, содержащей только линии"""
    nodes = [Node.from_dict(node) for node in test_data_line["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_line["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_line["PARAMETERS"])

    nodes, branches = IterativeGaussianMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(115.372, 0.059)) < 1e-3
    assert abs(nodes[2].voltage - complex(112.198, -2.571)) < 1e-3

def test_igm_t2(test_data_t2):
    """Проверка расчета итерационным методом Гаусса для сети, содержащей только двухобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t2["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t2["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t2["PARAMETERS"])
    nodes, branches = IterativeGaussianMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(11.222, -0.247)) < 1e-3

def test_igm_t3(test_data_t3):
    """Проверка расчета итерационным методом Гаусса для сети, содержащей только трехобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t3["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t3["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t3["PARAMETERS"])

    nodes, branches = IterativeGaussianMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(123.773, -4.773)) < 1e-3
    assert abs(nodes[2].voltage - complex(11.154, -0.789)) < 1e-3