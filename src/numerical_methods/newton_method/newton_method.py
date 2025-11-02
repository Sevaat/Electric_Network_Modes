import json
import os
from pathlib import Path
from typing import List, Dict, Any

from src.numerical_methods.newton_method.models.branch import Branch
from src.numerical_methods.newton_method.models.node import Node
from src.numerical_methods.newton_method.models.parameters import Parameters


class NewtonMethod:
    nodes: List[Node]
    branches: List[Branch]
    parameters: Parameters

    def __init__(self):
        data = self._load()
        self.nodes = [Node(node) for node in data['nodes']]
        self.branches = [Branch(branch) for branch in data['branches']]
        self.parameters = Parameters(data['parameters'])

    @staticmethod
    def _load() -> Dict[str, Any]:
        """
        Читать JSON файл
        :return:
        """
        filepath = str(Path(__file__).resolve().parent / "data")
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
