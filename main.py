import asyncio
from pathlib import Path

from app.config.settings import load_settings
from app.service.ai_orchestrator import run
from app.config.logging import setup_logging
import os

setup_logging()

if __name__ == '__main__':
    settings = load_settings(Path("config/local.yaml"))
    os.environ[
        "OPENAI_API_KEY"] = "OPENAI_API_KEY"

    asyncio.run(run())
