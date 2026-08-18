"""
Data loading and persistence into SQLite data mart and Parquet cache.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from src.config import get_config
from src.logging import get_logger
from src.utils.io import save_parquet, save_sqlite

logger = get_logger("data_loader")


def persist_data_mart(
    tables: Dict[str, pd.DataFrame],
    db_path: Optional[Path] = None,
    cache_dir: Optional[Path] = None
) -> None:
    """
    Persists DataFrames to both SQLite database tables and Parquet cache files.
    """
    config = get_config()
    db_p = db_path or config.sqlite_db_path
    cache_p = cache_dir or config.raw_cache_dir

    logger.info(f"Persisting data mart into SQLite database: {db_p}")

    for table_name, df in tables.items():
        if df is None or df.empty:
            logger.debug(f"Skipping empty table '{table_name}'")
            continue

        # 1. Save to SQLite
        try:
            save_sqlite(df, db_p, table_name, if_exists="replace")
        except Exception as e:
            logger.error(f"Failed to persist table '{table_name}' to SQLite: {e}")

        # 2. Save to Parquet Cache
        try:
            parquet_path = cache_p / f"{table_name}.parquet"
            save_parquet(df, parquet_path)
        except Exception as e:
            logger.error(f"Failed to persist table '{table_name}' to Parquet: {e}")

    logger.info("Data mart persistence successfully completed.")
