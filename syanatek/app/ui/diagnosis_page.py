from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.viewer.three_d_viewer import ThreeDViewer


class DiagnosisPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QHBoxLayout(self)

        left = QVBoxLayout()
        self.safety_banner = QLabel("Safety: Follow LOTO / HV PPE protocol before step execution.")
        self.safety_banner.setStyleSheet("background:#f59e0b;color:#111827;padding:8px;font-weight:700;")
        left.addWidget(self.safety_banner)

        self.step_list = QListWidget()
        left.addWidget(QLabel("Diagnostic Steps"))
        left.addWidget(self.step_list)

        self.progress = QLabel("Step 0/0")
        left.addWidget(self.progress)

        self.instructions = QTextEdit()
        self.instructions.setReadOnly(True)
        left.addWidget(QLabel("Instructions"))
        left.addWidget(self.instructions)

        btn_row = QHBoxLayout()
        self.yes_btn = QPushButton("YES / Completed")
        self.no_btn = QPushButton("NO / Failed")
        self.isolate_btn = QPushButton("Isolate Part")
        self.reset_btn = QPushButton("Reset Camera")
        btn_row.addWidget(self.yes_btn)
        btn_row.addWidget(self.no_btn)
        btn_row.addWidget(self.isolate_btn)
        btn_row.addWidget(self.reset_btn)
        left.addLayout(btn_row)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setMaximumWidth(420)

        self.viewer = ThreeDViewer()

        root.addWidget(left_widget)
        root.addWidget(self.viewer, stretch=1)

        self.setStyleSheet("QWidget{background:#0f172a;color:#e5e7eb;} QListWidget,QTextEdit{background:#111827;}")
        self.instructions.setAlignment(Qt.AlignTop)
