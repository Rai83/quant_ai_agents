import pandas as pd

from app.repository.csv import load_csv_to_dataframe
from app.repository.db import PostgresClient
import logging

logger = logging.getLogger(__name__)

class DataLoading:

    def __init__(self, db_client: PostgresClient, correlation_uuid: str):
        self.db_client = db_client
        self.correlation_uuid = correlation_uuid

    def process(self, file_path,
                value_name,
                start_date=None,
                end_date=None,
                timeframe =None,
                ) -> dict:
        try:
            logger.info(f"{self.correlation_uuid}: starting loading assets from file: {file_path} value_name: {value_name} start_date: {start_date} end_date: {end_date} timeframe: {timeframe}")
            df = load_csv_to_dataframe(file_path)
            df = filter_dates(df, start_date, end_date)
            self.insert_quotes_from_df(df, timeframe, value_name)
            logger.info(f"{self.correlation_uuid}: finished loading assets from file: {file_path} value_name: {value_name} start_date: {start_date} end_date: {end_date} timeframe: {timeframe}")
            result = {
                'correlation_uuid': self.correlation_uuid,
                'rows': df.shape[0],
                'columns': df.shape[1]
            }
            logger.info(result)
            return result
        except Exception as e:
            message = f"{self.correlation_uuid}: failed loading assets from file: {file_path} value_name: {value_name} start_date: {start_date} end_date: {end_date} timeframe: {timeframe} message: {str(e)}"
            logger.error(message)
            raise Exception(message)

    def insert_quotes_from_df(self, df, timeframe: str, value_name: str) -> None:
        if df.empty:
            logger.info(f"{self.correlation_uuid}: Empty dataframe")
            return

        symbols = [col for col in df.columns if col != "Timestamp"]

        with self.db_client.get_session() as session:

            symbol_to_id = self.db_client.get_or_create_assets(symbols, session)

            batch = []
            batch_size = 100

            for _, row in df.iterrows():
                ts = row["Timestamp"]

                for symbol in symbols:
                    value = row[symbol]

                    if value is None:
                        continue

                    record = {
                        "asset_id": symbol_to_id[symbol],
                        "timestamp": ts,
                        "timeframe": timeframe,
                        value_name: value,
                    }

                    batch.append(record)

                    if len(batch) >= batch_size:
                        self.db_client.bulk_upsert_quotes(batch, session)
                        batch.clear()

            if batch:
                self.db_client.bulk_upsert_quotes(batch, session)

def filter_dates(df, start_date=None, end_date=None):
    mask = pd.Series(True, index=df.index)
    if start_date is not None:
        mask &= df["Timestamp"] >= start_date
    if end_date is not None:
        mask &= df["Timestamp"] <= end_date
    df = df.loc[mask]
    return df

def chunks(df, size: int):
    for start in range(0, len(df), size):
        yield df.iloc[start:start + size]