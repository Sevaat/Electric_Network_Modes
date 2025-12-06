from typing import Union, Dict, Any, Optional, Type, TypeVar, Self

from pydantic import ValidationError, BaseModel

from src.numerical_methods.newton_method.models.node import Node


class Line(BaseModel):
    """
    Класс представляющий параметры схемы замещения линии электропередачи
    """
    type_branch: str  # тип ветви
    high: Node  # имя стартового узла ветви
    low: Node  # имя конечного узла ветви
    impedance: complex  # сопротивление (активное, реактивное)
    conductivity: complex  # проводимость (активная, реактивная)
    current: Optional[complex] = None  # ток в линии
    power_losses: Optional[complex] = None  # потери в линии

    @classmethod
    def from_dict(cls, dict_line: Dict[str, Any]) -> Self:
        """
        Конвертировать словаря входных данных линии электропередачи
        :param dict_line: словарь входных данных линии электропередачи
        :return: экземпляр линии электропередачи
        """
        type_branch = dict_line['Type (LINE, T2, T3)']
        high = dict_line['Node (start)']
        low = dict_line['Node (end)']
        impedance = complex(dict_line['Impedance, Ohm']['Real'],
                                 dict_line['Impedance, Ohm']['Imaginary'])
        conductivity = complex(dict_line['Conductivity, S']['Real'],
                                    dict_line['Conductivity, S']['Imaginary'])
        return cls(type_branch=type_branch,
                   high=high,
                   low=low,
                   impedance=impedance,
                   conductivity=conductivity)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных ветви в виде словаря
        :return: словарь ветви
        """
        return {
            "Type (LINE, T2, T3)": self.type_branch,
            "Node (start)": self.start.name,
            "Node (end)": self.end.name,
            "Impedance, Ohm":
                {
                    'Real': self.impedance.real,
                    'Imaginary': self.impedance.imag
                },
            "Conductivity, S":
                {
                    'Real': self.conductivity.real,
                    'Imaginary': self.conductivity.imag
                },
            "Current, A": abs(self.current) * 1000,
            "Power losses, MVA":
                {
                    'Real': self.power_losses.real,
                    'Imaginary': self.power_losses.imag
                }
        }


class T2(BaseModel):
    """
    Класс представляющий параметры схемы замещения двухобмоточного трансформатора
    """
    type_branch: str  # тип ветви
    high: Node  # имя узла высшей стороны
    low: Node  # имя узла низшей стороны
    impedance: complex  # сопротивление (активное, реактивное)
    conductivity: complex  # проводимость (активная, реактивная)
    current: Optional[complex] = None  # ток в высшей стороны
    power_losses: Optional[complex] = None  # потери в высшей стороны
    tr_rat_high_low: Union[float, int]  # коэффициент трансформации с ВН на СН

    @classmethod
    def from_dict(cls, dict_t2: Dict[str, Any]) -> Self:
        """
        Конвертировать словаря входных данных двухобмоточного трансформатора
        :param dict_t2: словарь входных данных двухобмоточного трансформатора
        :return: экземпляр двухобмоточного трансформатора
        """
        type_branch = dict_t2['Type (LINE, T2, T3)']
        high = dict_t2['Node (HV)']
        low = dict_t2['Node (LV)']
        impedance = complex(dict_t2['Impedance, Ohm']['Real'],
                                 dict_t2['Impedance, Ohm']['Imaginary'])
        conductivity = complex(dict_t2['Conductivity, S']['Real'],
                                    dict_t2['Conductivity, S']['Imaginary'])
        tr_rat_high_low = dict_t2['Transformation ratio HV-LV']
        return cls(type_branch=type_branch,
                   high=high,
                   low=low,
                   impedance=impedance,
                   conductivity=conductivity,
                   tr_rat_high_low=tr_rat_high_low)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных двухобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        return {
            "Type (LINE, T2, T3)": self.type_branch,
            "Node (HV)": self.high.name,
            "Node (LV)": self.low.name,
            "Impedance, Ohm":
                {
                    'Real': self.impedance.real,
                    'Imaginary': self.impedance.imag
                },
            "Conductivity, S":
                {
                    'Real': self.conductivity.real,
                    'Imaginary': self.conductivity.imag
                },
            "Current, A": abs(self.high_current) * 1000,
            "Power losses, MVA":
                {
                    'Real': self.power_losses.real,
                    'Imaginary': self.power_losses.imag
                },
            "Transformation ratio HV-LV": self.tr_rat_high_low
        }

class T3(BaseModel):
    """
    Класс представляющий параметры схемы замещения трехобмоточного трансформатора
    """
    type_branch: str  # тип ветви
    high: Node  # имя узла высшей стороны
    high_impedance: complex  # сопротивление ВН (активное, реактивное)
    high_conductivity: complex  # проводимость ВН (активная, реактивная)
    high_current: Optional[complex] = None  # ток ВН
    high_power_losses: Optional[complex] = None  # потери ВН
    middle: Optional[Node]  # имя узла средней стороны
    middle_impedance: complex  # сопротивление ВН (активное, реактивное)
    middle_current: Optional[complex] = None  # ток в средней стороны
    middle_power_losses: Optional[complex] = None  # потери в высшей стороны
    low: Node  # имя узла низшей стороны
    low_impedance: complex  # сопротивление ВН (активное, реактивное)
    low_current: Optional[complex] = None  # ток в средней стороны
    low_power_losses: Optional[complex] = None  # потери в высшей стороны
    tr_rat_high_middle: Union[float, int]  # коэффициент трансформации с ВН на СН
    tr_rat_high_low: Union[float, int]  # коэффициент трансформации с ВН на НН

    @classmethod
    def from_dict(cls, dict_t3: Dict[str, Any]) -> Self:
        """
        Конвертировать словаря входных данных трехобмоточного трансформатора
        :param dict_t3: словарь входных данных трехобмоточного трансформатора
        :return: экземпляр трехобмоточного трансформатора
        """
        type_branch = dict_t3['Type (LINE, T2, T3)']
        high = dict_t3['Node (HV)']
        high_impedance = complex(dict_t3['High_impedance, Ohm']['Real'],
                                      dict_t3['High_impedance, Ohm']['Imaginary'])
        high_conductivity = complex(dict_t3['High_conductivity, S']['Real'],
                                         dict_t3['High_conductivity, S']['Imaginary'])
        middle = dict_t3['Node (MV)']
        middle_impedance = complex(dict_t3['Middle_impedance, Ohm']['Real'],
                                        dict_t3['Middle_impedance, Ohm']['Imaginary'])
        low = dict_t3['Node (LV)']
        low_impedance = complex(dict_t3['Low_impedance, Ohm']['Real'],
                                     dict_t3['Low_impedance, Ohm']['Imaginary'])
        tr_rat_high_middle = dict_t3['Transformation ratio HV-MV']
        tr_rat_high_low = dict_t3['Transformation ratio HV-LV']
        return cls(type_branch=type_branch,
                   high=high,
                   high_impedance=high_impedance,
                   high_conductivity=high_conductivity,
                   middle=middle,
                   middle_impedance=middle_impedance,
                   low=low,
                   low_impedance=low_impedance,
                   tr_rat_high_middle=tr_rat_high_middle,
                   tr_rat_high_low=tr_rat_high_low)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных трехобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        return {
            "Type (LINE, T2, T3)": self.type_branch,
            "Node (HV)": self.high.name,
            "Node (MV)": self.middle.name,
            "Node (LV)": self.low.name,

            "High impedance, Ohm":
                {
                    'Real': self.high_impedance.real,
                    'Imaginary': self.high_impedance.imag
                },
            "High conductivity, S":
                {
                    'Real': self.high_conductivity.real,
                    'Imaginary': self.high_conductivity.imag
                },
            "High current, A": abs(self.high_current) * 1000,
            "High power losses, MVA":
                {
                    'Real': self.high_power_losses.real,
                    'Imaginary': self.high_power_losses.imag
                },

            "Middle impedance, Ohm":
                {
                    'Real': self.middle_impedance.real,
                    'Imaginary': self.middle_impedance.imag
                },
            "Middle current, A": abs(self.middle_current) * 1000,
            "Middle power losses, MVA":
                {
                    'Real': self.middle_power_losses.real,
                    'Imaginary': self.middle_power_losses.imag
                },
            "Transformation ratio HV-MV": self.tr_rat_high_middle,

            "Low impedance, Ohm":
                {
                    'Real': self.low_impedance.real,
                    'Imaginary': self.low_impedance.imag
                },
            "Low current, A": abs(self.low_current) * 1000,
            "Low power losses, MVA":
                {
                    'Real': self.low_power_losses.real,
                    'Imaginary': self.low_power_losses.imag
                },
            "Transformation ratio HV-LV": self.tr_rat_high_low
        }
