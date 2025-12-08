import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.numerical_methods.newton_method.models.branch import Line, Transformer2, Transformer3, new_branch
from src.numerical_methods.newton_method.models.node import Node
from src.numerical_methods.newton_method.models.parameters import Parameters
from src.numerical_methods.newton_method.newton_method import NewtonMethod


class Methods:
    nodes: List[Node]
    branches: List[Line | Transformer2 | Transformer3]
    parameters: Parameters

    def __init__(self) -> None:
        data = self._load()
        self.nodes = [Node.from_dict(node) for node in data["NODES"]]
        self.branches = [new_branch(branch, self.nodes) for branch in data["BRANCHES"]]
        self.parameters = Parameters.from_dict(data["PARAMETERS"])
        for branch in self.branches:
            if isinstance(branch, Transformer3):
                dict_t3 ={
                    "name": f"T3_{branch.high}_{branch.middle}_{branch.low}",
                    "type_node": "L",
                    "power": complex(0, 0),
                    "voltage": complex(0, 0),
                }
                node = Node.from_dict(dict_t3)
                branch.neutral_node = node
                self.nodes.append(node)

    @staticmethod
    def _load() -> Dict[str, Any]:
        """
        Читать JSON файл
        :return:
        """
        filepath = str(Path(__file__).resolve().parent.parent.parent.parent / "data")
        os.makedirs(filepath, exist_ok=True)
        filepath = f"{filepath}/data_nm.json"
        data = {}
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            print("Файл успешно загружен")
        except FileNotFoundError as e:
            print(f"Файл не найден: {e}")
        except json.JSONDecodeError as e:
            print(f"Ошибка в формате JSON: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        return data

    def _save(self) -> None:
        """
        Запись в JSON файл
        :return:
        """
        filepath = str(Path(__file__).resolve().parent.parent.parent.parent / "result")
        os.makedirs(filepath, exist_ok=True)
        filepath = f"{filepath}/result_{datetime.now().strftime("%d.%m.%Y_%H-%M-%S")}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                nodes_list = [node.to_dict() for node in self.nodes]
                branch_list = [branch.to_dict() for branch in self.branches]
                full_power_losses = sum([branch.power_losses for branch in self.branches])
                data = {
                    "NODES": nodes_list,
                    "BRANCHES": branch_list,
                    "REAL TOTAL POWER LOSSES, MW": full_power_losses.real,
                    "IMAGINARY TOTAL POWER LOSSES, Mvar": full_power_losses.imag,
                }
                json.dump(data, file)
            print("Запись результатов прошла успешно")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def newton_method(
        self, nodes: List[Node], branches: List[Line | Transformer2 | Transformer3], parameters: Parameters
    ) -> None:
        """
        Рассчитать режим методом Ньютона
        :return:
        """
        self.nodes, self.branches = NewtonMethod.run(nodes, branches, parameters)
        self._save()
