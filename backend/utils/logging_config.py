import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import os

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("liubao")
