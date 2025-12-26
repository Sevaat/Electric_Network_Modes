from typing import Any, Dict, List, Optional, Self, Union

import numpy as np
from pydantic import BaseModel

from src.models.node import Node


class Line(BaseModel):
    """
    Класс представляющий параметры схемы замещения линии электропередачи
    """

    type_branch: str  # тип ветви
    start: Node  # имя стартового узла ветви
    end: Node  # имя конечного узла ветви
    impedance: complex  # сопротивление (активное, реактивное)
    conductivity: complex  # проводимость (активная, реактивная)
    current: Optional[complex] = None  # ток в линии
    power_losses: Optional[complex] = None  # потери в линии

    @classmethod
    def from_dict(cls, dict_line: Dict[str, Any], nodes: List[Node]) -> Self:
        """
        Конвертировать словаря входных данных линии электропередачи
        :param nodes: список узлов
        :param dict_line: словарь входных данных линии электропередачи
        :return: экземпляр линии электропередачи
        """
        fields_line = [
            "Node (start)",
            "Node (end)",
            "Type (Line, T2, T3)",
            ["Impedance, Ohm", "Real", "Imaginary"],
            ["Conductivity, S", "Real", "Imaginary"]
        ]

        if presence_parameters(fields_line, dict_line):
            key_nodes = ["Node (start)", "Node (end)"]
            for node in nodes:
                for key_node in key_nodes:
                    if not isinstance(dict_line[key_node], Node):
                        if dict_line[key_node] == node.name:
                            dict_line[key_node] = node

            type_branch = dict_line["Type (Line, T2, T3)"]
            start = dict_line["Node (start)"]
            end = dict_line["Node (end)"]
            impedance = complex(dict_line["Impedance, Ohm"]["Real"], dict_line["Impedance, Ohm"]["Imaginary"])
            conductivity = complex(dict_line["Conductivity, S"]["Real"], dict_line["Conductivity, S"]["Imaginary"])
            return cls(
                type_branch=type_branch, start=start, end=end, impedance=impedance, conductivity=conductivity
            )
        else:
            raise KeyError

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных ветви в виде словаря
        :return: словарь ветви
        """
        current = None
        real_power_losses = None
        imag_power_losses = None
        if isinstance(self.current, complex):
            current = abs(self.current) * 1000
        else:
            raise TypeError
        if isinstance(self.power_losses, complex):
            real_power_losses = self.power_losses.real
            imag_power_losses = self.power_losses.imag
        else:
            raise TypeError
        return {
            "Type (Line, T2, T3)": self.type_branch,
            "Node (start)": self.start.name,
            "Node (end)": self.end.name,
            "Impedance, Ohm": {"Real": self.impedance.real, "Imaginary": self.impedance.imag},
            "Conductivity, S": {"Real": self.conductivity.real, "Imaginary": self.conductivity.imag},
            "Current, A": current,
            "Power losses, MVA": {"Real": real_power_losses, "Imaginary": imag_power_losses},
        }

    def calculate_current_losses(self) -> None:
        """
        Рассчитать ток в линии электропередачи и потери мощности
        :return: None
        """
        try:
            self.current = (self.start.voltage - self.end.voltage) / self.impedance
            self.power_losses = 3 * self.current**2 * self.impedance
        except AttributeError:
            raise AttributeError

class Transformer2(BaseModel):
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
    def from_dict(cls, dict_t2: Dict[str, Any], nodes: List[Node]) -> Self:
        """
        Конвертировать словаря входных данных двухобмоточного трансформатора
        :param nodes: список узлов
        :param dict_t2: словарь входных данных двухобмоточного трансформатора
        :return: экземпляр двухобмоточного трансформатора
        """
        fields_t2 = [
            "Node (HV)",
            "Node (LV)",
            "Type (Line, T2, T3)",
            ["Impedance, Ohm", "Real", "Imaginary"],
            ["Conductivity, S", "Real", "Imaginary"],
            "Transformation ratio HV-LV"
        ]

        if presence_parameters(fields_t2, dict_t2):
            key_nodes = ["Node (HV)", "Node (LV)"]
            for node in nodes:
                for key_node in key_nodes:
                    if not isinstance(dict_t2[key_node], Node):
                        if dict_t2[key_node] == node.name:
                            dict_t2[key_node] = node

            type_branch = dict_t2["Type (Line, T2, T3)"]
            high = dict_t2["Node (HV)"]
            low = dict_t2["Node (LV)"]
            impedance = complex(dict_t2["Impedance, Ohm"]["Real"], dict_t2["Impedance, Ohm"]["Imaginary"])
            conductivity = complex(dict_t2["Conductivity, S"]["Real"], dict_t2["Conductivity, S"]["Imaginary"])
            tr_rat_high_low = dict_t2["Transformation ratio HV-LV"]
            return cls(
                type_branch=type_branch,
                high=high,
                low=low,
                impedance=impedance,
                conductivity=conductivity,
                tr_rat_high_low=tr_rat_high_low,
            )
        else:
            raise KeyError

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных двухобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        current = None
        real_power_losses = None
        imag_power_losses = None
        if isinstance(self.current, complex):
            current = abs(self.current) * 1000
        else:
            raise TypeError
        if isinstance(self.power_losses, complex):
            real_power_losses = self.power_losses.real
            imag_power_losses = self.power_losses.imag
        else:
            raise TypeError
        return {
            "Type (Line, T2, T3)": self.type_branch,
            "Node (HV)": self.high.name,
            "Node (LV)": self.low.name,
            "Impedance, Ohm": {"Real": self.impedance.real, "Imaginary": self.impedance.imag},
            "Conductivity, S": {"Real": self.conductivity.real, "Imaginary": self.conductivity.imag},
            "Current, A": current,
            "Power losses, MVA": {"Real": real_power_losses, "Imaginary": imag_power_losses},
            "Transformation ratio HV-LV": self.tr_rat_high_low,
        }

    def calculate_current_losses(self) -> None:
        """
        Рассчитать ток в двухобмоточном трансформаторе и потери мощности
        :return: None
        """
        try:
            self.current = (self.high.voltage - self.low.voltage) / self.impedance
            self.power_losses = 3 * self.current**2 * self.impedance
        except AttributeError:
            raise AttributeError


class Transformer3(BaseModel):
    """
    Класс представляющий параметры схемы замещения трехобмоточного трансформатора
    """

    type_branch: str  # тип ветви
    high: Node  # имя узла высшей стороны
    high_impedance: complex  # сопротивление ВН (активное, реактивное)
    high_conductivity: complex  # проводимость ВН (активная, реактивная)
    high_current: Optional[complex] = None  # ток ВН
    middle: Node  # имя узла средней стороны
    middle_impedance: complex  # сопротивление ВН (активное, реактивное)
    middle_current: Optional[complex] = None  # ток в средней стороны
    low: Node  # имя узла низшей стороны
    low_impedance: complex  # сопротивление ВН (активное, реактивное)
    low_current: Optional[complex] = None  # ток в средней стороны
    power_losses: Optional[complex] = None  # потери в трансформаторе
    tr_rat_high_middle: Union[float, int]  # коэффициент трансформации с ВН на СН
    tr_rat_high_low: Union[float, int]  # коэффициент трансформации с ВН на НН

    @classmethod
    def from_dict(cls, dict_t3: Dict[str, Any], nodes: List[Node]) -> Self:
        """
        Конвертировать словаря входных данных трехобмоточного трансформатора
        :param nodes: список узлов
        :param dict_t3: словарь входных данных трехобмоточного трансформатора
        :return: экземпляр трехобмоточного трансформатора
        """
        fields_t3 = [
            "Node (HV)",
            "Node (LV)",
            "Node (MV)",
            "Type (Line, T2, T3)",
            ["High_impedance, Ohm", "Real", "Imaginary"],
            ["High_conductivity, S", "Real", "Imaginary"],
            ["Middle_impedance, Ohm", "Real", "Imaginary"],
            ["Low_impedance, Ohm", "Real", "Imaginary"],
            "Transformation ratio HV-MV",
            "Transformation ratio HV-LV"
        ]

        if presence_parameters(fields_t3, dict_t3):
            key_nodes = ["Node (HV)", "Node (MV)", "Node (LV)"]
            for node in nodes:
                for key_node in key_nodes:
                    if not isinstance(dict_t3[key_node], Node):
                        if dict_t3[key_node] == node.name:
                            dict_t3[key_node] = node

            type_branch = dict_t3["Type (Line, T2, T3)"]
            high = dict_t3["Node (HV)"]
            high_impedance = complex(
                dict_t3["High_impedance, Ohm"]["Real"], dict_t3["High_impedance, Ohm"]["Imaginary"]
            )
            high_conductivity = complex(
                dict_t3["High_conductivity, S"]["Real"], dict_t3["High_conductivity, S"]["Imaginary"]
            )
            middle = dict_t3["Node (MV)"]
            middle_impedance = complex(
                dict_t3["Middle_impedance, Ohm"]["Real"], dict_t3["Middle_impedance, Ohm"]["Imaginary"]
            )
            low = dict_t3["Node (LV)"]
            low_impedance = complex(
                dict_t3["Low_impedance, Ohm"]["Real"], dict_t3["Low_impedance, Ohm"]["Imaginary"]
            )
            tr_rat_high_middle = dict_t3["Transformation ratio HV-MV"]
            tr_rat_high_low = dict_t3["Transformation ratio HV-LV"]
            return cls(
                type_branch=type_branch,
                high=high,
                high_impedance=high_impedance,
                high_conductivity=high_conductivity,
                middle=middle,
                middle_impedance=middle_impedance,
                low=low,
                low_impedance=low_impedance,
                tr_rat_high_middle=tr_rat_high_middle,
                tr_rat_high_low=tr_rat_high_low,
            )
        else:
            raise KeyError

    def to_dict(self) -> Dict[str, Any]:
        """
        Представление данных трехобмоточного трансформатора в виде словаря
        :return: словарь трансформатора
        """
        high_current = None
        middle_current = None
        low_current = None
        real_power_losses = None
        imag_power_losses = None
        if isinstance(self.high_current, complex):
            high_current = abs(self.high_current) * 1000
        else:
            raise TypeError
        if isinstance(self.middle_current, complex):
            middle_current = abs(self.middle_current) * 1000
        else:
            raise TypeError
        if isinstance(self.low_current, complex):
            low_current = abs(self.low_current) * 1000
        else:
            raise TypeError
        if isinstance(self.power_losses, complex):
            real_power_losses = self.power_losses.real
            imag_power_losses = self.power_losses.imag
        else:
            raise TypeError
        return {
            "Type (Line, T2, T3)": self.type_branch,
            "Node (HV)": self.high.name,
            "Node (MV)": self.middle.name,
            "Node (LV)": self.low.name,
            "High impedance, Ohm": {"Real": self.high_impedance.real, "Imaginary": self.high_impedance.imag},
            "High conductivity, S": {"Real": self.high_conductivity.real, "Imaginary": self.high_conductivity.imag},
            "High current, A": high_current,
            "Middle impedance, Ohm": {"Real": self.middle_impedance.real, "Imaginary": self.middle_impedance.imag},
            "Middle current, A": middle_current,
            "Low impedance, Ohm": {"Real": self.low_impedance.real, "Imaginary": self.low_impedance.imag},
            "Low current, A": low_current,
            "Transformation ratio HV-MV": self.tr_rat_high_middle,
            "Transformation ratio HV-LV": self.tr_rat_high_low,
            "Power losses, MVA": {"Real": real_power_losses, "Imaginary": imag_power_losses},
        }

    def calculate_current_losses(self, nodes: List[Node], conductivity_matrix: np.ndarray) -> None:
        """
        Рассчитать ток в трехобмоточном трансформаторе и потери мощности
        :param nodes: список узлов
        :param conductivity_matrix: матрица собственных и взаимных проводимостей
        :return: None
        """
        try:
            high_node = nodes.index(self.high)
            middle_node = nodes.index(self.middle)
            low_node = nodes.index(self.low)
            i_hm = (self.high.voltage - self.middle.voltage) * conductivity_matrix[high_node, middle_node]
            i_hl = (self.high.voltage - self.low.voltage) * conductivity_matrix[high_node, low_node]
            i_ml = (self.middle.voltage - self.low.voltage) * conductivity_matrix[middle_node, low_node]
            i_h = i_hm + i_hl
            i_m = i_hm - i_ml
            i_l = i_hl + i_ml
            if isinstance(i_h, complex) and isinstance(i_m, complex) and isinstance(i_l, complex):
                self.high_current = i_h
                self.middle_current = i_m
                self.low_current = i_l
            s_h = self.high.voltage * self.high_current.conjugate() + self.high.voltage**2 * self.high_conductivity
            s_m = self.middle.voltage * (-self.middle_current).conjugate()
            s_l = self.low.voltage * (-self.low_current).conjugate()
            ds = s_h + s_m + s_l
            self.power_losses = ds
        except AttributeError:
            raise AttributeError

def presence_parameters(fields_branch: List[str], dict_branch: Dict[str, Any]) -> bool:
    """
    Проверить наличие ключа в словаре
    :param fields_branch: ключи для ветви
    :param dict_branch: словарь данных ветви
    :return:
    """
    for fb in fields_branch:
        if not isinstance(fb, list):
            if fb not in dict_branch:
                return False
        else:
            if fb[0] not in dict_branch and fb[1] not in dict_branch[fb[0]] and fb[2] not in dict_branch[fb[0]]:
                return False
    return True

def new_branch(dict_branch: Dict[str, Any], nodes: List[Node]) -> Line | Transformer2 | Transformer3:
    """
    Собрать новую ветвь по типу
    :param dict_branch: словарь ветви, проверяется ключ Type (LINE, T2, T3)
    :param nodes: список узлов
    :return: линия, т2, т3 или None
    """
    if "Type (Line, T2, T3)" not in dict_branch.keys():
        raise KeyError
    if dict_branch["Type (Line, T2, T3)"] not in ["Line", "T2", "T3"]:
        raise ValueError

    if dict_branch["Type (Line, T2, T3)"] == "Line":
        return Line.from_dict(dict_branch, nodes)
    elif dict_branch["Type (Line, T2, T3)"] == "T2":
        return Transformer2.from_dict(dict_branch, nodes)
    elif dict_branch["Type (Line, T2, T3)"] == "T3":
        return Transformer3.from_dict(dict_branch, nodes)
    else:
        raise KeyError
