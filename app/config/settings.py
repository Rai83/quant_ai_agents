from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Settings:
    data: dict
    db: dict
    files: dict
    analysis: dict
    logging: dict
    metrics: dict


def load_settings(path: Path) -> Settings:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return Settings(
        data=raw["data"],
        db=raw["db"],
        files=raw["files"],
        analysis=raw["analysis"],
        logging=raw["logging"],
        metrics=raw["metrics"],
    )
