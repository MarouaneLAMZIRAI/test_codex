from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.services.db import db_service
from app.ui.main_window import MainWindow
from app.utils.logging_config import setup_logging


def main() -> int:
    setup_logging()
    db_service.connect()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
