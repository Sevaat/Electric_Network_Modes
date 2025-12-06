import pytest


@pytest.fixture
def test_data():
    return {
        "NODES": [
            {
                "Name": "1",
                "Node type (L, S, LS)": "S",
                "Power, MVA": {'Real': 0, 'Imaginary': 0 },
                "Voltage, kV": { 'Real': 115, 'Imaginary': 0 }
            },
            {
                "Name": "2",
                "Node type (L, S, LS)": "LS",
                "Power, MVA": {'Real': 28.8675, 'Imaginary': 17.3205},
                "Voltage, kV": {'Real': 110, 'Imaginary': 0}
            },
            {
                "Name": "3",
                "Node type (L, S, LS)": "L",
                "Power, MVA": {'Real': 46.188, 'Imaginary': 23.094},
                "Voltage, kV": {'Real': 110, 'Imaginary': 0}
            }
        ],
        "BRANCHES": [
            {
                "Type (LINE, T2, T3)": "Line",
                "Node (start)": "1",
                "Node (end)": "2",
                "Impedance, Ohm": {'Real': 10, "Imaginary": 20},
                "Conductivity, S": {'Real': 0, "Imaginary": 0}
            },
            {
                "Type (LINE, T2, T3)": "Line",
                "Node (start)": "1",
                "Node (end)": "3",
                "Impedance, Ohm": {'Real': 15, "Imaginary": 30},
                "Conductivity, S": {'Real': 0, "Imaginary": 0}
            },
            {
                "Type (LINE, T2, T3)": "Line",
                "Node (start)": "2",
                "Node (end)": "3",
                "Impedance, Ohm": {'Real': 10, "Imaginary": 25},
                "Conductivity, S": {'Real': 0, "Imaginary": 0}
            }
        ],
        "PARAMETERS": {
            "Nominal voltage, kV": 110,
            "Accuracy": 0.001,
            "Max iterations": 100
        }
    }
