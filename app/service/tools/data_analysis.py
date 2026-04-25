import logging

from app.repository.db import PostgresClient

logger = logging.getLogger(__name__)

class AssetAnalysis:

    def __init__(self, db_client: PostgresClient, correlation_uuid: str):
        self.db_client = db_client
        self.correlation_uuid = correlation_uuid

    def process(self, symbol, timeframe, start_date = None, end_date = None) -> dict:
        try:
            logger.info(f"{self.correlation_uuid}: Processing asset: {symbol}, start_date: {start_date}, end_date: {end_date}")
            df = self.db_client.get_quotes(symbol, timeframe, start_date, end_date)
            message = f"{self.correlation_uuid}: Finished processing asset: {symbol}, start_date: {start_date}, end_date: {end_date}"
            logger.info(message)
            result = {
                'correlation_uuid': self.correlation_uuid,
                'asset': symbol,
                'mean': df["close"].mean(),
                'volatility': df["close"].std()
            }
            logger.info(result)
            return result
        except Exception as e:
            message = f"{self.correlation_uuid}: Failed asset processing asset: {symbol}, start_date: {start_date}, end_date: {end_date} with message: {str(e)}"
            logger.error(message)
            raise Exception(message)

    def check(self, symbol, timeframe, start_date = None, end_date = None) -> dict:
        try:
            logger.info(f"{self.correlation_uuid}: Checking asset: {symbol}, start_date: {start_date}, end_date: {end_date}")
            df = self.db_client.get_quotes(symbol, timeframe, start_date, end_date)
            message = f"{self.correlation_uuid}: Finished checking asset: {symbol}, start_date: {start_date}, end_date: {end_date}"
            logger.info(message)
            result = {
                'correlation_uuid': self.correlation_uuid,
                'asset': symbol,
                'enough_data': len(df) > 0
            }
            logger.info(result)
            return result
        except Exception as e:
            message = f"{self.correlation_uuid}: Failed checking asset: {symbol}, start_date: {start_date}, end_date: {end_date} with message: {str(e)}"
            logger.error(message)
            raise Exception(message)