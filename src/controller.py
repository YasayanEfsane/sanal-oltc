from dataclasses import dataclass
from typing import Optional

@dataclass
class ControllerParams:
    deadband_percent: float = 1.5
    delay_time_s: float = 2.0
    min_time_between_taps_s: float = 1.0
    controller_type: str = "Geleneksel (Sabit Zamanlı)"

class TapController:
    def __init__(self, params: ControllerParams, target_pu: float, tap_min: int, tap_max: int):
        self.params = params
        self.target_v = target_pu
        self.tap_min = tap_min
        self.tap_max = tap_max
        
        self.current_tap = 0
        self.timer_s = 0.0
        self.timer_direction = 0 
        self.time_since_last_tap_s = params.min_time_between_taps_s 
        
        self.upper_limit = target_pu * (1.0 + params.deadband_percent / 100.0)
        self.lower_limit = target_pu * (1.0 - params.deadband_percent / 100.0)
        
        # Akıllı denetleyici için üstel hareketli ortalama (EMA) filtresi
        self.ema_voltage = target_pu

    def step(self, dt: float, v_out_pu: float) -> tuple[int, Optional[str]]:
        if self.params.controller_type == "Akıllı (EMA & Ters Zamanlı)":
            return self._step_smart(dt, v_out_pu)
        else:
            return self._step_traditional(dt, v_out_pu)

    def _step_traditional(self, dt: float, v_out_pu: float) -> tuple[int, Optional[str]]:
        self.time_since_last_tap_s += dt
        event = None
        
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
                            event = "Kademe üst sınırına ulaşıldı."
                    elif self.timer_direction == -1:
                        if self.current_tap > self.tap_min:
                            self.current_tap -= 1
                            event = "Yüksek gerilim nedeniyle kademe düşürüldü."
                            self.timer_s = 0.0
                            self.time_since_last_tap_s = 0.0
                        else:
                            event = "Kademe alt sınırına ulaşıldı."
                        
        return self.current_tap, event

    def _step_smart(self, dt: float, v_out_pu: float) -> tuple[int, Optional[str]]:
        self.time_since_last_tap_s += dt
        event = None
        
        # 1. EMA (Üstel Hareketli Ortalama) Filtresi: Anlık gürültüleri (transient) görmezden gel
        alpha = dt / (0.5 + dt) # 0.5 saniyelik zaman sabiti
        self.ema_voltage = self.ema_voltage * (1 - alpha) + v_out_pu * alpha
        v_eval = self.ema_voltage
        
        error = v_eval - self.target_v
        error_percent = abs(error) * 100.0
        
        # 2. Ters Zamanlı (IDMT) Gecikme Algoritması
        if error_percent > self.params.deadband_percent:
            over_error = error_percent - self.params.deadband_percent
            
            # Hata ne kadar büyükse, bekleme süresi o kadar KISALIR! (Akıllı karar)
            # Kritik: dynamic_delay sabit delay_time_s'den başlar ve aşağı düşer
            dynamic_delay = self.params.delay_time_s / (1.0 + 3.0 * over_error)
            dynamic_delay = max(dynamic_delay, self.params.min_time_between_taps_s)
            
            new_direction = -1 if error > 0 else 1
        else:
            new_direction = 0
            dynamic_delay = self.params.delay_time_s
            
        if new_direction == 0:
            self.timer_s = 0.0
            self.timer_direction = 0
        else:
            if self.timer_direction == new_direction:
                self.timer_s += dt
            else:
                self.timer_direction = new_direction
                self.timer_s = dt
                
            epsilon = 1e-6
            if self.timer_s >= dynamic_delay - epsilon:
                if self.time_since_last_tap_s >= self.params.min_time_between_taps_s - epsilon:
                    if self.timer_direction == 1:
                        if self.current_tap < self.tap_max:
                            self.current_tap += 1
                            event = "Düşük gerilim (Akıllı Müdahale) nedeniyle kademe artırıldı."
                            self.timer_s = 0.0
                            self.time_since_last_tap_s = 0.0
                        else:
                            event = "Kademe üst sınırına ulaşıldı."
                    elif self.timer_direction == -1:
                        if self.current_tap > self.tap_min:
                            self.current_tap -= 1
                            event = "Yüksek gerilim (Akıllı Müdahale) nedeniyle kademe düşürüldü."
                            self.timer_s = 0.0
                            self.time_since_last_tap_s = 0.0
                        else:
                            event = "Kademe alt sınırına ulaşıldı."
                        
        return self.current_tap, event
