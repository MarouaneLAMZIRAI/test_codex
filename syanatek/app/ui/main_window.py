from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.services.repository import Repository, VehicleFilter
from app.ui.dashboard_page import DashboardPage, DashboardSignals
from app.ui.diagnosis_page import DiagnosisPage

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.repo = Repository()
        self.vehicle_filters = self.repo.get_vehicle_filters()
        self.vehicle_id = 1
        self.steps = []

        self.setWindowTitle("SyanaTek - Guided Diagnosis")
        self.resize(1440, 900)

        top = QToolBar("top")
        top.addWidget(QLabel("SyanaTek | User: Technician_01"))
        self.addToolBar(top)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(
            DashboardSignals(
                open_diagnosis=self.open_diagnosis,
                refresh_data=self.load_dashboard_data,
            )
        )
        self.diagnosis_page = DiagnosisPage()
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.diagnosis_page)

        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(self.stack)

        back = QPushButton("Back to Dashboard")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_page))
        layout.addWidget(back)
        self.setCentralWidget(wrapper)

        self._wire_events()
        self._populate_filters()
        self.load_dashboard_data()

    def _wire_events(self) -> None:
        self.diagnosis_page.step_list.currentRowChanged.connect(self.on_step_selected)
        self.diagnosis_page.isolate_btn.clicked.connect(self.diagnosis_page.viewer.isolate_selected)
        self.diagnosis_page.reset_btn.clicked.connect(self.diagnosis_page.viewer.reset_camera)
        self.diagnosis_page.yes_btn.clicked.connect(lambda: self._mark_step("YES"))
        self.diagnosis_page.no_btn.clicked.connect(lambda: self._mark_step("NO"))

    def _populate_filters(self) -> None:
        manufacturers = sorted({vf.manufacturer for vf in self.vehicle_filters})
        models = sorted({vf.model for vf in self.vehicle_filters})
        years = sorted({str(vf.year) for vf in self.vehicle_filters}, reverse=True)
        variants = sorted({vf.variant or "N/A" for vf in self.vehicle_filters})
        self.dashboard_page.set_vehicle_filters(manufacturers, models, years, variants)

    def _selected_vehicle(self) -> VehicleFilter:
        return VehicleFilter(
            manufacturer=self.dashboard_page.manufacturer_combo.currentText(),
            model=self.dashboard_page.model_combo.currentText(),
            year=int(self.dashboard_page.year_combo.currentText()),
            variant=self.dashboard_page.variant_combo.currentText().replace("N/A", "") or None,
        )

    def load_dashboard_data(self) -> None:
        vf = self._selected_vehicle()
        vehicle_id = self.repo.get_vehicle_id(vf)
        if vehicle_id is None:
            QMessageBox.warning(self, "Vehicle Missing", "No vehicle found for selected filters.")
            return
        self.vehicle_id = vehicle_id

        hours = 24 if self.dashboard_page.range_combo.currentText() == "Last day" else 1
        df = self.repo.get_kpi_timeseries(vehicle_id, hours=hours)
        if df.empty:
            QMessageBox.information(self, "DAQ", "No DAQ data available for this period.")
            return

        latest = df.iloc[-1]
        self.dashboard_page.update_kpis(
            float(latest.get("voltage", 0)),
            float(latest.get("current", 0)),
            float(latest.get("soc", 0)),
            float(latest.get("temp_c", 0)),
        )
        xs = list(range(len(df)))
        self.dashboard_page.update_plots(xs, df["voltage"].fillna(0).tolist(), df["soc"].fillna(0).tolist())

    def open_diagnosis(self) -> None:
        self.steps = self.repo.get_steps(self.vehicle_id)
        self.diagnosis_page.step_list.clear()

        if not self.steps:
            QMessageBox.warning(self, "No steps", "No diagnostic steps configured for this vehicle.")
            return

        for step in self.steps:
            self.diagnosis_page.step_list.addItem(f"{step.step_order}. {step.title}")
        self.stack.setCurrentWidget(self.diagnosis_page)
        self.diagnosis_page.step_list.setCurrentRow(0)

    def on_step_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.steps):
            return
        step = self.steps[row]
        parts = self.repo.get_target_part_codes(step.id)

        info = (
            f"Title: {step.title}\n\n"
            f"Instructions: {step.instructions}\n\n"
            f"Tools: {step.tools_required or 'N/A'}\n"
            f"Safety: {step.safety_warning or 'N/A'}\n"
            f"Severity: {step.severity or 'N/A'} | ETA: {step.estimated_minutes or '-'} min\n"
            f"Mapped parts: {', '.join(parts) if parts else 'None'}"
        )
        self.diagnosis_page.instructions.setText(info)
        self.diagnosis_page.progress.setText(f"Step {row + 1}/{len(self.steps)}")

        if not parts:
            QMessageBox.warning(self, "Mapping Missing", "This step is not linked to any 3D part.")
            self.diagnosis_page.viewer.clear_highlight()
        else:
            self.diagnosis_page.viewer.highlight_parts(parts)

    def _mark_step(self, outcome: str) -> None:
        row = self.diagnosis_page.step_list.currentRow()
        if row < 0:
            return
        logger.info("Step %s marked as %s", row + 1, outcome)
