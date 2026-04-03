import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import numpy as np
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

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

        # Variables for Graph Settings
        self.graph_title = tk.StringVar(value="Development S-Curve")
        self.x_label = tk.StringVar(value="Time (Months)")
        self.y_label = tk.StringVar(value="Percentage Done (%)")
        self.pt1_label = tk.StringVar(value="Alpha")
        self.pt2_label = tk.StringVar(value="Beta")
        self.pt3_label = tk.StringVar(value="Release")
        self.show_x_ticks = tk.BooleanVar(value=True)

        self.active_setting_name = None
        self.clean_state_dict = None
        
        self.setup_ui()
        
        # Load default settings on startup
        self._load_default_settings()
        if self.clean_state_dict is None:
            self.clean_state_dict = self._get_current_settings_dict()
        
        self.update_plot()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        
        self.build_graph_settings(control_frame)
        
        # Settings Buttons
        load_conf_btn = ttk.Button(control_frame, text="Load Settings", command=self.load_settings_dialog)
        load_conf_btn.pack(pady=5, fill=tk.X)

        save_conf_btn = ttk.Button(control_frame, text="Save Settings", command=self.save_settings)
        save_conf_btn.pack(pady=5, fill=tk.X)

        # Save Button
        save_btn = ttk.Button(control_frame, text="Save Picture (PNG)", command=self.save_picture)
        save_btn.pack(pady=5, fill=tk.X)

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
        entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self.update_plot())

        # Duration Slider
        ttk.Label(frame, text="Duration (Months):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=dur_min, to=dur_max, variable=duration_var, command=lambda e, v=duration_var: (v.set(int(round(float(e)))), self.update_plot())).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        dur_entry = ttk.Entry(frame, textvariable=duration_var, width=5)
        dur_entry.grid(row=1, column=2, padx=5, pady=2)
        dur_entry.bind("<KeyRelease>", lambda e: self.update_plot())

        # Milestone Slider (If applicable)
        if milestone_var:
            ttk.Label(frame, text="End % Done:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Scale(frame, from_=5, to=95, variable=milestone_var, command=lambda e, v=milestone_var: (v.set(int(round(float(e)))), self.update_plot())).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
            mil_entry = ttk.Entry(frame, textvariable=milestone_var, width=5)
            mil_entry.grid(row=2, column=2, padx=5, pady=2)
            mil_entry.bind("<KeyRelease>", lambda e: self.update_plot())

        # Curvature Slider
        ttk.Label(frame, text="Curvature:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=0.2, to=5.0, variable=curve_var, command=lambda e: self.update_plot()).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        curv_entry = ttk.Entry(frame, textvariable=curve_var, width=5)
        curv_entry.grid(row=3, column=2, padx=5, pady=2)
        curv_entry.bind("<KeyRelease>", lambda e: self.update_plot())
        
        frame.columnconfigure(1, weight=1)

    def build_graph_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="Graph Settings")
        frame.pack(fill=tk.X, pady=5)
        
        settings = [
            ("Title:", self.graph_title),
            ("X-Axis:", self.x_label),
            ("Y-Axis:", self.y_label),
            ("Point 1 (P1 End):", self.pt1_label),
            ("Point 2 (P2 End):", self.pt2_label),
            ("Point 3 (End):", self.pt3_label)
        ]
        
        for i, (label_text, var) in enumerate(settings):
            ttk.Label(frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            entry.bind("<KeyRelease>", lambda e: self.update_plot())
            
        chk = ttk.Checkbutton(frame, text="Show Numbers on X Axis", variable=self.show_x_ticks, command=self.update_plot)
        chk.grid(row=len(settings), column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
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
        try:
            d1, d2, d3 = self.p1_duration.get(), self.p2_duration.get(), self.p3_duration.get()
            m1, m2 = self.p1_milestone.get(), self.p2_milestone.get()
            c1, c2, c3 = self.p1_curve.get(), self.p2_curve.get(), self.p3_curve.get()
        except tk.TclError:
            return  # Ignore updates if user temporarily inputs invalid letters/empty string

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
        self.ax.set_title(self.graph_title.get(), fontsize=14, pad=15)
        self.ax.set_xlabel(self.x_label.get(), fontsize=12)
        self.ax.set_ylabel(self.y_label.get(), fontsize=12)
        self.ax.set_xlim(0, t3)
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        if not self.show_x_ticks.get():
            self.ax.tick_params(axis='x', labelbottom=False)
        else:
            self.ax.tick_params(axis='x', labelbottom=True)
        self.ax.legend(loc="upper left")

        # Mark important points
        pts_x = [t1, t2, t3]
        pts_y = [m1, m2, 100]
        labels = [self.pt1_label.get(), self.pt2_label.get(), self.pt3_label.get()]
        
        self.ax.scatter(pts_x, pts_y, color='red', zorder=5)
        
        for i in range(3):
            if labels[i].strip():
                self.ax.annotate(labels[i], (pts_x[i], pts_y[i]), 
                                 textcoords="offset points", xytext=(0, 10), 
                                 ha='center', fontsize=10, color='red', weight='bold')

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

    def apply_settings(self, config, name=None):
        if "p1_name" in config: self.p1_name.set(config["p1_name"])
        if "p1_duration" in config: self.p1_duration.set(config["p1_duration"])
        if "p1_milestone" in config: self.p1_milestone.set(config["p1_milestone"])
        if "p1_curve" in config: self.p1_curve.set(config["p1_curve"])
        
        if "p2_name" in config: self.p2_name.set(config["p2_name"])
        if "p2_duration" in config: self.p2_duration.set(config["p2_duration"])
        if "p2_milestone" in config: self.p2_milestone.set(config["p2_milestone"])
        if "p2_curve" in config: self.p2_curve.set(config["p2_curve"])
        
        if "p3_name" in config: self.p3_name.set(config["p3_name"])
        if "p3_duration" in config: self.p3_duration.set(config["p3_duration"])
        if "p3_curve" in config: self.p3_curve.set(config["p3_curve"])
        
        if "graph_title" in config: self.graph_title.set(config["graph_title"])
        if "x_label" in config: self.x_label.set(config["x_label"])
        if "y_label" in config: self.y_label.set(config["y_label"])
        
        if "pt1_label" in config: self.pt1_label.set(config["pt1_label"])
        if "pt2_label" in config: self.pt2_label.set(config["pt2_label"])
        if "pt3_label" in config: self.pt3_label.set(config["pt3_label"])
        if "show_x_ticks" in config: self.show_x_ticks.set(config["show_x_ticks"])
        
        if "window_geometry" in config:
            try:
                self.root.geometry(config["window_geometry"])
            except Exception:
                pass
                
        self.update_plot()
        
        self.active_setting_name = name
        if name:
            self.root.title(f"Development S-Curve Simulator - [{name}]")
        else:
            self.root.title("Development S-Curve Simulator")
            
        self.clean_state_dict = self._get_current_settings_dict()

    def _load_default_settings(self):
        conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator.conf")
        if os.path.exists(conf_file):
            try:
                with open(conf_file, 'r') as f:
                    configs = json.load(f)
                if "default" in configs:
                    self.apply_settings(configs["default"], "default")
            except Exception:
                pass

    def load_settings_dialog(self):
        conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator.conf")
        if not os.path.exists(conf_file):
            messagebox.showinfo("Info", "No saved settings found (generator.conf missing).")
            return
            
        try:
            with open(conf_file, 'r') as f:
                configs = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read settings:\n{e}")
            return
            
        if not configs:
            messagebox.showinfo("Info", "No settings available in conf file.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load Settings")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select configuration to load:").pack(pady=10)

        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for name in configs.keys():
            listbox.insert(tk.END, name)

        def on_load():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a setting to load.", parent=dialog)
                return
            
            setting_name = listbox.get(selected[0])
            self.apply_settings(configs[setting_name], setting_name)
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Load", command=on_load).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, expand=True, padx=5)
        
        listbox.bind("<Double-Button-1>", lambda e: on_load())

    def _get_current_settings_dict(self):
        return {
            "p1_name": self.p1_name.get(),
            "p1_duration": self.p1_duration.get(),
            "p1_milestone": self.p1_milestone.get(),
            "p1_curve": self.p1_curve.get(),
            "p2_name": self.p2_name.get(),
            "p2_duration": self.p2_duration.get(),
            "p2_milestone": self.p2_milestone.get(),
            "p2_curve": self.p2_curve.get(),
            "p3_name": self.p3_name.get(),
            "p3_duration": self.p3_duration.get(),
            "p3_curve": self.p3_curve.get(),
            "graph_title": self.graph_title.get(),
            "x_label": self.x_label.get(),
            "y_label": self.y_label.get(),
            "pt1_label": self.pt1_label.get(),
            "pt2_label": self.pt2_label.get(),
            "pt3_label": self.pt3_label.get(),
            "show_x_ticks": self.show_x_ticks.get(),
            "window_geometry": self.root.geometry()
        }

    def save_settings(self):
        conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generator.conf")
        
        configs = {}
        if os.path.exists(conf_file):
            try:
                with open(conf_file, 'r') as f:
                    configs = json.load(f)
            except Exception:
                pass
                
        initial_name = self.active_setting_name if self.active_setting_name else ""
        while True:
            setting_name = simpledialog.askstring("Save Settings", "Enter name for this setting:", 
                                                  initialvalue=initial_name, parent=self.root)
            if setting_name is None: 
                return # user cancelled
                
            setting_name = setting_name.strip()
            if not setting_name:
                messagebox.showwarning("Warning", "Setting name cannot be empty.")
                continue

            if setting_name in configs:
                overwrite = messagebox.askyesno("Overwrite?", f"Setting '{setting_name}' already exists. Overwrite?")
                if not overwrite:
                    continue # Let them pick a different name
            
            try:
                configs[setting_name] = self._get_current_settings_dict()
                with open(conf_file, 'w') as f:
                    json.dump(configs, f, indent=4)
                messagebox.showinfo("Success", f"Setting '{setting_name}' saved successfully in generator.conf!")
                
                self.active_setting_name = setting_name
                self.root.title(f"Development S-Curve Simulator - [{setting_name}]")
                self.clean_state_dict = self._get_current_settings_dict()
                break
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings:\n{e}")
                break
                
    def is_dirty(self):
        if not hasattr(self, 'clean_state_dict') or not self.clean_state_dict:
            return False
        current = self._get_current_settings_dict()
        for k in current:
            if k == "window_geometry": continue # Ignore just geometry change for dirty prompting
            if current[k] != self.clean_state_dict.get(k):
                return True
        return False
        
    def on_closing(self):
        if self.is_dirty():
            ans = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before exiting?")
            if ans is True: # Yes
                self.save_settings()
                if not self.is_dirty(): # Meaning they actually saved it successfully
                    self.root.destroy()
            elif ans is False: # No
                self.root.destroy()
            # else ans is None (Cancel), stays open
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DevelopmentCurveSimulator(root)
    root.mainloop()
