import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MonteCarloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monte Carlo Cycle Time Simulator")

        self.cycle_times = None

        self.num_backlog = tk.IntVar(value=10)
        self.num_sims = tk.IntVar(value=10000)
        self.sample_size = tk.IntVar(value=1000)

        self.percentiles = {
            "P50": tk.BooleanVar(value=True),
            "P80": tk.BooleanVar(value=False),
            "P85": tk.BooleanVar(value=False),
            "P90": tk.BooleanVar(value=False),
        }

        self.canvas = None
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Upload Excel/CSV
        ttk.Button(frm, text="📁 Upload Excel/CSV", command=self.load_excel).grid(row=0, column=0, sticky="w")
        self.lbl_file = ttk.Label(frm, text="No file loaded")
        self.lbl_file.grid(row=0, column=1, sticky="w")

        # N Backlog
        ttk.Label(frm, text="Number of backlog items (N):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.num_backlog).grid(row=1, column=1, sticky="w")

        # Simulations
        ttk.Label(frm, text="Simulations (10k - 30k):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.num_sims).grid(row=2, column=1, sticky="w")

        # Sample size input
        ttk.Label(frm, text="Cycle time history to use (last N rows):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.sample_size).grid(row=3, column=1, sticky="w")

        # Percentiles
        pct_frame = ttk.LabelFrame(frm, text="Select Percentiles")
        pct_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        for i, (label, var) in enumerate(self.percentiles.items()):
            ttk.Checkbutton(pct_frame, text=label, variable=var).grid(row=0, column=i, sticky="w", padx=5)

        # Run + Help Buttons
        ttk.Button(frm, text="▶️ Run Simulation", command=self.run_simulation).grid(row=5, column=0, pady=10, sticky="w")
        ttk.Button(frm, text="ℹ️ How Monte Carlo Works", command=self.show_help).grid(row=5, column=1, pady=10, sticky="e")

        # Output Table (Treeview)
        columns = ["Position"] + list(self.percentiles.keys())
        self.tree = ttk.Treeview(frm, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        self.tree.grid(row=6, column=0, columnspan=2, pady=10)

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Excel or CSV files", "*.xls *.xlsx *.csv"),
            ("Excel files", "*.xls *.xlsx"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ])
        if not path:
            return

        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)

            numeric = df.select_dtypes(include=[np.number])
            if numeric.empty:
                messagebox.showerror("Error", "No numeric columns found.")
                return

            self.cycle_times = numeric.iloc[:, 0].dropna().values
            self.lbl_file.config(text=f"Loaded: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def run_simulation(self):
        if self.cycle_times is None:
            messagebox.showwarning("No file", "Please upload an Excel or CSV file first.")
            return

        N = self.num_backlog.get()
        sims = self.num_sims.get()
        hist_n = self.sample_size.get()

        if N <= 0 or not (10000 <= sims <= 30000):
            messagebox.showerror("Error", "Invalid N or simulation count.")
            return

        history = self.cycle_times[-hist_n:] if hist_n < len(self.cycle_times) else self.cycle_times
        if len(history) < N:
            messagebox.showerror("Error", f"Not enough data in selected history size ({len(history)}) for N={N}")
            return

        sim_matrix = np.zeros((sims, N))
        for i in range(sims):
            sample = np.random.choice(history, size=N, replace=True)
            sim_matrix[i] = np.cumsum(sample)

        requested_pcts = [int(p[1:]) for p, var in self.percentiles.items() if var.get()]
        headers = ["Position"] + [f"P{p}" for p in requested_pcts]

        # Clear old table
        for row in self.tree.get_children():
            self.tree.delete(row)

        plot_data = {f"P{p}": [] for p in requested_pcts}

        for pos in range(N):
            row = [pos + 1]
            for p in requested_pcts:
                val = np.percentile(sim_matrix[:, pos], p)
                row.append(f"{val:.2f}")
                plot_data[f"P{p}"].append(val)
            self.tree.insert("", "end", values=row)

        # Plot
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        positions = list(range(1, N + 1))
        for label, values in plot_data.items():
            ax.plot(positions, values, label=label)

        ax.set_title("Forecasted Delivery Time per Backlog Position")
        ax.set_xlabel("Backlog Position")
        ax.set_ylabel("Days")
        ax.legend()
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, pady=10)

    def show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("How Monte Carlo Simulation Works")
        help_win.geometry("650x500")

        text = tk.Text(help_win, wrap="word", font=("Segoe UI", 10))
        text.pack(expand=True, fill="both", padx=10, pady=10)

        explanation = """
📊 Monte Carlo Simulation for Delivery Forecasting

What it's for:
This app predicts the time it will take to deliver each item in your backlog based on historical cycle time data.

How it works:
1. You upload past cycle times from a CSV/Excel file.
2. You choose how many backlog positions you want to forecast (N).
3. For each simulation:
   - It randomly picks N cycle times from history.
   - It sums them cumulatively to simulate sequential delivery.
     For example:
         Sample:     [6, 8, 7, 5, 9]
         Cumulative: [6, 14, 21, 26, 35]
4. It runs this 10,000–30,000 times.
5. For each backlog position (1 to N), it calculates percentiles:
   - P50: Median delivery time
   - P80: 80% confidence the item is done by this time
   - P90: Even safer forecast

How to read the results:
• Position 1 → P80 = 7.3 → 80% chance it’ll be done within 7.3 days
• Position 5 → P90 = 35.1 → 90% chance first 5 items are done within 35.1 days

Use this to forecast sprints, release plans, or SLA confidence!
"""
        text.insert("1.0", explanation)
        text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonteCarloApp(root)
    root.mainloop()
