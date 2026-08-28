import pandas as pd
import numpy as np

def calculate_kpis(df: pd.DataFrame, target_pu: float, deadband_percent: float, cost_per_tap: float = 0.5):
    uncontrolled_max_dev = df["Kontrolsüz Hata"].abs().max()
    controlled_max_dev = df["Kontrollü Hata"].abs().max()
    
    uncontrolled_mae = df["Kontrolsüz Hata"].abs().mean()
    controlled_mae = df["Kontrollü Hata"].abs().mean()
    
    improvement_percent = 0.0
    if uncontrolled_mae > 0:
        improvement_percent = ((uncontrolled_mae - controlled_mae) / uncontrolled_mae) * 100.0
        
    tap_diff1 = df["Kademe 1"].diff().fillna(0)
    tap_diff2 = df["Kademe 2"].diff().fillna(0)
    total_tap_changes = (tap_diff1 != 0).sum() + (tap_diff2 != 0).sum()
    total_wear_cost = total_tap_changes * cost_per_tap
    
    dt = df["Zaman (s)"].diff().mean()
    if np.isnan(dt): dt = 0
    
    deadband_pu = deadband_percent / 100.0
    out_of_deadband_mask = df["Kontrollü Hata"].abs() > deadband_pu
    time_out_of_deadband = out_of_deadband_mask.sum() * dt
    
    min_v_out = df["Kontrollü Çıkış (pu)"].min()
    max_v_out = df["Kontrollü Çıkış (pu)"].max()
    max_i_circ = df["Sirkülasyon Akımı (pu)"].max() if "Sirkülasyon Akımı (pu)" in df.columns else 0.0
    
    return {
        "uncontrolled_max_dev": float(uncontrolled_max_dev),
        "controlled_max_dev": float(controlled_max_dev),
        "uncontrolled_mae": float(uncontrolled_mae),
        "controlled_mae": float(controlled_mae),
        "improvement_percent": float(improvement_percent),
        "total_tap_changes": int(total_tap_changes),
        "total_wear_cost": float(total_wear_cost),
        "time_out_of_deadband": float(time_out_of_deadband),
        "min_v_out": float(min_v_out),
        "max_v_out": float(max_v_out),
        "max_i_circ": float(max_i_circ)
    }
