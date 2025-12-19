from typing import Any, Dict, Union

from pydantic import BaseModel, Field


class Parameters(BaseModel):
    """
    Класс представляющий параметры расчета
    """

    nominal_voltage: Union[float, int] = Field(gt=0, le=1000000)  # номинальное напряжение сети
    accuracy: Union[float, int] = Field(gt=0, le=1000000)  # точность расчета
    iterations: int = Field(gt=0, le=1000000)  # количество итераций

    @classmethod
    def from_dict(cls, dict_param: Dict[str, Any]) -> Any:
        """
        Конвертировать словаря входных данных параметров
        :param dict_param: словарь входных данных параметров
        :return: экземпляр узла
        """
        if "Nominal voltage, kV" in dict_param and "Accuracy" in dict_param and "Max iterations" in dict_param:
            nominal_voltage = dict_param["Nominal voltage, kV"]
            accuracy = dict_param["Accuracy"]
            iterations = dict_param["Max iterations"]
            return cls(nominal_voltage=nominal_voltage, accuracy=accuracy, iterations=iterations)
        else:
            raise KeyError
