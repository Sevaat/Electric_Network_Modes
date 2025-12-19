from src.linear_systems.matrix_method import MatrixMethod
from src.models.branch import new_branch
from src.models.node import Node
from src.models.parameters import Parameters


def test_matrix_method_line(test_data_line):
    """Проверка расчета матричным методом для сети, содержащей только линии"""
    nodes = [Node.from_dict(node) for node in test_data_line["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_line["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_line["PARAMETERS"])

    nodes, branches = MatrixMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(115.414, 0.153)) < 1e-3
    assert abs(nodes[2].voltage - complex(112.107, -2.502)) < 1e-3

def test_matrix_method_t2(test_data_t2):
    """Проверка расчета матричным методом для сети, содержащей только двухобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t2["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t2["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t2["PARAMETERS"])
    nodes, branches = MatrixMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(11.471, -0.024)) < 1e-3

def test_matrix_method_t3(test_data_t3):
    """Проверка расчета матричным методом для сети, содержащей только трехобмоточный трансформатор"""
    # проверка правильности расчета
    nodes = [Node.from_dict(node) for node in test_data_t3["NODES"]]
    branches = [new_branch(branch, nodes) for branch in test_data_t3["BRANCHES"]]
    parameters = Parameters.from_dict(test_data_t3["PARAMETERS"])

    nodes, branches = MatrixMethod.run(nodes, branches, parameters)

    assert abs(nodes[1].voltage - complex(125.105, -1.584)) < 1e-3
    assert abs(nodes[2].voltage - complex(11.363, -0.163)) < 1e-3