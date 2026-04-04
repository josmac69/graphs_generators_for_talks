import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
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
        self.p2_show = tk.BooleanVar(value=True)
        self.p2_name = tk.StringVar(value="Principal Photography")
        self.p2_duration = tk.IntVar(value=3)
        self.p2_milestone = tk.IntVar(value=80)
        self.p2_curve = tk.DoubleVar(value=1.0) # Linear

        # Variables for Phase 3
        self.p3_show = tk.BooleanVar(value=True)
        self.p3_name = tk.StringVar(value="Post-Production")
        self.p3_duration = tk.IntVar(value=9)
        self.p3_milestone = tk.IntVar(value=95)
        self.p3_curve = tk.DoubleVar(value=0.5) # Early blooming

        # Variables for Phase 4
        self.p4_show = tk.BooleanVar(value=False)
        self.p4_name = tk.StringVar(value="Phase 4")
        self.p4_duration = tk.IntVar(value=6)
        self.p4_milestone = tk.IntVar(value=98)
        self.p4_curve = tk.DoubleVar(value=1.0) 

        # Variables for Phase 5
        self.p5_show = tk.BooleanVar(value=False)
        self.p5_name = tk.StringVar(value="Phase 5")
        self.p5_duration = tk.IntVar(value=6)
        self.p5_curve = tk.DoubleVar(value=1.0) 

        # Variables for Graph Settings
        self.graph_title = tk.StringVar(value="Development S-Curve")
        self.x_label = tk.StringVar(value="Time (Months)")
        self.y_label = tk.StringVar(value="Percentage Done (%)")
        self.pt1_label = tk.StringVar(value="Alpha")
        self.pt2_label = tk.StringVar(value="Beta")
        self.pt3_label = tk.StringVar(value="Release")
        self.pt4_label = tk.StringVar(value="")
        self.pt5_label = tk.StringVar(value="")
        self.show_x_ticks = tk.BooleanVar(value=True)

        # Variables for Text Styling
        self.style_fonts = {
            "title": tk.StringVar(value="sans-serif"),
            "axes": tk.StringVar(value="sans-serif"),
            "ticks": tk.StringVar(value="sans-serif"),
            "legend": tk.StringVar(value="sans-serif"),
            "annot": tk.StringVar(value="sans-serif")
        }
        self.style_sizes = {
            "title": tk.IntVar(value=14),
            "axes": tk.IntVar(value=12),
            "ticks": tk.IntVar(value=10),
            "legend": tk.IntVar(value=10),
            "annot": tk.IntVar(value=10)
        }
        self.style_colors = {
            "title": tk.StringVar(value="#000000"),
            "axes": tk.StringVar(value="#000000"),
            "ticks": tk.StringVar(value="#000000"),
            "legend": tk.StringVar(value="#000000"),
            "annot": tk.StringVar(value="#ff0000")
        }

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
        left_container = ttk.Frame(self.root, width=370)
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)
        
        self.left_canvas = tk.Canvas(left_container, highlightthickness=0)
        self.left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.left_canvas.yview)
        
        self.left_panel = ttk.Frame(self.left_canvas, padding="10")
        
        self.left_panel.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(
                scrollregion=self.left_canvas.bbox("all")
            )
        )
        
        self.canvas_window = self.left_canvas.create_window((0, 0), window=self.left_panel, anchor="nw")
        
        self.left_canvas.bind(
            '<Configure>', 
            lambda e: self.left_canvas.itemconfig(self.canvas_window, width=e.width)
        )
        
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)
        
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            if hasattr(event, 'num') and event.num == 5 or event.delta < 0:
                self.left_canvas.yview_scroll(1, "units")
            elif hasattr(event, 'num') and event.num == 4 or event.delta > 0:
                self.left_canvas.yview_scroll(-1, "units")

        def _bind_mouse_wheel(event):
            self.left_canvas.bind_all("<Button-4>", _on_mousewheel)
            self.left_canvas.bind_all("<Button-5>", _on_mousewheel)
            self.left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mouse_wheel(event):
            self.left_canvas.unbind_all("<Button-4>")
            self.left_canvas.unbind_all("<Button-5>")
            self.left_canvas.unbind_all("<MouseWheel>")

        self.left_canvas.bind("<Enter>", _bind_mouse_wheel)
        self.left_canvas.bind("<Leave>", _unbind_mouse_wheel)
        
        self.plot_frame = ttk.Frame(self.root, padding="10")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.left_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        tab_phases = ttk.Frame(self.notebook, padding=5)
        tab_labels = ttk.Frame(self.notebook, padding=5)
        tab_style = ttk.Frame(self.notebook, padding=5)

        self.notebook.add(tab_phases, text="Phases")
        self.notebook.add(tab_labels, text="Labels")
        self.notebook.add(tab_style, text="Styling")

        # Build Controls in Tabs
        self.build_phase_controls(tab_phases, "Phase 1", self.p1_name, self.p1_duration, self.p1_milestone, self.p1_curve, 1, 36)
        ttk.Separator(tab_phases, orient='horizontal').pack(fill='x', pady=5)
        self.build_phase_controls(tab_phases, "Phase 2", self.p2_name, self.p2_duration, self.p2_milestone, self.p2_curve, 1, 12, self.p2_show)
        ttk.Separator(tab_phases, orient='horizontal').pack(fill='x', pady=5)
        self.build_phase_controls(tab_phases, "Phase 3", self.p3_name, self.p3_duration, self.p3_milestone, self.p3_curve, 1, 24, self.p3_show)
        ttk.Separator(tab_phases, orient='horizontal').pack(fill='x', pady=5)
        self.build_phase_controls(tab_phases, "Phase 4", self.p4_name, self.p4_duration, self.p4_milestone, self.p4_curve, 1, 24, self.p4_show)
        ttk.Separator(tab_phases, orient='horizontal').pack(fill='x', pady=5)
        self.build_phase_controls(tab_phases, "Phase 5", self.p5_name, self.p5_duration, None, self.p5_curve, 1, 24, self.p5_show)
        
        self.build_graph_settings(tab_labels)
        self.build_styling_controls(tab_style)
        
        # Action Buttons frame at bottom
        action_frame = ttk.Frame(self.left_panel)
        action_frame.pack(fill=tk.X, pady=10)

        load_conf_btn = ttk.Button(action_frame, text="Load Settings", command=self.load_settings_dialog)
        load_conf_btn.pack(pady=2, fill=tk.X)

        save_conf_btn = ttk.Button(action_frame, text="Save Settings", command=self.save_settings)
        save_conf_btn.pack(pady=2, fill=tk.X)

        save_btn = ttk.Button(action_frame, text="Save Picture (PNG)", command=self.save_picture)
        save_btn.pack(pady=2, fill=tk.X)

        # Matplotlib Setup
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_phase_controls(self, parent, title, name_var, duration_var, milestone_var, curve_var, dur_min, dur_max, show_var=None):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.X, pady=5)

        row_idx = 0
        if show_var is not None:
            ttk.Checkbutton(frame, text="Show Phase", variable=show_var, command=self.update_plot).grid(row=row_idx, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
            row_idx += 1

        # Name Input
        ttk.Label(frame, text="Name:").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        entry = ttk.Entry(frame, textvariable=name_var)
        entry.grid(row=row_idx, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self.update_plot())
        row_idx += 1

        # Duration Slider
        ttk.Label(frame, text="Duration (Months):").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=dur_min, to=dur_max, variable=duration_var, command=lambda e, v=duration_var: (v.set(int(round(float(e)))), self.update_plot())).grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
        dur_entry = ttk.Entry(frame, textvariable=duration_var, width=5)
        dur_entry.grid(row=row_idx, column=2, padx=5, pady=2)
        dur_entry.bind("<KeyRelease>", lambda e: self.update_plot())
        row_idx += 1

        # Milestone Slider (If applicable)
        if milestone_var:
            ttk.Label(frame, text="End % Done:").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Scale(frame, from_=5, to=95, variable=milestone_var, command=lambda e, v=milestone_var: (v.set(int(round(float(e)))), self.update_plot())).grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
            mil_entry = ttk.Entry(frame, textvariable=milestone_var, width=5)
            mil_entry.grid(row=row_idx, column=2, padx=5, pady=2)
            mil_entry.bind("<KeyRelease>", lambda e: self.update_plot())
            row_idx += 1

        # Curvature Slider
        ttk.Label(frame, text="Curvature:").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(frame, from_=0.2, to=5.0, variable=curve_var, command=lambda e: self.update_plot()).grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
        curv_entry = ttk.Entry(frame, textvariable=curve_var, width=5)
        curv_entry.grid(row=row_idx, column=2, padx=5, pady=2)
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
            ("Point 3:", self.pt3_label),
            ("Point 4:", self.pt4_label),
            ("Point 5:", self.pt5_label)
        ]
        
        for i, (label_text, var) in enumerate(settings):
            ttk.Label(frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            entry.bind("<KeyRelease>", lambda e: self.update_plot())
            
        chk = ttk.Checkbutton(frame, text="Show Numbers on X Axis", variable=self.show_x_ticks, command=self.update_plot)
        chk.grid(row=len(settings), column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
        frame.columnconfigure(1, weight=1)

    def build_styling_controls(self, parent):
        fonts = ["sans-serif", "serif", "monospace", "Arial", "Times New Roman", "Courier New", "Comic Sans MS"]
        groups = [
            ("Main Title", "title"),
            ("Axes Labels", "axes"),
            ("Tick Numbers", "ticks"),
            ("Legend", "legend"),
            ("Annotations", "annot")
        ]
        
        self.color_buttons = {}
        for name, key in groups:
            frame = ttk.LabelFrame(parent, text=name)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text="Font:").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
            font_cb = ttk.Combobox(frame, textvariable=self.style_fonts[key], values=fonts, width=12)
            font_cb.grid(row=0, column=1, padx=2, pady=2)
            font_cb.bind("<<ComboboxSelected>>", lambda e: self.update_plot())
            font_cb.bind("<KeyRelease>", lambda e: self.update_plot())
            
            ttk.Label(frame, text="Size:").grid(row=0, column=2, sticky=tk.W, padx=2, pady=2)
            size_spin = ttk.Spinbox(frame, from_=6, to=40, textvariable=self.style_sizes[key], width=3, command=self.update_plot)
            size_spin.grid(row=0, column=3, padx=2, pady=2)
            size_spin.bind("<KeyRelease>", lambda e: self.update_plot())
            
            color_btn = tk.Button(frame, text="Pick Color", bg=self.style_colors[key].get())
            def set_color(k=key, b=color_btn):
                code = colorchooser.askcolor(title=f"Choose {k} color", initialcolor=self.style_colors[k].get())[1]
                if code:
                    self.style_colors[k].set(code)
                    b.config(bg=code)
                    self.update_plot()
            color_btn.config(command=set_color)
            color_btn.grid(row=1, column=0, columnspan=4, sticky=tk.EW, padx=2, pady=2)
            self.color_buttons[key] = color_btn

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
            phases = [
                (self.p1_duration.get(), self.p1_name.get(), self.p1_milestone.get(), self.p1_curve.get(), True, self.pt1_label.get()),
                (self.p2_duration.get(), self.p2_name.get(), self.p2_milestone.get(), self.p2_curve.get(), self.p2_show.get(), self.pt2_label.get()),
                (self.p3_duration.get(), self.p3_name.get(), self.p3_milestone.get(), self.p3_curve.get(), self.p3_show.get(), self.pt3_label.get()),
                (self.p4_duration.get(), self.p4_name.get(), self.p4_milestone.get(), self.p4_curve.get(), self.p4_show.get(), self.pt4_label.get()),
                (self.p5_duration.get(), self.p5_name.get(), 100, self.p5_curve.get(), self.p5_show.get(), self.pt5_label.get())
            ]
        except tk.TclError:
            return  # Ignore updates if user temporarily inputs invalid letters/empty string

        active_phases = [p for p in phases if p[4]]
        if not active_phases:
            return

        # Dynamically set the last phase's milestone to 100
        last_idx = len(active_phases) - 1
        last_p = active_phases[last_idx]
        active_phases[last_idx] = (last_p[0], last_p[1], 100, last_p[3], last_p[4], last_p[5])

        # Enforce progressive milestones
        for i in range(1, len(active_phases)):
            prev_m = active_phases[i-1][2]
            curr_m = active_phases[i][2]
            if curr_m <= prev_m:
               curr_m = prev_m + 1
               if i < len(active_phases) - 1:
                   active_phases[i] = (active_phases[i][0], active_phases[i][1], curr_m, active_phases[i][3], active_phases[i][4], active_phases[i][5])

        colors = ['blue', 'green', 'purple', 'orange', 'red']
        
        t_curr = 0
        m_curr = 0
        
        self.pts_x = []
        self.pts_y = []
        self.labels = []

        for i, (p_dur, p_name, p_mil, p_curv, p_show, p_label) in enumerate(active_phases):
            t_next = t_curr + p_dur
            m_next = p_mil
            
            x, y = self.generate_curve_segment(t_curr, t_next, m_curr, m_next, p_curv)
            self.ax.plot(x, y, color=colors[i % len(colors)], linewidth=3)
            self.ax.axvspan(t_curr, t_next, color=colors[i % len(colors)], alpha=0.1, label=p_name)
            
            self.pts_x.append(t_next)
            self.pts_y.append(m_next)
            self.labels.append(p_label)
            
            t_curr = t_next
            m_curr = m_next

        t_total = t_curr

        # Formatting
        self.ax.set_title(self.graph_title.get(), 
                          fontsize=self.style_sizes["title"].get(), 
                          fontfamily=self.style_fonts["title"].get(), 
                          color=self.style_colors["title"].get(), pad=15)
                          
        self.ax.set_xlabel(self.x_label.get(), 
                           fontsize=self.style_sizes["axes"].get(), 
                           fontfamily=self.style_fonts["axes"].get(), 
                           color=self.style_colors["axes"].get())
                           
        self.ax.set_ylabel(self.y_label.get(), 
                           fontsize=self.style_sizes["axes"].get(), 
                           fontfamily=self.style_fonts["axes"].get(), 
                           color=self.style_colors["axes"].get())
                           
        self.ax.set_xlim(0, t_total)
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        tick_fontsize = self.style_sizes["ticks"].get()
        tick_fontfamily = self.style_fonts["ticks"].get()
        tick_color = self.style_colors["ticks"].get()

        self.ax.tick_params(axis='both', labelsize=tick_fontsize, labelcolor=tick_color)
        if not self.show_x_ticks.get():
            self.ax.tick_params(axis='x', labelbottom=False)

        for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            label.set_fontfamily(tick_fontfamily)

        leg = self.ax.legend(loc="upper left", prop={'family': self.style_fonts["legend"].get(), 'size': self.style_sizes["legend"].get()})
        if leg:
            for text in leg.get_texts():
                text.set_color(self.style_colors["legend"].get())

        # Mark important points
        self.ax.scatter(self.pts_x, self.pts_y, color=self.style_colors["annot"].get(), zorder=5)
        
        for i in range(len(self.pts_x)):
            if self.labels[i].strip():
                self.ax.annotate(self.labels[i], (self.pts_x[i], self.pts_y[i]), 
                                 textcoords="offset points", xytext=(0, 10), 
                                 ha='center', 
                                 fontsize=self.style_sizes["annot"].get(), 
                                 fontfamily=self.style_fonts["annot"].get(), 
                                 color=self.style_colors["annot"].get(), 
                                 weight='bold')

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
        
        for p in ["p2", "p3", "p4", "p5"]:
            if f"{p}_show" in config: getattr(self, f"{p}_show").set(config[f"{p}_show"])
            if f"{p}_name" in config: getattr(self, f"{p}_name").set(config[f"{p}_name"])
            if f"{p}_duration" in config: getattr(self, f"{p}_duration").set(config[f"{p}_duration"])
            if f"{p}_curve" in config: getattr(self, f"{p}_curve").set(config[f"{p}_curve"])
            if f"{p}_milestone" in config and hasattr(self, f"{p}_milestone"): getattr(self, f"{p}_milestone").set(config[f"{p}_milestone"])
            
        if "graph_title" in config: self.graph_title.set(config["graph_title"])
        if "x_label" in config: self.x_label.set(config["x_label"])
        if "y_label" in config: self.y_label.set(config["y_label"])
        
        if "pt1_label" in config: self.pt1_label.set(config["pt1_label"])
        if "pt2_label" in config: self.pt2_label.set(config["pt2_label"])
        if "pt3_label" in config: self.pt3_label.set(config["pt3_label"])
        if "pt4_label" in config: self.pt4_label.set(config["pt4_label"])
        if "pt5_label" in config: self.pt5_label.set(config["pt5_label"])
        if "show_x_ticks" in config: self.show_x_ticks.set(config["show_x_ticks"])
        
        if "style_fonts" in config:
            for k, v in config["style_fonts"].items():
                if k in self.style_fonts: self.style_fonts[k].set(v)
        if "style_sizes" in config:
            for k, v in config["style_sizes"].items():
                if k in self.style_sizes: self.style_sizes[k].set(v)
        if "style_colors" in config:
            for k, v in config["style_colors"].items():
                if k in self.style_colors: self.style_colors[k].set(v)
                
        if hasattr(self, 'color_buttons'):
            for k, btn in self.color_buttons.items():
                btn.config(bg=self.style_colors[k].get())
        
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
        d = {
            "p1_name": self.p1_name.get(),
            "p1_duration": self.p1_duration.get(),
            "p1_milestone": self.p1_milestone.get(),
            "p1_curve": self.p1_curve.get(),
        }
        for p in ["p2", "p3", "p4", "p5"]:
            d[f"{p}_show"] = getattr(self, f"{p}_show").get()
            d[f"{p}_name"] = getattr(self, f"{p}_name").get()
            d[f"{p}_duration"] = getattr(self, f"{p}_duration").get()
            d[f"{p}_curve"] = getattr(self, f"{p}_curve").get()
            if hasattr(self, f"{p}_milestone"):
                d[f"{p}_milestone"] = getattr(self, f"{p}_milestone").get()
                
        d.update({
            "graph_title": self.graph_title.get(),
            "x_label": self.x_label.get(),
            "y_label": self.y_label.get(),
            "pt1_label": self.pt1_label.get(),
            "pt2_label": self.pt2_label.get(),
            "pt3_label": self.pt3_label.get(),
            "pt4_label": self.pt4_label.get(),
            "pt5_label": self.pt5_label.get(),
            "show_x_ticks": self.show_x_ticks.get(),
            "style_fonts": {k: v.get() for k,v in self.style_fonts.items()},
            "style_sizes": {k: v.get() for k,v in self.style_sizes.items()},
            "style_colors": {k: v.get() for k,v in self.style_colors.items()},
            "window_geometry": self.root.geometry()
        })
        return d

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
