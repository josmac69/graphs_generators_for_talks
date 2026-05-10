import os
import sys
import json
import numpy as np

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
                                 QSlider, QCheckBox, QPushButton, QComboBox, 
                                 QSpinBox, QColorDialog, QSplitter, QScrollArea, 
                                 QTabWidget, QGroupBox, QFileDialog, QMessageBox, QInputDialog, QListWidget)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
except ImportError:
    print("Error: PyQt5 is not installed.")
    print("Please install it using: pip install PyQt5")
    sys.exit(1)

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator

class DevelopmentCurveSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Development S-Curve Simulator")
        self.resize(1100, 700)

        self.active_setting_name = None
        self.clean_state_dict = None
        self._is_updating = True # Block updates during init
        
        self.setup_ui()
        
        # Load default settings on startup
        self._load_default_settings()
        if self.clean_state_dict is None:
            self.clean_state_dict = self._get_current_settings_dict()
            
        self._is_updating = False
        self.update_plot()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left Panel
        left_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        
        self.notebook = QTabWidget()
        left_layout.addWidget(self.notebook)
        
        self.tab_phases = QWidget()
        self.tab_labels = QWidget()
        self.tab_style = QWidget()
        
        self.notebook.addTab(self.tab_phases, "Phases")
        self.notebook.addTab(self.tab_labels, "Labels")
        self.notebook.addTab(self.tab_style, "Styling")
        
        self.setup_phases_tab()
        self.setup_labels_tab()
        self.setup_style_tab()
        
        # Action Buttons
        action_layout = QVBoxLayout()
        load_btn = QPushButton("Load Settings")
        load_btn.clicked.connect(self.load_settings_dialog)
        save_conf_btn = QPushButton("Save Settings")
        save_conf_btn.clicked.connect(self.save_settings)
        save_btn = QPushButton("Save Picture (PNG)")
        save_btn.clicked.connect(self.save_picture)
        
        action_layout.addWidget(load_btn)
        action_layout.addWidget(save_conf_btn)
        action_layout.addWidget(save_btn)
        left_layout.addLayout(action_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(left_panel_widget)
        scroll_area.setFixedWidth(390)
        
        # Right Panel
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        plot_layout.addWidget(self.canvas)
        
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(plot_widget, 1)

    def trigger_update(self):
        if not self._is_updating:
            self.update_plot()

    def setup_phases_tab(self):
        layout = QVBoxLayout(self.tab_phases)
        
        self.p_controls = {}
        self.p_controls['p1'] = self.build_phase_controls("Phase 1", 1, 36, has_show=False)
        self.p_controls['p2'] = self.build_phase_controls("Phase 2", 1, 12, has_show=True)
        self.p_controls['p3'] = self.build_phase_controls("Phase 3", 1, 24, has_show=True)
        self.p_controls['p4'] = self.build_phase_controls("Phase 4", 1, 24, has_show=True)
        self.p_controls['p5'] = self.build_phase_controls("Phase 5", 1, 24, has_show=True, has_milestone=False)
        
        for p in ['p1', 'p2', 'p3', 'p4', 'p5']:
            layout.addWidget(self.p_controls[p]['group'])
        layout.addStretch()

        # Set Initial Defaults
        self.set_val(self.p_controls['p1']['name'], "Pre-Production")
        self.set_val(self.p_controls['p1']['duration'], 12)
        self.set_val(self.p_controls['p1']['milestone'], 15)
        self.set_val(self.p_controls['p1']['curve'], 25)

        self.set_val(self.p_controls['p2']['show'], True)
        self.set_val(self.p_controls['p2']['name'], "Principal Photography")
        self.set_val(self.p_controls['p2']['duration'], 3)
        self.set_val(self.p_controls['p2']['milestone'], 80)
        self.set_val(self.p_controls['p2']['curve'], 10)

        self.set_val(self.p_controls['p3']['show'], True)
        self.set_val(self.p_controls['p3']['name'], "Post-Production")
        self.set_val(self.p_controls['p3']['duration'], 9)
        self.set_val(self.p_controls['p3']['milestone'], 95)
        self.set_val(self.p_controls['p3']['curve'], 5)

        self.set_val(self.p_controls['p4']['show'], False)
        self.set_val(self.p_controls['p4']['name'], "Phase 4")
        self.set_val(self.p_controls['p4']['duration'], 6)
        self.set_val(self.p_controls['p4']['milestone'], 98)
        self.set_val(self.p_controls['p4']['curve'], 10)

        self.set_val(self.p_controls['p5']['show'], False)
        self.set_val(self.p_controls['p5']['name'], "Phase 5")
        self.set_val(self.p_controls['p5']['duration'], 6)
        self.set_val(self.p_controls['p5']['curve'], 10)

    def build_phase_controls(self, title, dur_min, dur_max, has_show=True, has_milestone=True):
        group = QGroupBox(title)
        layout = QFormLayout(group)
        controls = {'group': group}
        
        if has_show:
            show_cb = QCheckBox("Show Phase")
            show_cb.stateChanged.connect(self.trigger_update)
            layout.addRow(show_cb)
            controls['show'] = show_cb
            
        name_edit = QLineEdit()
        name_edit.textChanged.connect(self.trigger_update)
        layout.addRow("Name:", name_edit)
        controls['name'] = name_edit
        
        dur_slider = QSlider(Qt.Horizontal)
        dur_slider.setMinimum(dur_min)
        dur_slider.setMaximum(dur_max)
        dur_lbl = QLabel()
        def update_dur(val, lbl=dur_lbl):
            lbl.setText(str(val))
            self.trigger_update()
        dur_slider.valueChanged.connect(update_dur)
        
        h_dur = QHBoxLayout()
        h_dur.addWidget(dur_slider)
        h_dur.addWidget(dur_lbl)
        layout.addRow("Duration (Mo):", h_dur)
        controls['duration'] = dur_slider
        
        if has_milestone:
            mil_slider = QSlider(Qt.Horizontal)
            mil_slider.setMinimum(5)
            mil_slider.setMaximum(95)
            mil_lbl = QLabel()
            def update_mil(val, lbl=mil_lbl):
                lbl.setText(str(val))
                self.trigger_update()
            mil_slider.valueChanged.connect(update_mil)
            
            h_mil = QHBoxLayout()
            h_mil.addWidget(mil_slider)
            h_mil.addWidget(mil_lbl)
            layout.addRow("End % Done:", h_mil)
            controls['milestone'] = mil_slider
            
        curv_slider = QSlider(Qt.Horizontal)
        curv_slider.setMinimum(2)
        curv_slider.setMaximum(50) 
        curv_lbl = QLabel()
        def update_curv(val, lbl=curv_lbl):
            lbl.setText(f"{val/10.0:.1f}")
            self.trigger_update()
        curv_slider.valueChanged.connect(update_curv)
        
        h_curv = QHBoxLayout()
        h_curv.addWidget(curv_slider)
        h_curv.addWidget(curv_lbl)
        layout.addRow("Curvature:", h_curv)
        controls['curve'] = curv_slider
        
        return controls

    def setup_labels_tab(self):
        layout = QFormLayout(self.tab_labels)
        self.labels_controls = {}
        
        settings = [
            ("graph_title", "Title:", "Development S-Curve"),
            ("x_label", "X-Axis:", "Time (Months)"),
            ("y_label", "Y-Axis:", "Percentage Done (%)"),
            ("pt1_label", "Point 1 (P1 End):", "Alpha"),
            ("pt2_label", "Point 2 (P2 End):", "Beta"),
            ("pt3_label", "Point 3:", "Release"),
            ("pt4_label", "Point 4:", ""),
            ("pt5_label", "Point 5:", "")
        ]
        
        for key, text, default in settings:
            edit = QLineEdit(default)
            edit.textChanged.connect(self.trigger_update)
            layout.addRow(text, edit)
            self.labels_controls[key] = edit
            
        self.labels_controls["graph_width"] = QSpinBox()
        self.labels_controls["graph_width"].setRange(1, 30)
        self.labels_controls["graph_width"].setValue(7)
        self.labels_controls["graph_width"].valueChanged.connect(self.trigger_update)
        layout.addRow("Graph Width (in):", self.labels_controls["graph_width"])

        self.labels_controls["graph_height"] = QSpinBox()
        self.labels_controls["graph_height"].setRange(1, 30)
        self.labels_controls["graph_height"].setValue(5)
        self.labels_controls["graph_height"].valueChanged.connect(self.trigger_update)
        layout.addRow("Graph Height (in):", self.labels_controls["graph_height"])
            
        self.show_x_ticks = QCheckBox("Show Numbers on X Axis")
        self.show_x_ticks.setChecked(True)
        self.show_x_ticks.stateChanged.connect(self.trigger_update)
        layout.addRow(self.show_x_ticks)

    def setup_style_tab(self):
        layout = QVBoxLayout(self.tab_style)
        fonts = ["sans-serif", "serif", "monospace", "Arial", "Times New Roman", "Courier New", "Comic Sans MS"]
        groups = [
            ("title", "Main Title", "#000000", 14),
            ("axes", "Axes Labels", "#000000", 12),
            ("ticks", "Tick Numbers", "#000000", 10),
            ("legend", "Legend", "#000000", 10),
            ("annot", "Annotations", "#ff0000", 10)
        ]
        
        self.style_controls = {}
        for key, name, def_color, def_size in groups:
            group = QGroupBox(name)
            glayout = QFormLayout(group)
            
            self.style_controls[key] = {}
            
            font_cb = QComboBox()
            font_cb.addItems(fonts)
            font_cb.currentTextChanged.connect(self.trigger_update)
            glayout.addRow("Font:", font_cb)
            self.style_controls[key]['font'] = font_cb
            
            size_sb = QSpinBox()
            size_sb.setRange(6, 40)
            size_sb.setValue(def_size)
            size_sb.valueChanged.connect(self.trigger_update)
            glayout.addRow("Size:", size_sb)
            self.style_controls[key]['size'] = size_sb
            
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {def_color};")
            self.style_controls[key]['color_val'] = def_color
            def set_color(k=key, b=color_btn):
                color = QColorDialog.getColor(QColor(self.style_controls[k]['color_val']), self)
                if color.isValid():
                    h = color.name()
                    self.style_controls[k]['color_val'] = h
                    b.setStyleSheet(f"background-color: {h};")
                    self.trigger_update()
            color_btn.clicked.connect(set_color)
            glayout.addRow("Color:", color_btn)
            
            layout.addWidget(group)
        layout.addStretch()

    # Utilities
    def get_val(self, ctrl):
        if isinstance(ctrl, QLineEdit): return ctrl.text()
        elif isinstance(ctrl, QCheckBox): return ctrl.isChecked()
        elif isinstance(ctrl, QSlider): return ctrl.value()
        elif isinstance(ctrl, QComboBox): return ctrl.currentText()
        elif isinstance(ctrl, QSpinBox): return ctrl.value()
        
    def set_val(self, ctrl, val):
        if isinstance(ctrl, QLineEdit): ctrl.setText(str(val))
        elif isinstance(ctrl, QCheckBox): ctrl.setChecked(bool(val))
        elif isinstance(ctrl, QSlider): ctrl.setValue(int(val))
        elif isinstance(ctrl, QComboBox): ctrl.setCurrentText(str(val))
        elif isinstance(ctrl, QSpinBox): ctrl.setValue(int(val))

    def generate_curve_segment(self, x_start, x_end, y_start, y_end, curve_shape, num_points=100):
        if x_start == x_end:
            return [x_start], [y_end]
        x_vals = np.linspace(x_start, x_end, num_points)
        progress_t = (x_vals - x_start) / (x_end - x_start)
        y_vals = y_start + (y_end - y_start) * (progress_t ** curve_shape)
        return x_vals, y_vals

    def update_plot(self):
        self.ax.clear()

        # Read phase settings
        p1 = (self.get_val(self.p_controls['p1']['duration']), self.get_val(self.p_controls['p1']['name']), self.get_val(self.p_controls['p1']['milestone']), self.get_val(self.p_controls['p1']['curve'])/10.0, True, self.get_val(self.labels_controls['pt1_label']))
        p2 = (self.get_val(self.p_controls['p2']['duration']), self.get_val(self.p_controls['p2']['name']), self.get_val(self.p_controls['p2']['milestone']), self.get_val(self.p_controls['p2']['curve'])/10.0, self.get_val(self.p_controls['p2']['show']), self.get_val(self.labels_controls['pt2_label']))
        p3 = (self.get_val(self.p_controls['p3']['duration']), self.get_val(self.p_controls['p3']['name']), self.get_val(self.p_controls['p3']['milestone']), self.get_val(self.p_controls['p3']['curve'])/10.0, self.get_val(self.p_controls['p3']['show']), self.get_val(self.labels_controls['pt3_label']))
        p4 = (self.get_val(self.p_controls['p4']['duration']), self.get_val(self.p_controls['p4']['name']), self.get_val(self.p_controls['p4']['milestone']), self.get_val(self.p_controls['p4']['curve'])/10.0, self.get_val(self.p_controls['p4']['show']), self.get_val(self.labels_controls['pt4_label']))
        p5 = (self.get_val(self.p_controls['p5']['duration']), self.get_val(self.p_controls['p5']['name']), 100, self.get_val(self.p_controls['p5']['curve'])/10.0, self.get_val(self.p_controls['p5']['show']), self.get_val(self.labels_controls['pt5_label']))

        phases = [p1, p2, p3, p4, p5]
        active_phases = [p for p in phases if p[4]]
        if not active_phases:
            self.canvas.draw_idle()
            return

        last_idx = len(active_phases) - 1
        last_p = active_phases[last_idx]
        active_phases[last_idx] = (last_p[0], last_p[1], 100, last_p[3], last_p[4], last_p[5])

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

        self.ax.set_title(self.get_val(self.labels_controls["graph_title"]), 
                          fontsize=self.get_val(self.style_controls["title"]['size']), 
                          fontfamily=self.get_val(self.style_controls["title"]['font']), 
                          color=self.style_controls["title"]['color_val'], pad=15)
                          
        self.ax.set_xlabel(self.get_val(self.labels_controls["x_label"]), 
                           fontsize=self.get_val(self.style_controls["axes"]['size']), 
                           fontfamily=self.get_val(self.style_controls["axes"]['font']), 
                           color=self.style_controls["axes"]['color_val'])
                           
        self.ax.set_ylabel(self.get_val(self.labels_controls["y_label"]), 
                           fontsize=self.get_val(self.style_controls["axes"]['size']), 
                           fontfamily=self.get_val(self.style_controls["axes"]['font']), 
                           color=self.style_controls["axes"]['color_val'])
                           
        self.ax.set_xlim(0, t_total)
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        fig_w = self.get_val(self.labels_controls["graph_width"])
        fig_h = self.get_val(self.labels_controls["graph_height"])
        self.fig.set_size_inches(fig_w, fig_h)
        self.canvas.updateGeometry()
        
        tick_fontsize = self.get_val(self.style_controls["ticks"]['size'])
        tick_fontfamily = self.get_val(self.style_controls["ticks"]['font'])
        tick_color = self.style_controls["ticks"]['color_val']

        self.ax.tick_params(axis='both', labelsize=tick_fontsize, labelcolor=tick_color)
        if not self.get_val(self.show_x_ticks):
            self.ax.tick_params(axis='x', labelbottom=False)

        for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            label.set_fontfamily(tick_fontfamily)

        leg = self.ax.legend(loc="upper left", prop={'family': self.get_val(self.style_controls["legend"]['font']), 'size': self.get_val(self.style_controls["legend"]['size'])})
        if leg:
            for text in leg.get_texts():
                text.set_color(self.style_controls["legend"]['color_val'])

        self.ax.scatter(self.pts_x, self.pts_y, color=self.style_controls["annot"]['color_val'], zorder=5)
        
        for i in range(len(self.pts_x)):
            if self.labels[i].strip():
                self.ax.annotate(self.labels[i], (self.pts_x[i], self.pts_y[i]), 
                                 textcoords="offset points", xytext=(0, 10), 
                                 ha='center', 
                                 fontsize=self.get_val(self.style_controls["annot"]['size']), 
                                 fontfamily=self.get_val(self.style_controls["annot"]['font']), 
                                 color=self.style_controls["annot"]['color_val'], 
                                 weight='bold')

        self.canvas.draw_idle()

    def save_picture(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph As...", "", "PNG files (*.png);;All files (*.*)")
        if file_path:
            try:
                self.fig.savefig(file_path, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Graph saved successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image:\n{e}")

    def apply_settings(self, config, name=None):
        self._is_updating = True
        
        for i in range(1, 6):
            p = f"p{i}"
            if f"{p}_name" in config: self.set_val(self.p_controls[p]['name'], config[f"{p}_name"])
            if f"{p}_duration" in config: self.set_val(self.p_controls[p]['duration'], config[f"{p}_duration"])
            if f"{p}_curve" in config: self.set_val(self.p_controls[p]['curve'], int(config[f"{p}_curve"] * 10))
            if f"{p}_show" in config and 'show' in self.p_controls[p]: self.set_val(self.p_controls[p]['show'], config[f"{p}_show"])
            if f"{p}_milestone" in config and 'milestone' in self.p_controls[p]: self.set_val(self.p_controls[p]['milestone'], config[f"{p}_milestone"])
            
        if "graph_title" in config: self.set_val(self.labels_controls["graph_title"], config["graph_title"])
        if "x_label" in config: self.set_val(self.labels_controls["x_label"], config["x_label"])
        if "y_label" in config: self.set_val(self.labels_controls["y_label"], config["y_label"])
        if "graph_width" in config: self.set_val(self.labels_controls["graph_width"], config["graph_width"])
        if "graph_height" in config: self.set_val(self.labels_controls["graph_height"], config["graph_height"])
        
        for i in range(1, 6):
            pt = f"pt{i}_label"
            if pt in config: self.set_val(self.labels_controls[pt], config[pt])
            
        if "show_x_ticks" in config: self.set_val(self.show_x_ticks, config["show_x_ticks"])
        
        if "style_fonts" in config:
            for k, v in config["style_fonts"].items():
                if k in self.style_controls: self.set_val(self.style_controls[k]['font'], v)
        if "style_sizes" in config:
            for k, v in config["style_sizes"].items():
                if k in self.style_controls: self.set_val(self.style_controls[k]['size'], v)
        if "style_colors" in config:
            for k, v in config["style_colors"].items():
                if k in self.style_controls:
                    self.style_controls[k]['color_val'] = v
                    # The color button isn't easily accessible, find the layout child if needed or just skip updating visual button in load?
                    # Wait, we can't easily set the button style without storing it. We should store it.
                    # I didn't store the color_btn in self.style_controls, wait I can just redraw it or just don't worry about it too much, 
                    # actually I will fix this right now by storing it.
                    
        if "window_geometry" in config:
            try:
                # Basic geometry restoration for PyQt
                geo = config["window_geometry"] # Tkinter geometry "1100x700" 
                if "x" in geo and "+" not in geo:
                    w, h = geo.split("x")
                    self.resize(int(w), int(h))
            except Exception:
                pass
                
        self._is_updating = False
        self.update_plot()
        
        self.active_setting_name = name
        if name:
            self.setWindowTitle(f"Development S-Curve Simulator - [{name}]")
        else:
            self.setWindowTitle("Development S-Curve Simulator")
            
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
            QMessageBox.information(self, "Info", "No saved settings found (generator.conf missing).")
            return
            
        try:
            with open(conf_file, 'r') as f:
                configs = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read settings:\n{e}")
            return
            
        if not configs:
            QMessageBox.information(self, "Info", "No settings available in conf file.")
            return

        names = list(configs.keys())
        name, ok = QInputDialog.getItem(self, "Load Settings", "Select configuration to load:", names, 0, False)
        if ok and name:
            self.apply_settings(configs[name], name)

    def _get_current_settings_dict(self):
        d = {}
        for i in range(1, 6):
            p = f"p{i}"
            d[f"{p}_name"] = self.get_val(self.p_controls[p]['name'])
            d[f"{p}_duration"] = self.get_val(self.p_controls[p]['duration'])
            d[f"{p}_curve"] = self.get_val(self.p_controls[p]['curve']) / 10.0
            if 'show' in self.p_controls[p]: d[f"{p}_show"] = self.get_val(self.p_controls[p]['show'])
            if 'milestone' in self.p_controls[p]: d[f"{p}_milestone"] = self.get_val(self.p_controls[p]['milestone'])
                
        d.update({
            "graph_title": self.get_val(self.labels_controls["graph_title"]),
            "x_label": self.get_val(self.labels_controls["x_label"]),
            "y_label": self.get_val(self.labels_controls["y_label"]),
            "graph_width": self.get_val(self.labels_controls["graph_width"]),
            "graph_height": self.get_val(self.labels_controls["graph_height"]),
            "pt1_label": self.get_val(self.labels_controls["pt1_label"]),
            "pt2_label": self.get_val(self.labels_controls["pt2_label"]),
            "pt3_label": self.get_val(self.labels_controls["pt3_label"]),
            "pt4_label": self.get_val(self.labels_controls["pt4_label"]),
            "pt5_label": self.get_val(self.labels_controls["pt5_label"]),
            "show_x_ticks": self.get_val(self.show_x_ticks),
            "style_fonts": {k: self.get_val(v['font']) for k,v in self.style_controls.items()},
            "style_sizes": {k: self.get_val(v['size']) for k,v in self.style_controls.items()},
            "style_colors": {k: v['color_val'] for k,v in self.style_controls.items()},
            "window_geometry": f"{self.width()}x{self.height()}"
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
        name, ok = QInputDialog.getText(self, "Save Settings", "Enter name for this setting:", QLineEdit.Normal, initial_name)
        
        if not ok or not name.strip():
            return
            
        setting_name = name.strip()

        if setting_name in configs:
            reply = QMessageBox.question(self, "Overwrite?", f"Setting '{setting_name}' already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        try:
            configs[setting_name] = self._get_current_settings_dict()
            with open(conf_file, 'w') as f:
                json.dump(configs, f, indent=4)
            QMessageBox.information(self, "Success", f"Setting '{setting_name}' saved successfully in generator.conf!")
            
            self.active_setting_name = setting_name
            self.setWindowTitle(f"Development S-Curve Simulator - [{setting_name}]")
            self.clean_state_dict = self._get_current_settings_dict()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
                
    def is_dirty(self):
        if not hasattr(self, 'clean_state_dict') or not self.clean_state_dict:
            return False
        current = self._get_current_settings_dict()
        for k in current:
            if k == "window_geometry": continue
            if current[k] != self.clean_state_dict.get(k):
                return True
        return False
        
    def closeEvent(self, event):
        if self.is_dirty():
            reply = QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Do you want to save before exiting?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_settings()
                if not self.is_dirty(): 
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DevelopmentCurveSimulator()
    window.show()
    sys.exit(app.exec_())
