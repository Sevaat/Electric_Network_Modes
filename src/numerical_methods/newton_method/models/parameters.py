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