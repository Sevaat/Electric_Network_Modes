from typing import Union, Dict, Any, Optional

from pydantic import ValidationError, BaseModel

from src.numerical_methods.newton_method.models.node import Node


class Branch(BaseModel):
    start: Node                                     # имя стартового узла ветви
    end: Node                                       # имя конечного узла ветви
    real_resistance: Union[float, int]              # активное сопротивление
    imaginary_resistance: Union[float, int]         # реактивное сопротивление
    real_conductivity: Union[float, int]            # активная проводимость
    imaginary_conductivity: Union[float, int]       # реактивная проводимость
    current: Optional[complex] = None               # ток в линии
    power_losses: Optional[complex] = None          # потери в линии

    def __init__(self, branch: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in branch:
                raise ValidationError
        branch.update(data)
        super().__init__(**branch)

    @classmethod
    def conv_from_dict(cls, input_dict_branch: Dict[str, Any]) -> Any:
        """
        Конвертация словаря входных данных
        :param input_dict_branch: словарь входных данных ветви
        :return: экземпляр ветви
        """
        new_dict_branch = {'start': input_dict_branch['Node (start)'],
                           'end': input_dict_branch['Node (end)'],
                           'real_resistance': input_dict_branch['Real resistance, Ohm'],
                           'imaginary_resistance': input_dict_branch['Imaginary resistance, Ohm'],
                           'real_conductivity': input_dict_branch['Real conductivity, S'],
                           'imaginary_conductivity': input_dict_branch['Imaginary conductivity, S']}
        return cls(new_dict_branch)

    @property
    def impedance(self) -> complex:
        return complex(self.real_resistance, self.imaginary_resistance)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных ветви в виде словаря
        :return: словарь ветви
        """
        return {
            "start": self.start.name,
            "end": self.end.name,
            "real_resistance": self.real_resistance,
            "imaginary_resistance": self.imaginary_resistance,
            "real_conductivity": self.real_conductivity,
            "imaginary_conductivity": self.imaginary_conductivity,
            "current": abs(self.current),
            "real_power_losses": self.power_losses.real,
            "imaginary_power_losses": self.power_losses.imag
        }

