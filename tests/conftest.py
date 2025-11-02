import pytest


@pytest.fixture
def test_data():
    return {
        "nodes": [
            {
                "name": "1",
                "type_node": "ИП",
                "real_power": 0,
                "imaginary_power": 0,
                "real_voltage": 115,
                "imaginary_voltage": 0
            },
            {
                "name": "2",
                "type_node": "ИПО",
                "real_power": 28.8675,
                "imaginary_power": 17.3205,
                "real_voltage": 110,
                "imaginary_voltage": 0
            },
            {
                "name": "3",
                "type_node": "НАГР",
                "real_power": 46.188,
                "imaginary_power": 23.094,
                "real_voltage": 110,
                "imaginary_voltage": 0
            }
        ],
        "branches": [
            {
                "start": "1",
                "end": "2",
                "real_resistance": 10,
                "imaginary_resistance": 20,
                "real_conductivity": 0,
                "imaginary_conductivity": 0
            },
            {
                "start": "1",
                "end": "3",
                "real_resistance": 15,
                "imaginary_resistance": 30,
                "real_conductivity": 0,
                "imaginary_conductivity": 0
            },
            {
                "start": "2",
                "end": "3",
                "real_resistance": 10,
                "imaginary_resistance": 25,
                "real_conductivity": 0,
                "imaginary_conductivity": 0
            }
        ],
        "parameters": {
            "nominal_voltage": 110,
            "accuracy": 0.001,
            "iterations": 100
        }
    }
