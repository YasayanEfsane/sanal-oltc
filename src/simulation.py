import numpy as np
import pandas as pd
from typing import List, Dict, Any

from .models import TransformerModel, TransformerParams
from .controller import TapController, ControllerParams
from .scenarios import generate_voltage_scenario, generate_load_scenario

def run_simulation(
    transformer_params: TransformerParams,
    controller_params: ControllerParams,
    sim_time_s: float,
    dt_s: float,
    v_in_scenario_type: str,
    load_scenario_type: str,
    power_factor: float,
    is_inductive: bool
) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    
    time_array = np.arange(0, sim_time_s + dt_s, dt_s)
    
    # Pre-calculate scenarios
    v_in_pu_array = generate_voltage_scenario(v_in_scenario_type, time_array)
    load_pu_array = generate_load_scenario(load_scenario_type, time_array)
    
    # Models
    model_uncontrolled = TransformerModel(transformer_params)
    model_controlled = TransformerModel(transformer_params)
    controller = TapController(
        controller_params, 
        transformer_params.target_voltage_pu,
        transformer_params.tap_min,
        transformer_params.tap_max
    )
    
    results = []
    events = []
    
    for i, t in enumerate(time_array):
        v_in = v_in_pu_array[i]
        load = load_pu_array[i]
        
        # 1. Uncontrolled
        v_out_uncontrolled = model_uncontrolled.calculate_secondary_voltage_pu(
            v_in, 0, load, power_factor, is_inductive
        )
        
        # 2. Controlled
        current_tap = controller.current_tap
        v_out_controlled = model_controlled.calculate_secondary_voltage_pu(
            v_in, current_tap, load, power_factor, is_inductive
        )
        
        # Record pre-tap state for events
        v_out_pre_tap = v_out_controlled
        
        # Controller step
        new_tap, event = controller.step(dt_s, v_out_controlled)
        
        if event is not None:
            events.append({
                "Zaman (s)": round(t, 2),
                "Hareket Öncesi Gerilim (pu)": round(v_out_pre_tap, 4),
                "Hareket Nedeni": event,
                "Eski Kademe": current_tap,
                "Yeni Kademe": new_tap,
                "İşlem Sonucu": "Başarılı" if new_tap != current_tap else "Sınıra Ulaşıldı"
            })
            
        results.append({
            "Zaman (s)": t,
            "Giriş Gerilimi (pu)": v_in,
            "Yük (pu)": load,
            "Kontrolsüz Çıkış (pu)": v_out_uncontrolled,
            "Kontrollü Çıkış (pu)": v_out_controlled,
            "Kademe Konumu": new_tap,
            "Kontrolsüz Hata": v_out_uncontrolled - transformer_params.target_voltage_pu,
            "Kontrollü Hata": v_out_controlled - transformer_params.target_voltage_pu,
        })
        
    df_results = pd.DataFrame(results)
    df_events = pd.DataFrame(events) if events else pd.DataFrame(columns=[
        "Zaman (s)", "Hareket Öncesi Gerilim (pu)", "Hareket Nedeni", 
        "Eski Kademe", "Yeni Kademe", "İşlem Sonucu"
    ])
    
    return df_results, df_events, events
