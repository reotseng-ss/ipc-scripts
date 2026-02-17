
import math

class IPC7351Engine:
    def __init__(self):
        self.F = 0.1
        self.P = 0.05
        
        # Fillet Tables (jt: Toe, jh: Heel, js: Side)
        self.fillet_tables = {
            "Gull-wing": {
                "A": {"jt": 0.55, "jh": 0.45, "js": 0.05, "excess": 0.5},
                "B": {"jt": 0.35, "jh": 0.35, "js": 0.03, "excess": 0.25},
                "C": {"jt": 0.15, "jh": 0.25, "js": 0.01, "excess": 0.1}
            },
            "Chip (>=0603)": {
                "A": {"jt": 0.55, "jh": -0.05, "js": 0.05, "excess": 0.5},
                "B": {"jt": 0.35, "jh": -0.05, "js": 0.00, "excess": 0.25},
                "C": {"jt": 0.15, "jh": -0.05, "js": -0.05, "excess": 0.1}
            }
        }

    def calculate_land_pattern(self, l_min, l_max, w_min, w_max, t_min, t_max, family, level):
        f = self.fillet_tables[family][level]
        c_l, c_w, c_t = (l_max - l_min), (w_max - w_min), (t_max - t_min)
        
        # Statistical RMS calculation
        s_min = l_min - (2 * t_max)
        s_tol_rms = math.sqrt(c_l**2 + 2 * c_t**2)
        s_max_rms = s_min + s_tol_rms
        
        # Z, G, X Formulas
        z = l_min + (2 * f['jt']) + math.sqrt(c_l**2 + self.F**2 + self.P**2)
        g = s_max_rms - (2 * f['jh']) - math.sqrt(s_tol_rms**2 + self.F**2 + self.P**2)
        x = w_min + (2 * f['js']) + math.sqrt(c_w**2 + self.F**2 + self.P**2)
        
        # Courtyard
        c_l_dim = math.ceil((max(z, l_max) + 2 * f['excess']) * 10) / 10
        c_w_dim = math.ceil((max(x, w_max) + 2 * f['excess']) * 10) / 10
        
        return {"Z": z, "G": g, "X": x, "CL": c_l_dim, "CW": c_w_dim}

    def calculate_bga(self, ball_diam):
        # BGA Reduction logic 
        reduction = 0.25 if ball_diam >= 0.75 else 0.20
        land = ball_diam * (1 - reduction)
        return {"Land": land, "CL": ball_diam + 1.0, "CW": ball_diam + 1.0}
