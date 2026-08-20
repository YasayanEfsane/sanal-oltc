import math
from dataclasses import dataclass

@dataclass
class TransformerParams:
    nominal_power_kVA: float = 100.0
    nominal_primary_V: float = 34500.0
    nominal_secondary_V: float = 400.0
    frequency_Hz: float = 50.0
    r_pu: float = 0.01
    x_pu: float = 0.04
    target_voltage_pu: float = 1.00
    tap_min: int = -8
    tap_max: int = 8
    tap_step_pu: float = 0.0125

class TransformerModel:
    def __init__(self, params: TransformerParams):
        self.params = params

    def calculate_secondary_voltage_pu(
        self,
        vin_pu: float,
        tap_position: int,
        load_pu: float,
        power_factor: float,
        is_inductive: bool = True
    ) -> float:
        v, _ = self.calculate_parallel_secondary_voltage(
            vin_pu, tap_position, tap_position, load_pu / 2.0 if load_pu > 0 else 0, power_factor, is_inductive, is_single=True
        )
        return v

    def calculate_parallel_secondary_voltage(
        self,
        vin_pu: float,
        tap_position_1: int,
        tap_position_2: int,
        load_pu: float,
        power_factor: float,
        is_inductive: bool = True,
        is_single: bool = False
    ) -> tuple[float, float]:
        if vin_pu <= 0:
            return 0.0, 0.0

        tap_mult_1 = 1.0 + tap_position_1 * self.params.tap_step_pu
        tap_mult_2 = 1.0 + tap_position_2 * self.params.tap_step_pu
        v1 = vin_pu * tap_mult_1
        v2 = vin_pu * tap_mult_2
        
        v_s_eq = (v1 + v2) / 2.0
        
        z_mag = math.sqrt(self.params.r_pu**2 + self.params.x_pu**2)
        i_circ = abs(v1 - v2) / (2.0 * z_mag) if not is_single else 0.0
        
        if load_pu <= 0:
            return v_s_eq, i_circ
            
        p_pu = load_pu * power_factor
        q_pu = load_pu * math.sqrt(1.0 - power_factor**2)
        if not is_inductive:
            q_pu = -q_pu
            
        # If single, impedance is R, X. If parallel, it's R/2, X/2
        r_eq = self.params.r_pu if is_single else self.params.r_pu / 2.0
        x_eq = self.params.x_pu if is_single else self.params.x_pu / 2.0
        
        a = 1.0
        b = 2.0 * (p_pu * r_eq + q_pu * x_eq) - v_s_eq**2
        c = (p_pu**2 + q_pu**2) * (r_eq**2 + x_eq**2)
        
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            return 0.0, i_circ
            
        v_squared = (-b + math.sqrt(discriminant)) / 2.0
        if v_squared <= 0:
            return 0.0, i_circ
            
        return math.sqrt(v_squared), i_circ
