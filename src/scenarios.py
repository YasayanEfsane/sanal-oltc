import numpy as np

def generate_voltage_scenario(
    scenario_type: str, 
    time_array: np.ndarray, 
    base_pu: float = 1.0, 
    seed: int = 42
) -> np.ndarray:
    if scenario_type == "Sabit":
        return np.ones_like(time_array) * base_pu
    elif scenario_type == "Basamak":
        v = np.ones_like(time_array) * base_pu
        v[(time_array >= 10) & (time_array < 30)] = 0.92
        v[(time_array >= 30) & (time_array < 45)] = 1.07
        v[time_array >= 45] = 0.98
        return v
    elif scenario_type == "Rampa":
        v = np.ones_like(time_array) * base_pu
        ramp_start = 10
        ramp_end = 50
        mask = (time_array >= ramp_start) & (time_array <= ramp_end)
        v[mask] = base_pu - 0.1 * (time_array[mask] - ramp_start) / (ramp_end - ramp_start)
        v[time_array > ramp_end] = base_pu - 0.1
        return v
    elif scenario_type == "Sinüzoidal":
        return base_pu + 0.1 * np.sin(2 * np.pi * time_array / 20.0)
    elif scenario_type == "Rastgele":
        np.random.seed(seed)
        noise = np.random.normal(0, 0.02, len(time_array))
        trend = np.cumsum(np.random.normal(0, 0.005, len(time_array)))
        return base_pu + noise + trend
    else:
        return np.ones_like(time_array) * base_pu

def generate_load_scenario(
    scenario_type: str, 
    time_array: np.ndarray, 
    base_pu: float = 0.8, 
    seed: int = 42
) -> np.ndarray:
    if scenario_type == "Sabit":
        return np.ones_like(time_array) * base_pu
    elif scenario_type == "Basamak":
        l = np.ones_like(time_array) * base_pu
        l[(time_array >= 20) & (time_array < 40)] = base_pu * 1.2
        return l
    elif scenario_type == "Rampa":
        l = np.ones_like(time_array) * base_pu
        ramp_start = 10
        ramp_end = 50
        mask = (time_array >= ramp_start) & (time_array <= ramp_end)
        l[mask] = base_pu + 0.2 * (time_array[mask] - ramp_start) / (ramp_end - ramp_start)
        l[time_array > ramp_end] = base_pu + 0.2
        return l
    elif scenario_type == "TEİAŞ Günlük (Ölçekli)":
        t_normalized = time_array / time_array[-1] * 24.0
        xp = [0, 6, 9, 17, 20, 24]
        yp = [0.4, 0.5, 0.85, 0.85, 1.1, 0.4]
        l = np.interp(t_normalized, xp, yp) * (base_pu / 0.85)
        return l
    elif scenario_type == "TEİAŞ + EV Şarj Şoku":
        t_normalized = time_array / time_array[-1] * 24.0
        xp = [0, 6, 9, 17, 20, 24]
        yp = [0.4, 0.5, 0.85, 0.85, 1.1, 0.4]
        base_load = np.interp(t_normalized, xp, yp) * (base_pu / 0.85)
        
        # Akşam 18:30 ile 22:30 arası EV şarj şoku
        ev_load = np.zeros_like(t_normalized)
        ev_mask = (t_normalized >= 18.5) & (t_normalized <= 22.5)
        # Çan eğrisi şeklinde büyük bir şarj yığılması
        ev_load[ev_mask] = 0.5 * np.sin((t_normalized[ev_mask] - 18.5) * np.pi / 4.0)
        
        return base_load + ev_load
    elif scenario_type == "Rastgele":
        np.random.seed(seed + 1)
        noise = np.random.normal(0, 0.05, len(time_array))
        return np.clip(base_pu + noise, 0.0, 1.5)
    else:
        return np.ones_like(time_array) * base_pu

def generate_solar_scenario(
    scenario_type: str, 
    time_array: np.ndarray, 
    peak_pu: float = 0.5
) -> np.ndarray:
    if scenario_type == "Yok":
        return np.zeros_like(time_array)
    elif scenario_type == "Bulutsuz Yaz Günü":
        t_normalized = time_array / time_array[-1] * 24.0
        solar = np.zeros_like(t_normalized)
        mask = (t_normalized > 6) & (t_normalized < 18)
        solar[mask] = peak_pu * np.sin((t_normalized[mask] - 6) * np.pi / 12)
        return solar
    elif scenario_type == "Parçalı Bulutlu":
        t_normalized = time_array / time_array[-1] * 24.0
        solar = np.zeros_like(t_normalized)
        mask = (t_normalized > 6) & (t_normalized < 18)
        base_solar = peak_pu * np.sin((t_normalized[mask] - 6) * np.pi / 12)
        np.random.seed(42)
        noise = np.random.uniform(0.4, 1.0, size=len(base_solar))
        solar[mask] = base_solar * noise
        return solar
    else:
        return np.zeros_like(time_array)
