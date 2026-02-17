
import tkinter as tk
from ipc_calc.gui import IPCHomeGUI

def main():
    root = tk.Tk()
    app = IPCHomeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
