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

    assert abs(nodes[1].voltage - complex(115.415, 0.272)) < 1e-3
    assert abs(nodes[2].voltage - complex(109.643, -4.126)) < 1e-3

def test_igm_t2(test_data_t2):
    """Проверка расчета итерационным методом Гаусса для сети, содержащей только двухобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t2["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t2["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t2["PARAMETERS"])
    nodes, branches = IterativeGaussianMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(10.983, -0.405)) < 1e-3

def test_igm_t3(test_data_t3):
    """Проверка расчета итерационным методом Гаусса для сети, содержащей только трехобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t3["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t3["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t3["PARAMETERS"])

    nodes, branches = IterativeGaussianMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(120.616, -7.873)) < 1e-3
    assert abs(nodes[2].voltage - complex(10.674, -1.311)) < 1e-3