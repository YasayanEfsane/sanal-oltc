import pytest
import math
from src.models import TransformerModel, TransformerParams

def test_transformer_voltage_drop_inductive():
    params = TransformerParams(r_pu=0.01, x_pu=0.04)
    model = TransformerModel(params)
    
    # Vin = 1.0, Tap = 0, P=0, Q=0
    v_out_no_load = model.calculate_secondary_voltage_pu(1.0, 0, 0.0, 0.0)
    assert v_out_no_load == 1.0
    
    # Load = 0.8, PF = 0.9 Inductive
    p = 0.8 * 0.9
    q = 0.8 * math.sqrt(1 - 0.9**2)
    v_out_load = model.calculate_secondary_voltage_pu(1.0, 0, p, q)
    assert v_out_load < 1.0
    
def test_transformer_voltage_drop_capacitive():
    params = TransformerParams(r_pu=0.01, x_pu=0.04)
    model = TransformerModel(params)
    
    p = 0.8 * 0.9
    q_ind = 0.8 * math.sqrt(1 - 0.9**2)
    q_cap = -q_ind
    
    v_out_load_ind = model.calculate_secondary_voltage_pu(1.0, 0, p, q_ind)
    v_out_load_cap = model.calculate_secondary_voltage_pu(1.0, 0, p, q_cap)
    
    assert v_out_load_cap > v_out_load_ind
    
def test_transformer_tap_changes():
    params = TransformerParams(tap_step_pu=0.0125)
    model = TransformerModel(params)
    
    v_out_tap0 = model.calculate_secondary_voltage_pu(1.0, 0, 0.0, 0.0)
    v_out_tap1 = model.calculate_secondary_voltage_pu(1.0, 1, 0.0, 0.0)
    v_out_tap_minus1 = model.calculate_secondary_voltage_pu(1.0, -1, 0.0, 0.0)
    
    assert v_out_tap1 == 1.0125
    assert v_out_tap_minus1 == 0.9875
    
def test_invalid_parameters():
    params = TransformerParams()
    model = TransformerModel(params)
    
    assert model.calculate_secondary_voltage_pu(0.0, 0, 1.0, 0.0) == 0.0
    assert model.calculate_secondary_voltage_pu(-1.0, 0, 1.0, 0.0) == 0.0
