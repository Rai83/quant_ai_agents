from app.domain.entities import Asset
from app.repository.db import PostgresClient


def create_client() -> PostgresClient:
    return PostgresClient('iqana_user', 'iqana_pw', '127.0.0.1', '5432', 'iqana')


class TestDbClient:

    def test_insert(self):
        client = create_client()
        insert_asset(client)
        returned_asset = client.get_by_symbol('DOCU')
        assert returned_asset.symbol == 'DOCU'
        client.delete_by_id(returned_asset.asset_id)

def insert_asset(client):
    asset = Asset(symbol='DOCU', name='Docusign', exchange='exchange', currency='USD', multiplier=12)
    client.insert(asset)