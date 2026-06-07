#!/usr/bin/env python
"""六堡茶智能服务平台 - 启动脚本"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=LOG_LEVEL.lower(),
        factory=False,
    )
