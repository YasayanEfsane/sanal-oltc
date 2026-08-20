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
    is_inductive: bool,
    parallel_mode: str = "Tek Trafo"
) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    
    time_array = np.arange(0, sim_time_s + dt_s, dt_s)
    
    v_in_pu_array = generate_voltage_scenario(v_in_scenario_type, time_array)
    load_pu_array = generate_load_scenario(load_scenario_type, time_array)
    
    model_uncontrolled = TransformerModel(transformer_params)
    model_controlled = TransformerModel(transformer_params)
    
    controller1 = TapController(
        controller_params, 
        transformer_params.target_voltage_pu,
        transformer_params.tap_min,
        transformer_params.tap_max
    )
    
    # Second controller with slight delay offset to simulate independent unsynchronized relays
    c2_params = ControllerParams(
        deadband_percent=controller_params.deadband_percent,
        delay_time_s=controller_params.delay_time_s + 0.1,
        min_time_between_taps_s=controller_params.min_time_between_taps_s
    )
    controller2 = TapController(
        c2_params, 
        transformer_params.target_voltage_pu,
        transformer_params.tap_min,
        transformer_params.tap_max
    )
    
    results = []
    events = []
    
    for i, t in enumerate(time_array):
        v_in = v_in_pu_array[i]
        load = load_pu_array[i]
        
        if parallel_mode == "Tek Trafo":
            v_out_unc = model_uncontrolled.calculate_secondary_voltage_pu(v_in, 0, load, power_factor, is_inductive)
            v_out_ctrl = model_controlled.calculate_secondary_voltage_pu(v_in, controller1.current_tap, load, power_factor, is_inductive)
            i_circ = 0.0
            
            v_out_pre = v_out_ctrl
            tap1, ev1 = controller1.step(dt_s, v_out_ctrl)
            tap2 = tap1
            if ev1:
                events.append({"Zaman (s)": round(t, 2), "Trafo": "T1", "Hareket Öncesi (pu)": round(v_out_pre,4), "Hareket Nedeni": ev1, "Eski Kademe": controller1.current_tap - (1 if 'artırıldı' in ev1 else (-1 if 'düşürüldü' in ev1 else 0)), "Yeni Kademe": tap1, "Sonuç": "Başarılı" if ev1.startswith(("D", "Y")) else "Sınır"})
                
        else:
            v_out_unc, _ = model_uncontrolled.calculate_parallel_secondary_voltage(v_in, 0, 0, load, power_factor, is_inductive)
            v_out_ctrl, i_circ = model_controlled.calculate_parallel_secondary_voltage(v_in, controller1.current_tap, controller2.current_tap, load, power_factor, is_inductive)
            
            v_out_pre = v_out_ctrl
            tap1, ev1 = controller1.step(dt_s, v_out_ctrl)
            if ev1:
                events.append({"Zaman (s)": round(t, 2), "Trafo": "T1", "Hareket Öncesi (pu)": round(v_out_pre,4), "Hareket Nedeni": ev1, "Eski Kademe": controller1.current_tap - (1 if 'artırıldı' in ev1 else (-1 if 'düşürüldü' in ev1 else 0)), "Yeni Kademe": tap1, "Sonuç": "Başarılı" if ev1.startswith(("D", "Y")) else "Sınır"})
            
            if parallel_mode == "Bağımsız Paralel":
                tap2, ev2 = controller2.step(dt_s, v_out_ctrl)
                if ev2:
                    events.append({"Zaman (s)": round(t, 2), "Trafo": "T2", "Hareket Öncesi (pu)": round(v_out_pre,4), "Hareket Nedeni": ev2, "Eski Kademe": controller2.current_tap - (1 if 'artırıldı' in ev2 else (-1 if 'düşürüldü' in ev2 else 0)), "Yeni Kademe": tap2, "Sonuç": "Başarılı" if ev2.startswith(("D", "Y")) else "Sınır"})
            elif parallel_mode == "Lider-Takipçi Paralel":
                controller2.current_tap = tap1
                tap2 = tap1
        
        results.append({
            "Zaman (s)": t,
            "Giriş Gerilimi (pu)": v_in,
            "Yük (pu)": load,
            "Kontrolsüz Çıkış (pu)": v_out_unc,
            "Kontrollü Çıkış (pu)": v_out_ctrl,
            "Kademe 1": tap1,
            "Kademe 2": tap2,
            "Sirkülasyon Akımı (pu)": i_circ,
            "Kontrolsüz Hata": v_out_unc - transformer_params.target_voltage_pu,
            "Kontrollü Hata": v_out_ctrl - transformer_params.target_voltage_pu,
        })
        
    df_results = pd.DataFrame(results)
    df_events = pd.DataFrame(events) if events else pd.DataFrame(columns=[
        "Zaman (s)", "Trafo", "Hareket Öncesi (pu)", "Hareket Nedeni", 
        "Eski Kademe", "Yeni Kademe", "Sonuç"
    ])
    
    return df_results, df_events, events
