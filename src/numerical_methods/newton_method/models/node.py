from typing import Union, Dict, Any, Self

from pydantic import ValidationError, BaseModel
from math import atan


class Node(BaseModel):
    real_power: Union[float, int]               # активная мощность узла
    imaginary_power: Union[Union[float, int], str]          # реактивная мощность узла
    real_voltage: Union[float, int]                         # действительная часть напряжения
    imaginary_voltage: Union[float, int]                    # мнимая часть напряжения
    type_node: str                                          # тип узла
    name: str                                               # имя узла

    def __init__(self, node: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in node:
                raise ValidationError
        node.update(data)
        super().__init__(**node)

    @classmethod
    def conv_from_dict(cls, input_dict_node: Dict[str, Any]) -> Any:
        new_dict_node = {'name': input_dict_node['ИМЯ'], 'type_node': input_dict_node['ТИП УЗЛА (НАГР, ИПО, ИП)'],
                         'real_power': input_dict_node['АКТ. МОЩНОСТЬ, МВт'],
                         'imaginary_power': input_dict_node['РЕАКТ. МОЩНОСТЬ, Мвар'],
                         'real_voltage': input_dict_node['АКТ. НАПРЯЖЕНИЕ, кВ'],
                         'imaginary_voltage': input_dict_node['РЕАКТ. НАПРЯЖЕНИЕ, кВ']}
        return cls(new_dict_node)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            raise TypeError
        return self.name == other.name

    @property
    def full_power(self) -> complex:
        return complex(self.real_power, self.imaginary_power)

    @property
    def voltage(self) -> complex:
        return complex(self.real_voltage, self.imaginary_voltage)

    def voltage_correction(self, delta_voltage: complex) -> None:
        self.real_voltage += delta_voltage.real
        self.imaginary_voltage += delta_voltage.imag

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных узла в виде словаря
        :return: словарь узла
        """
        return {
            "name": self.name,
            "type_node": self.type_node,
            "real_power": self.real_power,
            "imaginary_power": self.imaginary_power,
            "full_power": abs(self.full_power),
            "real_voltage": self.real_voltage,
            "imaginary_voltage": self.imaginary_voltage,
            "voltage_module": abs(self.voltage),
            "voltage_angle": atan(self.imaginary_voltage / self.real_voltage)
        }
