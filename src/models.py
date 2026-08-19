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
        """
        Calculates the secondary voltage in per-unit using an exact quadratic solution
        for the voltage drop across the transformer's equivalent impedance.
        """
        if vin_pu <= 0:
            return 0.0

        # Tap multiplier (positive tap increases secondary voltage)
        tap_multiplier = 1.0 + tap_position * self.params.tap_step_pu
        vs_pu = vin_pu * tap_multiplier
        
        if load_pu <= 0:
            return vs_pu
            
        # P and Q in per-unit
        p_pu = load_pu * power_factor
        q_pu = load_pu * math.sqrt(1.0 - power_factor**2)
        if not is_inductive:
            q_pu = -q_pu # Capacitive load provides reactive power
            
        r = self.params.r_pu
        x = self.params.x_pu
        
        # Solving the exact quadratic equation for v = V_out_pu^2
        # v^2 + (2(PR + QX) - Vs^2)v + (P^2 + Q^2)(R^2 + X^2) = 0
        a = 1.0
        b = 2.0 * (p_pu * r + q_pu * x) - vs_pu**2
        c = (p_pu**2 + q_pu**2) * (r**2 + x**2)
        
        discriminant = b**2 - 4 * a * c
        
        if discriminant < 0:
            return 0.0
            
        v_squared = (-b + math.sqrt(discriminant)) / 2.0
        
        if v_squared <= 0:
            return 0.0
            
        return math.sqrt(v_squared)
