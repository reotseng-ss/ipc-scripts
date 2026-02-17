
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
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Inputs
        ttk.Label(main_frame, text="Package Type:").grid(row=0, column=0, sticky="W")
        self.pkg_type = ttk.Combobox(main_frame, values=["Gull-wing", "Chip (>=0603)", "BGA"])
        self.pkg_type.set("Gull-wing")
        self.pkg_type.grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Density Level:").grid(row=1, column=0, sticky="W")
        self.level = ttk.Combobox(main_frame, values=["A", "B", "C"])
        self.level.set("A")
        self.level.grid(row=1, column=1, pady=5)

        # Dimensions
        self.dim_labels = ["L Min", "L Max", "W Min", "W Max", "T Min", "T Max"]
        self.entries = {}
        for i, label in enumerate(self.dim_labels):
            ttk.Label(main_frame, text=f"{label} (mm):").grid(row=i+2, column=0, sticky="W")
            entry = ttk.Entry(main_frame)
            entry.grid(row=i+2, column=1, pady=2)
            self.entries[label] = entry

        ttk.Button(main_frame, text="Calculate", command=self.run_calc).grid(row=9, column=0, columnspan=2, pady=10)

        # Results
        self.res_text = tk.Text(main_frame, height=8, width=40, state="disabled", background="#f0f0f0")
        self.res_text.grid(row=10, column=0, columnspan=2)

    def run_calc(self):
        try:
            pkg = self.pkg_type.get()
            lvl = self.level.get()
            
            if pkg == "BGA":
                ball_text = self.entries["L Min"].get()
                if not ball_text:
                     messagebox.showerror("Input Error", "Please enter L Min (Ball Diameter) for BGA.")
                     return
                ball = float(ball_text)
                res = self.engine.calculate_bga(ball)
                output = f"BGA Land Diameter: {res['Land']:.2f} mm\nCourtyard: {res['CL']:.2f} x {res['CW']:.2f} mm"
            else:
                vals = []
                for k in self.dim_labels:
                    val_text = self.entries[k].get()
                    if not val_text:
                         messagebox.showerror("Input Error", f"Please enter a value for {k}.")
                         return
                    vals.append(float(val_text))
                
                res = self.engine.calculate_land_pattern(*vals, pkg, lvl)
                output = (f"Z (Outer): {res['Z']:.2f} mm\n"
                          f"G (Inner): {res['G']:.2f} mm\n"
                          f"X (Width): {res['X']:.2f} mm\n"
                          f"Courtyard: {res['CL']:.2f} x {res['CW']:.2f} mm")
            
            self.display_result(output)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric dimensions.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_result(self, text):
        self.res_text.config(state="normal")
        self.res_text.delete(1.0, tk.END)
        self.res_text.insert(tk.END, text)
        self.res_text.config(state="disabled")
