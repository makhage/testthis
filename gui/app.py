"""Simple GUI application for loading and exporting points."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple

from exporters.dxf_export import write_dxf

Point = Tuple[float, float]


class App(tk.Tk):
    """Minimal GUI for loading points and exporting them as DXF."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Point Exporter")
        self.points: List[Point] = []

        load_btn = tk.Button(self, text="Load Points", command=self.load_points)
        load_btn.pack(padx=5, pady=5)

        self.export_btn = tk.Button(
            self, text="Export DXF", command=self.export_dxf, state=tk.DISABLED
        )
        self.export_btn.pack(padx=5, pady=5)

    def load_points(self) -> None:
        """Load points from a text file (two numbers per line)."""
        file_path = filedialog.askopenfilename(title="Select point file")
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf8") as handle:
                self.points = [
                    tuple(map(float, line.split()))
                    for line in handle
                    if line.strip()
                ]
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Error", str(exc))
            return
        messagebox.showinfo("Loaded", f"Loaded {len(self.points)} points")
        self.export_btn.config(state=tk.NORMAL)

    def export_dxf(self) -> None:
        """Export loaded points to a DXF file."""
        if not self.points:
            messagebox.showwarning("No points", "No points loaded")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".dxf", filetypes=[("DXF files", "*.dxf")]
        )
        if not save_path:
            return
        try:
            write_dxf(self.points, save_path)
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror("Error", str(exc))
        else:
            messagebox.showinfo("Success", "DXF exported")


if __name__ == "__main__":  # pragma: no cover - manual execution
    app = App()
    app.mainloop()
