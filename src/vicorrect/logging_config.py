from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_dir: Path | None = None) -> Path:
    base_dir = log_dir or Path.cwd() / "logs"
    base_dir.mkdir(parents=True, exist_ok=True)
    log_file = base_dir / "vicorrect.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    return log_file
