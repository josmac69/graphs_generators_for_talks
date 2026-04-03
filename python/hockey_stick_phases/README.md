# Development S-Curve Simulator

## Description

The `generator.py` script is a Python-based interactive GUI application designed to visualize and simulate a three-phase project development life cycle (such as Pre-Production, Principal Photography, and Post-Production). It plots the percentage of completion against time based on user-defined parameters, forming an S-Curve (or "hockey stick" curve).

The tool boasts an intuitive interface that allows users to independently adjust:
- **Phase Duration** (time spent in each phase)
- **Phase Completion Milestone** (work percentage targeted by the end of Phases 1 and 2)
- **Curvature** (allowing tuning of the progress distribution over time, supporting late bloomers, linear progress, and early bloomers).

Modifying these parameters instantly updates a dynamically rendered `matplotlib` graph. Users also have the option to export and save their generated plot as a high-quality PNG image.

## Requirements

- Python 3
- `tkinter` (Standard Python library, OS-level package might be required on Linux. See Note below.)
- `numpy`
- `matplotlib`

**Linux specific node**: Depending on your distribution, you might need to install `tkinter` from your system's package manager if you haven't already. E.g., for Debian/Ubuntu:
```bash
sudo apt-get install python3-tk
```

## How to Run

For convenience, a `start.sh` script is provided. Running this bash script will:
1. Check if a Python virtual environment (`venv`) exists.
2. Automatically create the environment if it's missing.
3. Activate the environment.
4. Install the required external libraries (`numpy` and `matplotlib`).
5. Run the `generator.py` application.

To start the project using the script, run:

```bash
chmod +x start.sh
./start.sh
```

### Manual Execution

If you wish to do this manually instead, follow these commands in the terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install numpy matplotlib
python3 generator.py
```
