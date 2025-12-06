import pytest
from pydantic import ValidationError

from src.numerical_methods.newton_method.models.parameters import Parameters


def test_parameters(test_data):
    parameters = Parameters.from_dict(test_data["PARAMETERS"])

    # проверка инициализации
    assert parameters.nominal_voltage == 110
    assert parameters.accuracy == 0.001
    assert parameters.iterations == 100

    # отсутствуют данные
    parameters = {}
    with pytest.raises(KeyError):
        Parameters.from_dict(parameters)

    # неверный тип данных
    parameters = {
        "Nominal voltage, kV": 'text',
        "Accuracy": 0.001,
        "Max iterations": 100
    }
    with pytest.raises(ValidationError):
        Parameters.from_dict(parameters)