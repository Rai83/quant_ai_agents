import pandas as pd
from pathlib import Path


def load_csv_to_dataframe(
    file_path: str,
    *,
    parse_dates: list[str] | None = None,
    dtype: dict | None = None,
) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df = pd.read_csv(
            path,
            parse_dates=parse_dates,
            dtype=dtype
        )
    except Exception as exc:
        raise ValueError(f"Failed to load CSV {path}") from exc

    return df
