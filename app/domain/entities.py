from datetime import datetime

from sqlalchemy import String, Float, TIMESTAMP, func, Integer, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    exchange: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    asset_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    tick_size: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    multiplier: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    def __repr__(self):
        return (
            f"<Asset id={self.asset_id} "
            f"symbol='{self.symbol}'>"
            f"name={self.name} "
            f"exchange={self.exchange} "
            f"currency={self.currency} "
            f"asset_type={self.asset_type} "
            f"tick_size={self.tick_size} "
            f"multiplier={self.multiplier} "
            f"created_at={self.created_at} "
        )

class Quote(Base):
    __tablename__ = "quotes"

    asset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assets.asset_id"),
        primary_key=True
    )

    timeframe: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True
    )

    open: Mapped[float | None] = mapped_column(Float, nullable=True)
    high: Mapped[float | None] = mapped_column(Float, nullable=True)
    low: Mapped[float | None] = mapped_column(Float, nullable=True)
    close: Mapped[float | None] = mapped_column(Float, nullable=True)

    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Quote(asset_id={self.asset_id}, timeframe='{self.timeframe}', "
            f"timestamp={self.timestamp.isoformat()}, open={self.open}, "
            f"high={self.high}, low={self.low}, close={self.close}, volume={self.volume})>"
        )
