import yaml
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)


def load_db_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)["database"]


def build_engine(config_path: str = "config/db_config.yaml"):
    cfg = load_db_config(config_path)
    db_type = cfg.get("type", "sqlite")

    if db_type == "sqlite":
        url = f"sqlite:///{cfg['path']}"

    elif db_type == "mysql":
        url = (
            f"mysql+pymysql://{cfg['username']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        )

    elif db_type == "oracle":
        url = (
            f"oracle+cx_oracle://{cfg['username']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/?service_name={cfg['service_name']}"
        )

    else:
        raise ValueError(f"Unsupported DB type: {db_type}")

    logger.info(f"Connecting to {db_type} database...")
    return create_engine(url)


def run_query(sql: str, config_path: str = "config/db_config.yaml") -> pd.DataFrame:
    engine = build_engine(config_path)
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    logger.info(f"Query returned {len(df)} rows.")
    return df


def get_table(table_name: str, config_path: str = "config/db_config.yaml") -> pd.DataFrame:
    return run_query(f"SELECT * FROM {table_name}", config_path)