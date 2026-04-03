import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DevelopmentCurveSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Development S-Curve Simulator")
        self.root.geometry("1100x700")

        # Variables for Phase 1
        self.p1_name = tk.StringVar(value="Pre-Production")
        self.p1_duration = tk.IntVar(value=12)
        self.p1_milestone = tk.IntVar(value=15)
        self.p1_curve = tk.DoubleVar(value=2.5) # Late blooming

        # Variables for Phase 2
        self.p2_name = tk.StringVar(value="Principal Photography")
        self.p2_duration = tk.IntVar(value=3)
        self.p2_milestone = tk.IntVar(value=80)
        self.p2_curve = tk.DoubleVar(value=1.0) # Linear

        # Variables for Phase 3
        self.p3_name = tk.StringVar(value="Post-Production")
        self.p3_duration = tk.IntVar(value=9)
        self.p3_curve = tk.DoubleVar(value=0.5) # Early blooming

        self.setup_ui()
        self.update_plot()

    def setup_ui(self):
        # Main layout frames
        control_frame = ttk.Frame(self.root, padding="10", width=350)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.plot_frame = ttk.Frame(self.root, padding="10")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Build Controls
        self.build_phase_controls(control_frame, "Phase 1", self.p1_name, self.p1_duration, self.p1_milestone, self.p1_curve, 1, 36)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        
        self.build_phase_controls(control_frame, "Phase 2", self.p2_name, self.p2_duration, self.p2_milestone, self.p2_curve, 1, 12)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Phase 3 (No milestone, it always ends at 100%)
        self.build_phase_controls(control_frame, "Phase 3", self.p3_name, self.p3_duration, None, self.p3_curve, 1, 24)
        
        # Save Button
        save_btn = ttk.Button(control_frame, text="Save Picture (PNG)", command=self.save_picture)
        save_btn.pack(pady=20, fill=tk.X)

        # Matplotlib Setup
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_phase_controls(self, parent, title, name_var, duration_var, milestone_var, curve_var, dur_min, dur_max):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.X, pady=5)

        # Name Input
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        entry = ttk.Entry(frame, textvariable=name_var)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self.update_plot())

        # Duration Slider
        ttk.Label(frame, text="Duration (Months):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=dur_min, to=dur_max, variable=duration_var, command=lambda e: self.update_plot()).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # Milestone Slider (If applicable)
        if milestone_var:
            ttk.Label(frame, text="End % Done:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Scale(frame, from_=5, to=95, variable=milestone_var, command=lambda e: self.update_plot()).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        # Curvature Slider
        ttk.Label(frame, text="Curvature:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=0.2, to=5.0, variable=curve_var, command=lambda e: self.update_plot()).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        
        frame.columnconfigure(1, weight=1)

    def generate_curve_segment(self, x_start, x_end, y_start, y_end, curve_shape, num_points=100):
        if x_start == x_end:
            return [x_start], [y_end]
        x_vals = np.linspace(x_start, x_end, num_points)
        # Normalize progress from 0.0 to 1.0
        progress_t = (x_vals - x_start) / (x_end - x_start)
        # Apply exponent for curvitude
        y_vals = y_start + (y_end - y_start) * (progress_t ** curve_shape)
        return x_vals, y_vals

    def update_plot(self):
        self.ax.clear()

        # Get current values
        d1, d2, d3 = self.p1_duration.get(), self.p2_duration.get(), self.p3_duration.get()
        m1, m2 = self.p1_milestone.get(), self.p2_milestone.get()
        c1, c2, c3 = self.p1_curve.get(), self.p2_curve.get(), self.p3_curve.get()

        # Prevent Phase 2 milestone from being lower than Phase 1
        if m2 <= m1:
            m2 = m1 + 1 
            self.p2_milestone.set(m2)

        # Calculate time bounds
        t0 = 0
        t1 = d1
        t2 = t1 + d2
        t3 = t2 + d3

        # Generate points for each phase
        x1, y1 = self.generate_curve_segment(t0, t1, 0, m1, c1)
        x2, y2 = self.generate_curve_segment(t1, t2, m1, m2, c2)
        x3, y3 = self.generate_curve_segment(t2, t3, m2, 100, c3)

        # Plot lines
        self.ax.plot(x1, y1, color='blue', linewidth=3)
        self.ax.plot(x2, y2, color='green', linewidth=3)
        self.ax.plot(x3, y3, color='purple', linewidth=3)

        # Shade background phases
        self.ax.axvspan(t0, t1, color='blue', alpha=0.1, label=self.p1_name.get())
        self.ax.axvspan(t1, t2, color='green', alpha=0.1, label=self.p2_name.get())
        self.ax.axvspan(t2, t3, color='purple', alpha=0.1, label=self.p3_name.get())

        # Formatting
        self.ax.set_title("Development S-Curve", fontsize=14, pad=15)
        self.ax.set_xlabel("Time (Months)", fontsize=12)
        self.ax.set_ylabel("Percentage Done (%)", fontsize=12)
        self.ax.set_xlim(0, t3)
        self.ax.set_ylim(0, 105) # Slight padding at top
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend(loc="upper left")

        # Mark important points
        self.ax.scatter([t1, t2, t3], [m1, m2, 100], color='red', zorder=5)

        self.canvas.draw()

    def save_picture(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Graph As..."
        )
        if file_path:
            try:
                self.fig.savefig(file_path, bbox_inches='tight')
                messagebox.showinfo("Success", f"Graph saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DevelopmentCurveSimulator(root)
    root.mainloop()
