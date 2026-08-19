import pytest
from src.models import TransformerModel, TransformerParams

def test_transformer_voltage_drop_inductive():
    params = TransformerParams(r_pu=0.01, x_pu=0.04)
    model = TransformerModel(params)
    
    # Vin = 1.0, Tap = 0, Load = 0 -> Vout = 1.0
    v_out_no_load = model.calculate_secondary_voltage_pu(1.0, 0, 0.0, 1.0)
    assert v_out_no_load == 1.0
    
    # Vin = 1.0, Tap = 0, Load = 0.8, PF = 0.9 Inductive
    v_out_load = model.calculate_secondary_voltage_pu(1.0, 0, 0.8, 0.9, is_inductive=True)
    assert v_out_load < 1.0 # Should be voltage drop
    
def test_transformer_voltage_drop_capacitive():
    params = TransformerParams(r_pu=0.01, x_pu=0.04)
    model = TransformerModel(params)
    
    # Vin = 1.0, Tap = 0, Load = 0.8, PF = 0.9 Capacitive
    v_out_load_ind = model.calculate_secondary_voltage_pu(1.0, 0, 0.8, 0.9, is_inductive=True)
    v_out_load_cap = model.calculate_secondary_voltage_pu(1.0, 0, 0.8, 0.9, is_inductive=False)
    
    # Capacitive load increases voltage compared to inductive
    assert v_out_load_cap > v_out_load_ind
    
def test_transformer_tap_changes():
    params = TransformerParams(tap_step_pu=0.0125)
    model = TransformerModel(params)
    
    v_out_tap0 = model.calculate_secondary_voltage_pu(1.0, 0, 0.0, 1.0)
    v_out_tap1 = model.calculate_secondary_voltage_pu(1.0, 1, 0.0, 1.0)
    v_out_tap_minus1 = model.calculate_secondary_voltage_pu(1.0, -1, 0.0, 1.0)
    
    assert v_out_tap1 == 1.0125
    assert v_out_tap_minus1 == 0.9875
    
def test_invalid_parameters():
    params = TransformerParams()
    model = TransformerModel(params)
    
    assert model.calculate_secondary_voltage_pu(0.0, 0, 1.0, 1.0) == 0.0
    assert model.calculate_secondary_voltage_pu(-1.0, 0, 1.0, 1.0) == 0.0
