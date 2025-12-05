from typing import Union, Dict, Any, Optional

from pydantic import ValidationError, BaseModel

from src.numerical_methods.newton_method.models.node import Node

class T2(BaseModel):
    high: Node                                         # имя узла высшей стороны
    low: Node                                          # имя узла низшей стороны
    real_resistance: Union[float, int]                 # активное сопротивление высшей стороны
    imaginary_resistance: Union[float, int]            # реактивное сопротивление высшей стороны
    real_conductivity: Union[float, int]               # активная проводимость высшей стороны (потери хх)
    imaginary_conductivity: Union[float, int]          # реактивная проводимость высшей стороны (потери хх)
    current: Optional[complex] = None                  # ток в высшей стороны
    power_losses: Optional[complex] = None             # потери в высшей стороны

    tr_rat_high_low: Union[float, int]                 # коэффициент трансформации с ВН на СН

    def __init__(self, t2: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in t2:
                raise ValidationError
        t2.update(data)
        super().__init__(**t2)

    @classmethod
    def conv_from_dict(cls, input_dict_t2: Dict[str, Any]) -> Any:
        """
        Конвертация словаря входных данных
        :param input_dict_t2: словарь входных данных трансформаторов
        :return: экземпляр трансформатора
        """
        new_dict_transformer = {'high': input_dict_t2['Node (HV)'], 'low': input_dict_t2['Node (LV)'],
                                'real_resistance': input_dict_t2['Real resistance, Ohm'],
                                'imaginary_resistance': input_dict_t2['Imaginary resistance, Ohm'],
                                'real_conductivity': input_dict_t2['Real conductivity, S'],
                                'imaginary_conductivity': input_dict_t2['Imaginary conductivity, S']}
        return cls(new_dict_transformer)

    @property
    def impedance(self) -> complex:
        return complex(self.real_resistance, self.imaginary_resistance)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных двухобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        return {
            "Node (HV)": self.high.name,
            "Node (LV)": self.low.name,
            "Real resistance, Ohm": self.high_real_resistance,
            "Imaginary resistance, Ohm": self.high_imaginary_resistance,
            "Real conductivity, S": self.high_real_conductivity,
            "Imaginary conductivity, S": self.high_imaginary_conductivity,
            "Current, A": abs(self.high_current) * 1000,
            "Real power losses, MW": self.high_power_losses.real,
            "Imaginary power losses, Mvar": self.high_power_losses.imag,
            "Transformation ratio HV-LV": self.tr_rat_high_low
        }

class T3(BaseModel):
    high: Node                                                  # имя узла высшей стороны
    high_real_resistance: Union[float, int]                     # активное сопротивление высшей стороны
    high_imaginary_resistance: Union[float, int]                # реактивное сопротивление высшей стороны
    high_real_conductivity: Union[float, int]                   # активная проводимость высшей стороны (потери хх)
    high_imaginary_conductivity: Union[float, int]              # реактивная проводимость высшей стороны (потери хх)
    high_current: Optional[complex] = None                      # ток в высшей стороны
    high_power_losses: Optional[complex] = None                 # потери в высшей стороны

    middle: Optional[Node]                                      # имя узла средней стороны
    middle_real_resistance: Union[float, int]                   # активное сопротивление средней стороны
    middle_imaginary_resistance: Union[float, int]              # реактивное сопротивление средней стороны
    middle_current: Optional[complex] = None                    # ток в средней стороны
    middle_power_losses: Optional[complex] = None               # потери в высшей стороны

    low: Node                                                   # имя узла низшей стороны
    low_real_resistance: Union[float, int]                      # активное сопротивление средней стороны
    low_imaginary_resistance: Union[float, int]                 # реактивное сопротивление средней стороны
    low_current: Optional[complex] = None                       # ток в средней стороны
    low_power_losses: Optional[complex] = None                  # потери в высшей стороны

    tr_rat_high_middle: Union[float, int]                       # коэффициент трансформации с ВН на СН
    tr_rat_high_low: Union[float, int]                          # коэффициент трансформации с ВН на НН

    def __init__(self, t3: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in t3:
                raise ValidationError
        t3.update(data)
        super().__init__(**t3)

    @classmethod
    def conv_from_dict(cls, input_dict_t3: Dict[str, Any]) -> Any:
        """
        Конвертация словаря входных данных
        :param input_dict_t3: словарь входных данных трансформаторов
        :return: экземпляр трансформатора
        """
        new_dict_transformer = {
            'high': input_dict_t3['Node (HV)'],
            'high_real_resistance': input_dict_t3['High real resistance, Ohm'],
            'high_imaginary_resistance': input_dict_t3['High imaginary resistance, Ohm'],
            'high_real_conductivity': input_dict_t3['High real conductivity, S'],
            'high_imaginary_conductivity': input_dict_t3['High imaginary conductivity, S'],

            'middle': input_dict_t3['Node (MV)'],
            'middle_real_resistance': input_dict_t3['Middle real resistance, Ohm'],
            'middle_imaginary_resistance': input_dict_t3['Middle imaginary resistance, Ohm'],

            'low': input_dict_t3['Node (LV)'],
            'low_real_resistance': input_dict_t3['Low real resistance, Ohm'],
            'low_imaginary_resistance': input_dict_t3['Low imaginary resistance, Ohm'],

            'tr_rat_high_middle': input_dict_t3['Transformation ratio HV-MV'],
            'tr_rat_high_low': input_dict_t3['Transformation ratio HV-LV'],
        }
        return cls(new_dict_transformer)

    @property
    def high_impedance(self) -> complex:
        return complex(self.high_real_resistance, self.high_imaginary_resistance)

    @property
    def middle_impedance(self) -> complex:
        return complex(self.middle_real_resistance, self.middle_imaginary_resistance)

    @property
    def low_impedance(self) -> complex:
        return complex(self.low_real_resistance, self.low_imaginary_resistance)

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных трехобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        return {
            "Node (HV)": self.high.name,
            "High real resistance, Ohm": self.high_real_resistance,
            "High imaginary resistance, Ohm": self.high_imaginary_resistance,
            "High real conductivity, S": self.high_real_conductivity,
            "High imaginary conductivity, S": self.high_imaginary_conductivity,
            "High current, A": abs(self.high_current) * 1000,
            "High real power losses, MW": self.high_power_losses.real,
            "High imaginary power losses, Mvar": self.high_power_losses.imag,

            "Node (MV)": self.middle.name,
            "Middle real resistance, Ohm": self.middle_real_resistance,
            "Middle imaginary resistance, Ohm": self.middle_imaginary_resistance,
            "Middle current, A": abs(self.middle_current) * 1000,
            "Middle real power losses, MW": self.middle_power_losses.real,
            "Middle imaginary power losses, Mvar": self.middle_power_losses.imag,

            "Node (LV)": self.low.name,
            "Low real resistance, Ohm": self.low_real_resistance,
            "Low imaginary resistance, Ohm": self.low_imaginary_resistance,
            "Low current, A": abs(self.low_current) * 1000,
            "Low real power losses, MW": self.low_power_losses.real,
            "Low imaginary power losses, Mvar": self.low_power_losses.imag,

            "Transformation ratio HV-MV": self.tr_rat_high_middle,
            "Transformation ratio HV-LV": self.tr_rat_high_low
        }
