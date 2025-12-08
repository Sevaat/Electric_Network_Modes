import pytest

from src.numerical_methods.newton_method.models.parameters import Parameters


def test_parameters_valid_creation():
    """Тест создания валидного объекта Parameters"""
    params = Parameters(
        nominal_voltage=110.0,
        accuracy=0.01,
        iterations=1000
    )
    assert params.nominal_voltage == 110.0
    assert params.accuracy == 0.01
    assert params.iterations == 1000

def test_parameters_voltage_boundary_min():
    """Тест граничного значения напряжения (минимум)"""
    with pytest.raises(ValueError):
        Parameters(
            nominal_voltage=0,  # gt=0, не допускается
            accuracy=0.01,
            iterations=1000
        )

def test_parameters_voltage_boundary_max():
    """Тест граничного значения напряжения (максимум)"""
    params = Parameters(
        nominal_voltage=1000000,  # le=1000000, допускается
        accuracy=0.01,
        iterations=1000
    )
    assert params.nominal_voltage == 1000000

def test_parameters_voltage_exceeds_max():
    """Тест превышения максимума напряжения"""
    with pytest.raises(ValueError):
        Parameters(
            nominal_voltage=1000001,  # превышает максимум
            accuracy=0.01,
            iterations=1000
        )

def test_parameters_accuracy_boundary():
    """Тест граничных значений точности"""
    params = Parameters(
        nominal_voltage=110.0,
        accuracy=1000000,  # максимальное значение
        iterations=1000
    )
    assert params.accuracy == 1000000

def test_parameters_iterations_negative():
    """Тест отрицательного количества итераций"""
    with pytest.raises(ValueError):
        Parameters(
            nominal_voltage=110.0,
            accuracy=0.01,
            iterations=-1  # gt=0
        )

def test_parameters_from_dict_valid():
    """Тест создания Parameters из словаря с корректными данными"""
    dict_params = {
        "Nominal voltage, kV": 110.0,
        "Accuracy": 0.001,
        "Max iterations": 5000
    }
    params = Parameters.from_dict(dict_params)
    assert params.nominal_voltage == 110.0
    assert params.accuracy == 0.001
    assert params.iterations == 5000

def test_parameters_from_dict_missing_key():
    """Тест создания Parameters из неполного словаря"""
    dict_params = {
        "Nominal voltage, kV": 110.0,
        "Accuracy": 0.001
        # Missing "Max iterations"
    }
    with pytest.raises(KeyError):
        Parameters.from_dict(dict_params)

def test_parameters_from_dict_empty():
    """Тест создания Parameters из пустого словаря"""
    with pytest.raises(KeyError):
        Parameters.from_dict({})

def test_parameters_int_voltage():
    """Тест использования целочисленного напряжения"""
    params = Parameters(
        nominal_voltage=230,  # int вместо float
        accuracy=0.001,
        iterations=1000
    )
    assert isinstance(params.nominal_voltage, int)
    assert params.nominal_voltage == 230