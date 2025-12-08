from math import atan2
from typing import Any, Dict

from pydantic import BaseModel


class Node(BaseModel):
    """
    Класс представляющий параметры узла электрической сети
    """

    power: complex  # мощность узла
    voltage: complex  # напряжение в узле
    type_node: str  # тип узла
    name: str  # имя узла

    @classmethod
    def from_dict(cls, dict_node: Dict[str, Any]) -> Any:
        """
        Конвертировать словаря входных данных узла
        :param dict_node: словарь входных данных узла
        :return: экземпляр узла
        """
        if any([
            "Name" in dict_node,
            "Node type (L, S, LS)" in dict_node,
            "Power, MVA" in dict_node,
            "Voltage, kV" in dict_node,
        ]):
            if any([
                "Real" in dict_node["Power, MVA"],
                "Imaginary" in dict_node["Power, MVA"],
                "Real" in dict_node["Voltage, kV"],
                "Imaginary" in dict_node["Voltage, kV"],
            ]):
                name = dict_node["Name"]
                type_node = dict_node["Node type (L, S, LS)"]
                power: complex
                if type_node == "S":
                    power = complex(0, 0)
                else:
                    power = complex(dict_node["Power, MVA"]["Real"], dict_node["Power, MVA"]["Imaginary"])
                voltage = complex(dict_node["Voltage, kV"]["Real"], dict_node["Voltage, kV"]["Imaginary"])
                return cls(name=name, type_node=type_node, power=power, voltage=voltage)
            else:
                raise KeyError
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
        }
