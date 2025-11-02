from typing import Union, Dict, Any

from pydantic import ValidationError, BaseModel


class Branch(BaseModel):
    start: str                                      # имя стартового узла ветви
    end: str                                        # имя конечного узла ветви
    real_resistance: Union[float, int]              # активное сопротивление
    imaginary_resistance: Union[float, int]         # реактивное сопротивление
    real_conductivity: Union[float, int]            # активная проводимость
    imaginary_conductivity: Union[float, int]       # реактивная проводимость

    def __init__(self, branch: Dict[str, Any], **data: Any) -> None:
        for key in vars(self):
            if key not in branch:
                raise ValidationError
        branch.update(data)
        super().__init__(**branch)
