import pytest
import numpy as np
from src.simulation import run_simulation
from src.models import TransformerParams
from src.controller import ControllerParams
from src.metrics import calculate_kpis

def test_simulation_controlled_better_than_uncontrolled():
    transformer_params = TransformerParams()
    controller_params = ControllerParams(deadband_percent=1.5, delay_time_s=2.0)
    
    df, _, _ = run_simulation(
        transformer_params,
        controller_params,
        sim_time_s=60.0,
        dt_s=0.1,
        v_in_scenario_type="Basamak",
        load_scenario_type="Sabit",
        power_factor=0.9,
        is_inductive=True
    )
    
    kpis = calculate_kpis(df, transformer_params.target_voltage_pu, controller_params.deadband_percent)
    
    assert kpis["controlled_mae"] < kpis["uncontrolled_mae"]
    assert kpis["improvement_percent"] > 0
    assert kpis["total_tap_changes"] > 0

def test_random_seed_reproducibility():
    transformer_params = TransformerParams()
    controller_params = ControllerParams()
    
    from src.scenarios import generate_voltage_scenario
    time_array = np.arange(0, 10, 0.1)
    
    v1 = generate_voltage_scenario("Rastgele", time_array, seed=10)
    v2 = generate_voltage_scenario("Rastgele", time_array, seed=10)
    v3 = generate_voltage_scenario("Rastgele", time_array, seed=20)
    
    np.testing.assert_array_equal(v1, v2)
    with pytest.raises(AssertionError):
        np.testing.assert_array_equal(v1, v3)
