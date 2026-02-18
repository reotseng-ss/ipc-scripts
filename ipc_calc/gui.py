
import tkinter as tk
from tkinter import ttk, messagebox
from .engine import IPC7351Engine

class IPCHomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IPC-7351 Calculator")
        self.engine = IPC7351Engine()
        self.setup_ui()

    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="NSEW")

        # Tab 1: Land Pattern
        self.tab_land = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_land, text="Land Pattern")
        self.setup_land_tab(self.tab_land)

        # Tab 2: Pitch Analysis
        self.tab_pitch = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_pitch, text="Pitch Analysis")
        self.setup_pitch_tab(self.tab_pitch)

    def setup_land_tab(self, parent):
        # Configuration Section
        config_frame = ttk.LabelFrame(parent, text=" Configuration ", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky="EW", pady=(0, 10))

        ttk.Label(config_frame, text="Package Type:").grid(row=0, column=0, sticky="W")
        self.pkg_type = ttk.Combobox(config_frame, values=["Gull-wing", "BGA"], width=30)
        self.pkg_type.set("Gull-wing")
        self.pkg_type.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Density Level:").grid(row=1, column=0, sticky="W")
        self.level = ttk.Combobox(
            config_frame, 
            values=[
                "A (Maximum Protrusion)", 
                "B (Median Protrusion)", 
                "C (Minimum Protrusion)"
            ], 
            width=30
        )
        self.level.set("A (Maximum Protrusion)")
        self.level.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Board Size:").grid(row=2, column=0, sticky="W")
        self.board_dim = ttk.Combobox(
            config_frame, 
            values=[
                "Greatest_board_x_y_dim_up_to_300mm", 
                "Greatest_board_x_y_dim_up_to_450mm", 
                "Greatest_board_x_y_dim_up_to_600mm"
            ], 
            width=30
        )
        self.board_dim.set("Greatest_board_x_y_dim_up_to_300mm")
        self.board_dim.grid(row=2, column=1, padx=5, pady=5)

        # Dimensions Section
        dim_frame = ttk.LabelFrame(parent, text=" Component Dimensions (mm) ", padding="10")
        dim_frame.grid(row=2, column=0, columnspan=2, sticky="EW", pady=10)

        self.dim_labels = ["L Min", "L Max", "W Min", "W Max", "T Min", "T Max"]
        self.entries = {}
        for i, label in enumerate(self.dim_labels):
            row, col = divmod(i, 2)
            ttk.Label(dim_frame, text=f"{label}:").grid(row=row, column=col*2, sticky="W", padx=(5, 2))
            entry = ttk.Entry(dim_frame, width=10)
            entry.grid(row=row, column=col*2+1, padx=(0, 10), pady=5)
            self.entries[label] = entry

        ttk.Button(parent, text="Calculate Pattern", command=self.run_calc_land).grid(row=9, column=0, columnspan=2, pady=10)

        # Results Section
        res_frame = ttk.LabelFrame(parent, text=" Results ", padding="10")
        res_frame.grid(row=10, column=0, columnspan=2, sticky="NSEW", pady=5)

        self.res_text_land = tk.Text(res_frame, height=8, width=45, state="disabled", font=("Consolas", 10), background="#f8f8f8")
        self.res_text_land.grid(row=0, column=0, sticky="NSEW")

    def setup_pitch_tab(self, parent):
        # Description
        ttk.Label(parent, text="Verify lead-to-land spacing (IPC-7351B)").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Inputs
        input_frame = ttk.LabelFrame(parent, text=" Parameters (mm) ", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky="EW")

        labels = [
            ("Nominal Pitch (E)", "pitch"),
            ("Lead Width Min (Wmin)", "w_min"),
            ("Lead Width Max (Wmax)", "w_max"),
            ("Land Width (X)", "land_x"),
            ("Fab Tolerance (F)", "fab_f"),
            ("Place Tolerance (P)", "place_p")
        ]
        
        self.pitch_entries = {}
        for i, (text, key) in enumerate(labels):
            ttk.Label(input_frame, text=text + ":").grid(row=i, column=0, sticky="W", padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=15)
            # Set some defaults
            if key == "fab_f": entry.insert(0, "0.04") # IPC Class B approx
            if key == "place_p": entry.insert(0, "0.10") 
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.pitch_entries[key] = entry

        ttk.Button(parent, text="Verify Pitch", command=self.run_calc_pitch).grid(row=2, column=0, columnspan=2, pady=15)

        # Results
        res_frame = ttk.LabelFrame(parent, text=" Verification Results ", padding="10")
        res_frame.grid(row=3, column=0, columnspan=2, sticky="NSEW")

        self.res_text_pitch = tk.Text(res_frame, height=6, width=45, state="disabled", font=("Consolas", 10), background="#f8f8f8")
        self.res_text_pitch.grid(row=0, column=0, sticky="NSEW")

    def display_result(self, widget, text):
        widget.config(state="normal")
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")

    def run_calc_land(self):
        try:
            pkg = self.pkg_type.get()
            lvl = self.level.get()
            board_dim = self.board_dim.get()
            
            if pkg == "BGA":
                ball_text = self.entries["L Min"].get()
                if not ball_text:
                     messagebox.showwarning("Incomplete Data", "Please enter Ball Diameter (L Min) for BGA.")
                     return
                ball = float(ball_text)
                res = self.engine.calculate_bga(ball)
                output = f"BGA Land Diameter: {res['Land']:.2f} mm\nCourtyard: {res['CL']:.2f} x {res['CW']:.2f} mm"
            else:
                vals = []
                for k in self.dim_labels:
                    val_text = self.entries[k].get()
                    if not val_text:
                         messagebox.showwarning("Incomplete Data", f"Please enter a value for {k}.")
                         return
                    vals.append(float(val_text))
                
                res = self.engine.calculate_land_pattern(*vals, pkg, lvl, board_dim)
                output = (f"Land Pattern Dimensions:\n"
                          f"  Z (Outer): {res['Z']:.2f} mm\n"
                          f"  G (Inner): {res['G']:.2f} mm\n"
                          f"  X (Width): {res['X']:.2f} mm\n\n"
                          f"Courtyard: {res['CL']:.2f} x {res['CW']:.2f} mm")
            
            self.display_result(self.res_text_land, output)
        except ValueError:
            messagebox.showerror("Precision Error", "Please enter valid numeric dimensions.")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")

    def run_calc_pitch(self):
        try:
            # Gather inputs
            inputs = {}
            for key, entry in self.pitch_entries.items():
                val = entry.get()
                if not val:
                    messagebox.showwarning("Missing Input", f"Please enter a value for {key}")
                    return
                inputs[key] = float(val)

            # Map inputs to engine method args
            # pitch_e, lead_w_min, lead_w_max, land_x, fab_f, place_p
            res = self.engine.calculate_pitch_verification(
                pitch_e=inputs["pitch"],
                lead_w_min=inputs["w_min"],
                lead_w_max=inputs["w_max"],
                land_x=inputs["land_x"],
                fab_f=inputs["fab_f"],
                place_p=inputs["place_p"]
            )

            warn = "WARNING: HIGH DENSITY!" if res["Density_Warning"] else "OK"
            output = (f"Overlap (M):   {res['M_Overlap']:.2f} mm\n"
                      f"Clearance (N): {res['N_Clearance']:.2f} mm\n"
                      f"Status:        {warn}")
            
            self.display_result(self.res_text_pitch, output)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
