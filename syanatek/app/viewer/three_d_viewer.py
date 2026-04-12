from __future__ import annotations

import json
import logging
from pathlib import Path

import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.config import settings

logger = logging.getLogger(__name__)


class ThreeDViewer(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.plotter = QtInteractor(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotter.interactor)

        self.actors: dict[str, object] = {}
        self.default_colors: dict[str, str] = {}
        self.current_highlight: list[str] = []

        self._init_scene()

    def _init_scene(self) -> None:
        self.plotter.set_background("#111827")
        self.plotter.add_axes()
        self.plotter.enable_parallel_projection()
        self.load_manifest_scene(Path(settings.asset_manifest))
        self.plotter.reset_camera()

    def load_manifest_scene(self, manifest_path: Path) -> None:
        if not manifest_path.exists():
            logger.warning("Missing asset manifest %s. Loading primitive fallback.", manifest_path)
            self._load_fallback_geometry()
            return

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for part in manifest.get("parts", []):
            part_code = part["part_code"]
            mesh_path = manifest_path.parent / part["asset_path"]
            color = part.get("color", "lightgray")
            try:
                mesh = pv.read(mesh_path)
                actor = self.plotter.add_mesh(mesh, name=part_code, color=color, smooth_shading=True)
                self.actors[part_code] = actor
                self.default_colors[part_code] = color
            except Exception as exc:
                logger.error("Failed to load mesh %s for %s: %s", mesh_path, part_code, exc)

        if not self.actors:
            self._load_fallback_geometry()

    def _load_fallback_geometry(self) -> None:
        body = pv.Box(bounds=(-1.6, 1.6, -0.8, 0.8, -0.3, 0.3))
        battery = pv.Box(bounds=(-1.2, 1.2, -0.6, 0.6, -0.6, -0.3))
        pump = pv.Sphere(center=(0.9, 0.0, 0.0), radius=0.2)

        self.actors["CHASSIS"] = self.plotter.add_mesh(body, color="silver", name="CHASSIS")
        self.actors["BATTERY_PACK"] = self.plotter.add_mesh(battery, color="steelblue", name="BATTERY_PACK")
        self.actors["COOLANT_PUMP"] = self.plotter.add_mesh(pump, color="seagreen", name="COOLANT_PUMP")
        self.default_colors = {
            "CHASSIS": "silver",
            "BATTERY_PACK": "steelblue",
            "COOLANT_PUMP": "seagreen",
        }

    def highlight_parts(self, part_codes: list[str], isolate: bool = False) -> None:
        self.clear_highlight()
        self.current_highlight = part_codes

        for code, actor in self.actors.items():
            try:
                actor.prop.show_edges = False
                if code in part_codes:
                    actor.prop.color = pv.Color("red")
                    actor.prop.show_edges = True
                    actor.prop.edge_color = pv.Color("yellow")
                    actor.prop.opacity = 1.0
                elif isolate:
                    actor.prop.opacity = 0.08
                else:
                    actor.prop.opacity = 1.0
            except Exception as exc:
                logger.warning("Actor style update failed for %s: %s", code, exc)
        self.plotter.render()

    def clear_highlight(self) -> None:
        for code, actor in self.actors.items():
            default = self.default_colors.get(code, "lightgray")
            actor.prop.color = pv.Color(default)
            actor.prop.show_edges = False
            actor.prop.opacity = 1.0
        self.plotter.render()

    def reset_camera(self) -> None:
        self.plotter.reset_camera()

    def isolate_selected(self) -> None:
        if self.current_highlight:
            self.highlight_parts(self.current_highlight, isolate=True)
