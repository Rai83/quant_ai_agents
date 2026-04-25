from datetime import datetime
from typing import Annotated, Any

import pandas as pd
from pandas import DataFrame
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.domain.entities import Asset, Quote
# requires psycopg2


class PostgresClient:

    def __init__(self, username, password, host, port, database):
        connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(connection_string)

    def get_by_id(self, _id: int) -> type[Asset] | None:
        with Session(self.engine) as session:
            return session.get(Asset, _id)

    def get_by_symbol(self, symbol: str) -> type[Asset] | None:
        with Session(self.engine) as session:
            stmt = select(Asset).where(Asset.symbol == symbol)
            return session.execute(stmt).scalar_one_or_none()

    def insert(self, asset: Asset):
        with Session(self.engine) as session:
            session.add(asset)
            session.commit()

    def delete_by_id(self, _id: int):
        with Session(self.engine) as session:
            persisted_asset = session.get(Asset, _id)
            if not persisted_asset:
                print(f"No such asset: {_id}")
                return
            session.delete(persisted_asset)
            session.commit()

    def update(self, _id: int, asset: Asset):
        with Session(self.engine) as session:
            persisted_asset = session.get(Asset, _id)
            if not persisted_asset:
                print(f"No such asset: {_id}")
                return
            if asset.asset_type:
                persisted_asset.asset_type= asset.asset_type
            if asset.name:
                persisted_asset.name = asset.name
            if asset.symbol:
                persisted_asset.symbol = asset.symbol
            if asset.currency:
                persisted_asset.currency = asset.currency
            if asset.exchange:
                persisted_asset.exchange = asset.exchange
            if asset.multiplier:
                persisted_asset.multiplier = asset.multiplier
            if asset.tick_size:
                persisted_asset.tick_size = asset.tick_size
            session.commit()

    def upsert_quote(self, quote: dict, session) -> None:
        stmt = insert(Quote).values(**quote)

        update_values = {
            k: stmt.excluded[k]
            for k, v in quote.items()
            if v is not None and k not in ("asset_id", "timestamp", "timeframe")
        }

        if update_values:
            stmt = stmt.on_conflict_do_update(
                index_elements=["asset_id", "timeframe", "timestamp"],
                set_=update_values,
            )
        else:
            stmt = stmt.on_conflict_do_nothing()

        session.execute(stmt)
        session.commit()

    def bulk_upsert_quotes(self, quotes: list[dict], session: Session) -> None:
        if not quotes:
            return

        stmt = insert(Quote).values(quotes)
        updatable_columns = set().union(*(q.keys() for q in quotes))
        conflict_keys = {"asset_id", "timeframe", "timestamp"}

        update_cols = {
            col: getattr(stmt.excluded, col)
            for col in updatable_columns
            if col not in conflict_keys
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["asset_id", "timeframe", "timestamp"],
            set_=update_cols,
        )

        session.execute(stmt)
        session.commit()

    def get_quotes(
            self,
            symbol: str,
            timeframe: str,
            start: datetime | None = None,
            end: datetime | None = None,
    ) -> DataFrame:

        with Session(self.engine) as session:
            conditions = [
                Asset.symbol == symbol,
                Quote.timeframe == timeframe,
            ]

            if start is not None:
                conditions.append(Quote.timestamp >= start)

            if end is not None:
                conditions.append(Quote.timestamp <= end)

            stmt = (
                select(
                    Quote.asset_id,
                    Asset.symbol,
                    Quote.timeframe,
                    Quote.timestamp,
                    Quote.open,
                    Quote.high,
                    Quote.low,
                    Quote.close,
                    Quote.volume,
                    Quote.created_at
                )
                .join(Asset, Quote.asset_id == Asset.asset_id)
                .where(*conditions)
                .order_by(Quote.timestamp.asc())
            )

            df = pd.read_sql(stmt, session.bind)
            return df

    def get_or_create_assets(self, symbols: list[str], session: Session) -> dict[str, int]:
        result = {}

        existing = session.execute(
            select(Asset.symbol, Asset.asset_id)
            .where(Asset.symbol.in_(symbols))
        ).all()

        result.update({symbol: asset_id for symbol, asset_id in existing})

        missing = [s for s in symbols if s not in result]
        for symbol in missing:
            stmt = insert(Asset).values(symbol=symbol).returning(Asset.asset_id)
            try:
                asset_id = session.execute(stmt).scalar_one()
                result[symbol] = asset_id
            except IntegrityError:
                session.rollback()
                asset_id = session.execute(
                    select(Asset.asset_id).where(Asset.symbol == symbol)
                ).scalar_one()
                result[symbol] = asset_id

        session.commit()
        return result

    def get_session(self) -> Session:
        return Session(self.engine)

