CREATE DATABASE iqana;
CREATE USER iqana_user WITH ENCRYPTED PASSWORD 'iqana_pw';
GRANT ALL PRIVILEGES ON DATABASE iqana TO iqana_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO iqana_user;
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    exchange VARCHAR(50),
    currency VARCHAR(10),
    asset_type VARCHAR(20),
    tick_size FLOAT,
    multiplier FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quotes (
    asset_id INT REFERENCES assets(asset_id),
    timestamp TIMESTAMPTZ NOT NULL,
    timeframe TEXT NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume NUMERIC(30, 12),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (asset_id, timeframe, timestamp)
);

CREATE INDEX idx_quotes_asset_timeframe_time ON quotes (asset_id, timeframe, timestamp DESC);