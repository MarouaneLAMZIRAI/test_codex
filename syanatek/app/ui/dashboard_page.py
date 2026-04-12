from __future__ import annotations

from dataclasses import dataclass

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass
class DashboardSignals:
    open_diagnosis: callable
    refresh_data: callable


class DashboardPage(QWidget):
    def __init__(self, signals: DashboardSignals, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.signals = signals

        root = QVBoxLayout(self)

        filters = QGroupBox("Vehicle Selection")
        form = QFormLayout(filters)
        self.manufacturer_combo = QComboBox()
        self.model_combo = QComboBox()
        self.year_combo = QComboBox()
        self.variant_combo = QComboBox()
        form.addRow("Manufacturer", self.manufacturer_combo)
        form.addRow("Model", self.model_combo)
        form.addRow("Year", self.year_combo)
        form.addRow("Variant", self.variant_combo)
        root.addWidget(filters)

        kpi_grid = QGridLayout()
        self.kpi_labels = {}
        for idx, metric in enumerate(["Voltage (V)", "Current (A)", "SoC (%)", "Temp (°C)"]):
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet("background:#1f2937;color:#f9fafb;border-radius:8px;padding:12px;")
            layout = QVBoxLayout(card)
            title = QLabel(metric)
            value = QLabel("--")
            value.setStyleSheet("font-size:22px;font-weight:700;")
            self.kpi_labels[metric] = value
            layout.addWidget(title)
            layout.addWidget(value)
            kpi_grid.addWidget(card, 0, idx)
        root.addLayout(kpi_grid)

        plots = QHBoxLayout()
        self.plot_voltage = pg.PlotWidget(title="Voltage Trend")
        self.plot_soc = pg.PlotWidget(title="SoC Trend")
        plots.addWidget(self.plot_voltage)
        plots.addWidget(self.plot_soc)
        root.addLayout(plots)

        controls = QHBoxLayout()
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Last hour", "Last day"])
        controls.addWidget(QLabel("Time Filter:"))
        controls.addWidget(self.range_combo)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.signals.refresh_data)
        controls.addWidget(refresh_button)

        action_button = QPushButton("Recommended Actions")
        action_button.setStyleSheet("background:#ef4444;color:white;padding:8px 16px;")
        action_button.clicked.connect(self.signals.open_diagnosis)
        controls.addWidget(action_button)
        controls.addStretch()

        root.addLayout(controls)

    def set_vehicle_filters(self, manufacturers: list[str], models: list[str], years: list[str], variants: list[str]) -> None:
        self.manufacturer_combo.clear()
        self.manufacturer_combo.addItems(manufacturers)
        self.model_combo.clear()
        self.model_combo.addItems(models)
        self.year_combo.clear()
        self.year_combo.addItems(years)
        self.variant_combo.clear()
        self.variant_combo.addItems(variants)

    def update_kpis(self, voltage: float, current: float, soc: float, temp: float) -> None:
        self.kpi_labels["Voltage (V)"].setText(f"{voltage:.1f}")
        self.kpi_labels["Current (A)"].setText(f"{current:.1f}")
        self.kpi_labels["SoC (%)"].setText(f"{soc:.1f}")
        self.kpi_labels["Temp (°C)"].setText(f"{temp:.1f}")

    def update_plots(self, xs: list[float], voltage: list[float], soc: list[float]) -> None:
        self.plot_voltage.clear()
        self.plot_soc.clear()
        self.plot_voltage.plot(xs, voltage, pen=pg.mkPen(color="#60a5fa", width=2))
        self.plot_soc.plot(xs, soc, pen=pg.mkPen(color="#34d399", width=2))
