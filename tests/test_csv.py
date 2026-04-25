import pytest

from app.repository.csv import load_csv_to_dataframe


class TestCsvImport:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_csv_to_dataframe(file_path='doesntexist.csv')

    def test_load_close_price_csv_to_dataframe(self):
        df = load_csv_to_dataframe(file_path='files/binance_futures_close_price_1h_rest_20260116_1234.csv')
        assert df.shape == (52981, 82)

    def test_load_volume_csv_to_dataframe(self):
        df = load_csv_to_dataframe(file_path='files/binance_futures_quote_asset_volume_price_1h_rest_20260116_1234.csv')
        assert df.shape == (52981, 82)

    def test_load_metrics_csv_to_dataframe(self):
        df = load_csv_to_dataframe(file_path='files/btc_glassnode_metrics.csv')
        assert df.shape == (6157, 80)
