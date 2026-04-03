# Graphs Generators for Talks

When I create presentations for talks, I often need to show some graphs which illustrate the concepts I am talking about. In many cases, these graphs are meant to show a general idea or conceptual model rather than representing precise, strict data points.

Over time, I have created many small scripts and utilities to generate these graphs, but they often ended up being lost in the darkness of my hard drives. 

This repository is a centralized collection of these scripts, designed so that I can easily find, adjust, and re-generate these conceptual illustrations whenever I need them.

## 🛠️ Available Generators

Below is an index of the tools currently available in this repository. Each tool is self-contained in its own directory:

| Generator | Description | Stack |
| :--- | :--- | :--- |
| 📊 [**Development S-Curve Simulator**](./python/hockey_stick_phases/) | An interactive GUI application to simulate and visualize a project development life cycle across three phases (e.g. Pre-Production, Principal Photography, Post-Production). Allows dynamic tweaking of phase duration, success milestones, and exponential curvature, letting you save the results to PNG. | Python (`matplotlib`, `tkinter`) |

## 🚀 Usage

Generators are grouped by their primary programming language (e.g., `/python/`).

To use a generator:
1. Navigate to its specific directory.
2. Read the local `README.md` for dependencies and details.
3. Most tools provide a convenient `start.sh` script that will automatically handle virtual environments, install dependencies, and launch the tool for you.

For example, to run the Hockey Stick S-Curve generator:
```bash
cd python/hockey_stick_phases
./start.sh
```
