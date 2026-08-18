"""
Kaggle Client for dataset retrieval and credentials management.
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional
from src.config import get_config
from src.exceptions import KaggleAuthError, DatasetAccessError
from src.logging import get_logger
from src.utils.retry import retry_with_backoff

logger = get_logger("kaggle_client")


class KaggleClient:
    """Manages authentication and automated downloading from Kaggle."""

    def __init__(self):
        self.config = get_config()
        self._setup_credentials()

    def _setup_credentials(self) -> None:
        """Sets up Kaggle credentials directory ~/.kaggle and environment variables."""
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(parents=True, exist_ok=True)

        # 1. Check for Modern Kaggle API Token
        token = self.config.kaggle_api_token
        if token:
            os.environ["KAGGLE_API_TOKEN"] = token
            access_token_path = kaggle_dir / "access_token"
            try:
                with open(access_token_path, "w", encoding="utf-8") as f:
                    f.write(token.strip())
                logger.info(f"Kaggle access token configured at {access_token_path}")
            except Exception as e:
                logger.warning(f"Could not write to ~/.kaggle/access_token: {e}")

        # 2. Check for Legacy Username/Key
        username = self.config.kaggle_username
        key = self.config.kaggle_key
        if username and key:
            os.environ["KAGGLE_USERNAME"] = username
            os.environ["KAGGLE_KEY"] = key
            kaggle_json_path = kaggle_dir / "kaggle.json"
            try:
                import json
                with open(kaggle_json_path, "w", encoding="utf-8") as f:
                    json.dump({"username": username, "key": key}, f)
                logger.info(f"Kaggle kaggle.json configured at {kaggle_json_path}")
            except Exception as e:
                logger.warning(f"Could not write to ~/.kaggle/kaggle.json: {e}")

    @retry_with_backoff(retries=2, initial_delay=2.0, exceptions=(Exception,))
    def download_dataset(self, dataset_slug: str = "psparks/instacart-market-basket-analysis", destination: Optional[Path] = None) -> Path:
        """
        Attempts to download Instacart dataset via Kaggle API / kagglehub.
        """
        dest_dir = destination or self.config.raw_cache_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Attempting to download dataset '{dataset_slug}' into {dest_dir}...")

        # Try kagglehub first
        try:
            import kagglehub
            download_path = kagglehub.dataset_download(dataset_slug)
            logger.info(f"Dataset successfully downloaded via kagglehub to {download_path}")
            # Copy extracted files to destination
            src_p = Path(download_path)
            for item in src_p.glob("*"):
                if item.is_file():
                    shutil.copy(item, dest_dir / item.name)
            return dest_dir
        except Exception as e:
            logger.warning(f"kagglehub download attempt failed: {e}. Trying kaggle CLI / API...")

        # Try kaggle package
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            api.dataset_download_files(dataset_slug, path=str(dest_dir), unzip=True)
            logger.info(f"Dataset downloaded successfully via Kaggle API to {dest_dir}")
            return dest_dir
        except Exception as e:
            msg = (
                f"Failed to download Kaggle dataset '{dataset_slug}'.\n"
                f"Reason: {e}\n"
                f"Action Required:\n"
                f"1. Verify Kaggle API token in .env\n"
                f"2. Ensure you have accepted rules for '{dataset_slug}' on Kaggle website."
            )
            logger.error(msg)
            raise DatasetAccessError(msg)
