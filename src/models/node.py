from math import atan2
from typing import Any, Dict, List

from pydantic import BaseModel


class Node(BaseModel):
    """
    Класс представляющий параметры узла электрической сети
    """

    power: complex  # мощность узла
    voltage: complex  # напряжение в узле
    type_node: str  # тип узла
    name: str  # имя узла
    shunt_conductivity: complex  # проводимость шунта

    @classmethod
    def from_dict(cls, dict_node: Dict[str, Any]) -> Any:
        """
        Конвертировать словаря входных данных узла
        :param dict_node: словарь входных данных узла
        :return: экземпляр узла
        """
        fields_node = [
            "Name",
            "Node type (L, S, LS)",
            ["Power, MVA", "Real", "Imaginary"],
            ["Voltage, kV", "Real", "Imaginary"],
            ["Shunt conductivity, S", "Real", "Imaginary"]
        ]

        if presence_parameters(fields_node, dict_node):
            name = dict_node["Name"]
            type_node = dict_node["Node type (L, S, LS)"]
            power: complex
            if type_node == "S":
                power = complex(0, 0)
            else:
                power = complex(dict_node["Power, MVA"]["Real"], dict_node["Power, MVA"]["Imaginary"])
            voltage = complex(dict_node["Voltage, kV"]["Real"], dict_node["Voltage, kV"]["Imaginary"])
            shunt_conductivity = complex(dict_node["Shunt conductivity, S"]["Real"], dict_node["Shunt conductivity, S"]["Imaginary"])
            return cls(name=name, type_node=type_node, power=power, voltage=voltage, shunt_conductivity=shunt_conductivity)
        else:
            raise KeyError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            raise TypeError
        return self.name == other.name

    def voltage_correction(self, delta_voltage: complex) -> None:
        """
        Корректировать напряжение в узле
        :param delta_voltage: приращение уровня напряжения в узле
        :return: None
        """
        self.voltage = complex(self.voltage.real + delta_voltage.real, self.voltage.imag + delta_voltage.imag)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных узла в виде словаря
        :return: словарь узла
        """
        return {
            "Name": self.name,
            "Node type (L, S, LS)": self.type_node,
            "Power, MVA": {"Real": self.power.real, "Imaginary": self.power.imag, "Magnitude": abs(self.power)},
            "Voltage, kV": {
                "Real": self.voltage.real,
                "Imaginary": self.voltage.imag,
                "Magnitude": abs(self.voltage),
                "Angle": atan2(self.voltage.imag, self.voltage.real),
            },
            "Shunt conductivity, S": {
                "Real": self.shunt_conductivity.real,
                "Imaginary": self.shunt_conductivity.imag,
            },
        }

def presence_parameters(fields_node: List[str], dict_node: Dict[str, Any]) -> bool:
    """
    Проверить наличие ключа в словаре
    :param fields_node: ключи для узла
    :param dict_node: словарь данных узла
    :return:
    """
    for fn in fields_node:
        if not isinstance(fn, list):
            if fn not in dict_node:
                return False
        else:
            if fn[0] not in dict_node and fn[1] not in dict_node[fn[0]] and fn[2] not in dict_node[fn[0]]:
                return False
    return True
