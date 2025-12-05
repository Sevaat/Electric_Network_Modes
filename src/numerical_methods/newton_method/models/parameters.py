from typing import Union, Dict, Any

from pydantic import BaseModel, Field, ValidationError


class Parameters(BaseModel):
    nominal_voltage: Union[float, int] = Field(gt=0, le=1000000)            # номинальное напряжение сети
    accuracy: Union[float, int] = Field(gt=0, le=1000000)                   # точность расчета
    iterations: int = Field(gt=0, le=1000000)                               # количество итераций

    def __init__(self, parameters: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in parameters:
                raise ValidationError
        parameters.update(data)
        super().__init__(**parameters)

    @classmethod
    def conv_from_dict(cls, input_dict_param: Dict[str, Any]) -> Any:
        """
        Конвертация словаря входных данных
        :param input_dict_param: словарь входных данных параметров
        :return: экземпляр параметров
        """
        new_dict_param = {'nominal_voltage': input_dict_param['Nominal voltage, kV'],
                          'accuracy': input_dict_param['Accuracy'],
                          'iterations': input_dict_param['Max iterations']}
        return cls(new_dict_param)