from typing import Union, Dict, Any

from pydantic import ValidationError, BaseModel

from src.numerical_methods.newton_method.models.node import Node


class Branch(BaseModel):
    start: Node                                     # имя стартового узла ветви
    end: Node                                       # имя конечного узла ветви
    real_resistance: Union[float, int]              # активное сопротивление
    imaginary_resistance: Union[float, int]         # реактивное сопротивление
    real_conductivity: Union[float, int]            # активная проводимость
    imaginary_conductivity: Union[float, int]       # реактивная проводимость
    current: complex                                # ток в линии
    power_losses: complex                           # потери в линии

    def __init__(self, branch: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in branch:
                raise ValidationError
        branch.update(data)
        super().__init__(**branch)

    @property
    def impedance(self) -> complex:
        return complex(self.real_conductivity, self.imaginary_conductivity)

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
            "power_losses": self.power_losses
        }

