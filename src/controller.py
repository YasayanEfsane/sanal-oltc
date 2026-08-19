from dataclasses import dataclass
from typing import Optional

@dataclass
class ControllerParams:
    deadband_percent: float = 1.5
    delay_time_s: float = 2.0
    min_time_between_taps_s: float = 1.0
    
class TapController:
    def __init__(self, params: ControllerParams, target_pu: float, tap_min: int, tap_max: int):
        self.params = params
        self.target_pu = target_pu
        self.tap_min = tap_min
        self.tap_max = tap_max
        
        self.deadband_pu = self.params.deadband_percent / 100.0
        self.upper_limit = self.target_pu + self.deadband_pu
        self.lower_limit = self.target_pu - self.deadband_pu
        
        self.timer_s: float = 0.0
        self.time_since_last_tap_s: float = self.params.min_time_between_taps_s
        self.current_tap: int = 0
        self.timer_direction: int = 0

    def step(self, dt: float, v_out_pu: float) -> tuple[int, Optional[str]]:
        self.time_since_last_tap_s += dt
        event: Optional[str] = None
        
        if v_out_pu > self.upper_limit:
            new_direction = -1
        elif v_out_pu < self.lower_limit:
            new_direction = 1
        else:
            new_direction = 0
            
        if new_direction == 0:
            self.timer_s = 0.0
            self.timer_direction = 0
        else:
            if self.timer_direction == new_direction:
                self.timer_s += dt
            else:
                self.timer_direction = new_direction
                self.timer_s = dt
                
            # Use a tiny epsilon for float comparison
            epsilon = 1e-6
            if self.timer_s >= self.params.delay_time_s - epsilon:
                if self.time_since_last_tap_s >= self.params.min_time_between_taps_s - epsilon:
                    if self.timer_direction == 1:
                        if self.current_tap < self.tap_max:
                            self.current_tap += 1
                            event = "Düşük gerilim nedeniyle kademe artırıldı."
                            self.timer_s = 0.0
                            self.time_since_last_tap_s = 0.0
                        else:
                            if self.current_tap == self.tap_max:
                                event = "Kademe üst sınırına ulaşıldı."
                            self.timer_s = 0.0
                    elif self.timer_direction == -1:
                        if self.current_tap > self.tap_min:
                            self.current_tap -= 1
                            event = "Yüksek gerilim nedeniyle kademe düşürüldü."
                            self.timer_s = 0.0
                            self.time_since_last_tap_s = 0.0
                        else:
                            if self.current_tap == self.tap_min:
                                event = "Kademe alt sınırına ulaşıldı."
                            self.timer_s = 0.0
                            
        return self.current_tap, event
