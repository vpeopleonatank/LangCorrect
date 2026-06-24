from __future__ import annotations

import logging
from pathlib import Path

from .logging_config import configure_logging


def main() -> int:
    log_file = configure_logging(Path.cwd() / "logs")
    logger = logging.getLogger(__name__)

    try:
        from PyQt6.QtWidgets import QApplication

        from .ui.main_window import MainWindow
    except ImportError as exc:
        logger.exception("Missing desktop dependencies")
        raise SystemExit(
            "Thiếu dependency giao diện. Hãy chạy `pip install -r requirements.txt` trước."
        ) from exc

    app = QApplication([])
    window = MainWindow(log_file=log_file)
    window.show()
    return app.exec()
