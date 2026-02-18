
import math


class IPC7351Engine:
    def __init__(self):
        # p is "placement tolerance" and is defined by Fab House's assembly equipment
        self.defaults = {
            "Greatest_board_x_y_dim_up_to_300mm": {
                "A": {"F": 0.3, "P": 0.10},  # Preferred/General
                "B": {"F": 0.2, "P": 0.10},  # Nominal
                "C": {"F": 0.1, "P": 0.10}   # Reduced/Precision
            },
            "Greatest_board_x_y_dim_up_to_450mm": {
                "A": {"F": 0.35, "P": 0.10},  # Preferred/General
                "B": {"F": 0.25, "P": 0.10},  # Nominal
                "C": {"F": 0.15, "P": 0.10}   # Reduced/Precision
            },
            "Greatest_board_x_y_dim_up_to_600mm": {
                "A": {"F": 0.4, "P": 0.10},  # Preferred/General
                "B": {"F": 0.3, "P": 0.10},  # Nominal
                "C": {"F": 0.2, "P": 0.10}   # Reduced/Precision
            }
        }

        # Fillet Tables (jt: Toe, jh: Heel, js: Side)
        self.fillet_tables = {
            "Gull-wing": {
                "A": {"jt": 0.55, "jh": 0.45, "js": 0.01, "excess": 0.5},
                "B": {"jt": 0.35, "jh": 0.35, "js": -0.02, "excess": 0.25},
                "C": {"jt": 0.15, "jh": 0.25, "js": -0.04, "excess": 0.1}
            }
        }

    def _round_up(self, val, step):
        """Round UP to the nearest step (e.g., 0.20, 0.05, 0.01)."""
        # Using a small epsilon to avoid precision issues with ceil
        return math.ceil(round(val / step, 6)) * step

    def _courtyard_round(self, val):
        """Round UP to nearest 0.01mm as requested by the user."""
        return self._round_up(val, 0.01)

    def calculate_land_pattern(self, l_min, l_max, w_min, w_max, t_min, t_max, family, level_full, board_dim_mm):
        # Extract Level Letter (A, B, C)
        level = level_full[0] if level_full else "B"
        
        f_table = self.fillet_tables[family][level]
        defaults = self.defaults[board_dim_mm][level]

        print(f"DEBUG: Level={level}, BoardDim={board_dim_mm}")
        print(f"DEBUG: Defaults={defaults}")
        
        F = defaults["F"]
        P = defaults["P"]
        excess = f_table["excess"]
        
        c_l, c_w, c_t = (l_max - l_min), (w_max - w_min), (t_max - t_min)
        
        # Smin: Minimum dimension between opposing heels
        s_min = l_min - (2 * t_max)
        # Amax: Maximum lead span
        a_max = l_max
        # T1: Lead tolerance
        t1 = t_max - t_min

        # Heel Fillet (jh) Override for Gull-wing
        jh = f_table['jh']
        if family == "Gull-wing":
             if s_min <= a_max and t1 <= 0.5:
                 overrides = {"A": 0.25, "B": 0.15, "C": 0.05}
                 jh = overrides[level]

        # Statistical RMS calculation
        s_tol_rms = math.sqrt(c_l**2 + 2 * c_t**2)
        s_max_rms = s_min + s_tol_rms
        
        # Z, G, X Formulas
        raw_z = l_min + (2 * f_table['jt']) + math.sqrt(c_l**2 + F**2 + P**2)
        raw_g = s_max_rms - (2 * jh) - math.sqrt(s_tol_rms**2 + F**2 + P**2)
        raw_x = w_min + (2 * f_table['js']) + math.sqrt(c_w**2 + F**2 + P**2)
        
        # Feature Rounding
        # Toe (Z) & Heel (G): Nearest 0.20
        z = self._round_up(raw_z, 0.20)
        g = self._round_up(raw_g, 0.20)
        # Side (X): Nearest 0.05
        x = self._round_up(raw_x, 0.05)
        
        # Courtyard
        raw_cl = max(z, l_max) + (2 * excess)
        raw_cw = max(x, w_max) + (2 * excess)
        
        return {
            "Z": round(z, 2),
            "G": round(g, 2),
            "X": round(x, 2),
            "CL": self._courtyard_round(raw_cl),
            "CW": self._courtyard_round(raw_cw)
        }

    def calculate_pitch_verification(self, pitch_e, lead_w_min, lead_w_max, land_x, fab_f, place_p):
        """
        pitch_e: Nominal pitch between lead centers
        lead_w_min/max: Lead width dimensions
        land_x: Calculated land width (X)
        fab_f: Fabrication allowance
        place_p: Placement accuracy (True Position)
        """
        # Lead Width Tolerance (C)
        c_w = lead_w_max - lead_w_min
        
        # Statistical Tolerance Sum (RMS)
        # Applied to the width-wise variation
        tol_rms = math.sqrt(c_w**2 + fab_f**2 + place_p**2)
        
        # Equation for Attachment Overlap (M) [cite: 637]
        # M = ((W + X) / 2) - sqrt(C^2 + F^2 + P^2)
        m_overlap = ((lead_w_min + land_x) / 2.0) - tol_rms
        
        # Equation for Clearance Spacing (N) [cite: 637]
        # N = E - ((W + X) / 2) + sqrt(C^2 + F^2 + P^2)
        n_clearance = pitch_e - ((lead_w_min + land_x) / 2.0) + tol_rms
        
        return {
            "M_Overlap": round(m_overlap, 2),
            "N_Clearance": round(n_clearance, 2),
            "Density_Warning": n_clearance < 0.20 # High density threshold 
        }
    def calculate_bga(self, ball_diam):
        # BGA Reduction logic 
        reduction = 0.25 if ball_diam >= 0.75 else 0.20
        land = ball_diam * (1 - reduction)
        return {
            "Land": round(land, 2), 
            "CL": self._courtyard_round(ball_diam + 1.0), 
            "CW": self._courtyard_round(ball_diam + 1.0)
        }
