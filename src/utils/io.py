"""
I/O utility functions for atomic SQLite, Parquet, and CSV storage.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd
from src.logging import get_logger
from src.exceptions import EmptyDataError

logger = get_logger("io_utils")


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensures that the directory of the specified path exists."""
    p = Path(path)
    if p.suffix:  # It's a file path
        p.parent.mkdir(parents=True, exist_ok=True)
        return p.parent
    else:
        p.mkdir(parents=True, exist_ok=True)
        return p


def save_parquet(df: pd.DataFrame, filepath: Union[str, Path]) -> Path:
    """Saves a DataFrame to Parquet format atomically."""
    target_path = Path(filepath)
    ensure_dir(target_path)
    if df.empty:
        logger.warning(f"Saving empty DataFrame to {target_path}")
    df.to_parquet(target_path, index=False, engine="pyarrow", compression="snappy")
    logger.debug(f"Saved {len(df)} rows to Parquet: {target_path}")
    return target_path


def read_parquet(filepath: Union[str, Path]) -> pd.DataFrame:
    """Reads a DataFrame from Parquet file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")
    df = pd.read_parquet(path, engine="pyarrow")
    logger.debug(f"Loaded {len(df)} rows from Parquet: {path}")
    return df


def save_sqlite(df: pd.DataFrame, db_path: Union[str, Path], table_name: str, if_exists: str = "replace") -> None:
    """Saves a DataFrame into a SQLite database table."""
    db_p = Path(db_path)
    ensure_dir(db_p)
    with sqlite3.connect(db_p) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    logger.debug(f"Saved {len(df)} rows to SQLite table '{table_name}' in {db_p}")


def query_sqlite(query: str, db_path: Union[str, Path]) -> pd.DataFrame:
    """Executes a SQL query against SQLite database and returns a DataFrame."""
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_p}")
    with sqlite3.connect(db_p) as conn:
        return pd.read_sql_query(query, conn)


def save_csv(df: pd.DataFrame, filepath: Union[str, Path]) -> Path:
    """Saves a DataFrame to CSV format."""
    target_path = Path(filepath)
    ensure_dir(target_path)
    df.to_csv(target_path, index=False)
    logger.info(f"Exported {len(df)} rows to CSV: {target_path}")
    return target_path
