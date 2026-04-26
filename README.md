# Quant Trading Research Engine

AI-native research infrastructure: autonomous agents that collaborate to analyze datasets, generate insights, critique each other, produce structured research outputs.

## Agents

Agent examples:

- Load Agent: Agent in charge of populating the DB with the information provided in the csv
    - Prompt instructions
    You load market data when it isn't present. Only use the provided tools. You return structured JSON only.
- Analysis Agent: Agent in charge of analyzing data in the DB and generate statistics
    - Instructions
    You compute statistical metrics. Only use the provided tools. Return structured JSON only.
- Check Agent: Agent in charge of checking if there is data for the symbol and time range provided
    - Instructions
    You check if there is data for the symbol and time range provided. Only use the provided tools. Return structured JSON only.
- Reporting Agent: Agent in charge of presenting a final report on the whole flow
  - Instructions
  You are a financial reporting agent. You receive: - correlation_id - load_result - analyze_result Your task: - Produce a professional financial analysis report. - Include key metrics. - Highlight risk (volatility). - Mention if sample size is weak. - Keep structure clear. - Do NOT invent data.

## Deterministic Tools

- Load_from_file: loads quotes in csv Glassnode format and stores them in DB. Creates Asset if needed
- Asset_analysis: analyses a single Asset and generates simple statistics
   - Mean
   - std
- Asset check: counts the number of rows for the specified symbol, time range and timeframe and asserts whether there are more than 0 rows

## Running instructions

- Create venv
  
```python3.13 -m venv .venv```

```source .venv/bin/activate```
- Install requirements
  
```pip install --upgrade pip```

```pip install -r requirements.txt```

- Adapt DB configuration file
  
```config/local.yaml```

- Create Timescale DB
  
  ```docker run --hostname=53a38e76148d --env=POSTGRES_USER=timescaledb --env=POSTGRES_PASSWORD=password --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin --env=GOSU_VERSION=1.17 --env=LANG=en_US.utf8 --env=PG_MAJOR=17 --env=PG_VERSION=17.6 -- --env=DOCKER_PG_LLVM_DEPS=llvm19-dev 		clang19 --env=PGDATA=/var/lib/postgresql/data --volume=C:\Users\User\Documents\docker_volumes\timescaledb_volume:/home/postgres/pgdata/data/ --volume=/var/lib/postgresql/data --network=bridge --workdir=/ -p 5432:5432 --restart=no --label='maintainer=Timescale https://www.timescale.com' --runtime=runc -d timescale/timescaledb:latest-pg17```
  
- Exec SQL script
  
  ```sql/db_setup.sql```
  
- Run tests (uses real DB)
  
```Python -m pytest```

- Insert api key env variable in main.py
- Run application
 
```python main.py```
