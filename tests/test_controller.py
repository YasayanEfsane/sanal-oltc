import pytest
from src.controller import TapController, ControllerParams

def test_controller_increases_tap_on_low_voltage():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=2.0, min_time_between_taps_s=1.0)
    controller = TapController(params, target_pu=1.0, tap_min=-8, tap_max=8)
    
    # Voltage drops below deadband (0.985 limit, say 0.98)
    _, event = controller.step(1.0, 0.98)
    assert event is None
    assert controller.current_tap == 0
    
    # 2 seconds elapsed
    tap, event = controller.step(1.0, 0.98)
    assert event == "Düşük gerilim nedeniyle kademe artırıldı."
    assert tap == 1
    assert controller.current_tap == 1

def test_controller_decreases_tap_on_high_voltage():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=2.0, min_time_between_taps_s=1.0)
    controller = TapController(params, target_pu=1.0, tap_min=-8, tap_max=8)
    
    # Voltage goes above deadband (1.015 limit, say 1.02)
    _, event = controller.step(1.0, 1.02)
    assert event is None
    assert controller.current_tap == 0
    
    # 2 seconds elapsed
    tap, event = controller.step(1.0, 1.02)
    assert event == "Yüksek gerilim nedeniyle kademe düşürüldü."
    assert tap == -1
    assert controller.current_tap == -1

def test_controller_no_change_in_deadband():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=2.0, min_time_between_taps_s=1.0)
    controller = TapController(params, target_pu=1.0, tap_min=-8, tap_max=8)
    
    # Voltage within deadband (0.985 - 1.015)
    for _ in range(5):
        tap, event = controller.step(1.0, 1.01)
        assert event is None
        assert tap == 0
        
def test_controller_timer_resets_if_voltage_returns_to_normal():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=2.0, min_time_between_taps_s=1.0)
    controller = TapController(params, target_pu=1.0, tap_min=-8, tap_max=8)
    
    # Low voltage for 1s
    controller.step(1.0, 0.98)
    assert controller.timer_s == 1.0
    
    # Voltage normalizes
    controller.step(1.0, 1.00)
    assert controller.timer_s == 0.0
    
    # Low voltage again for 1s, total 2s but non-consecutive
    tap, event = controller.step(1.0, 0.98)
    assert controller.timer_s == 1.0
    assert event is None
    assert tap == 0

def test_controller_minimum_time_between_taps():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=1.0, min_time_between_taps_s=5.0)
    controller = TapController(params, target_pu=1.0, tap_min=-8, tap_max=8)
    
    # Step 1s: delay reached, min time (initially met) allows tap
    tap, event = controller.step(1.0, 0.98)
    assert tap == 1
    
    # Step another 1s: delay reached again (because still low), but min time (5s) not met
    tap, event = controller.step(1.0, 0.98)
    assert tap == 1 # unchanged
    assert event is None
    
    # Step 4s more: min time met
    tap, event = controller.step(4.0, 0.98)
    assert tap == 2
    
def test_controller_limits():
    params = ControllerParams(deadband_percent=1.5, delay_time_s=1.0, min_time_between_taps_s=1.0)
    controller = TapController(params, target_pu=1.0, tap_min=-1, tap_max=1) # tight limits
    
    # Tap up to max
    controller.step(1.0, 0.98)
    assert controller.current_tap == 1
    
    # Try to tap up again
    tap, event = controller.step(1.0, 0.98)
    assert tap == 1
    assert event == "Kademe üst sınırına ulaşıldı."
    
    # Return to normal then low again
    controller.step(1.0, 1.00)
    tap, event = controller.step(1.0, 0.98)
    assert tap == 1
    assert event == "Kademe üst sınırına ulaşıldı."
