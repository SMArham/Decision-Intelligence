"""
Configuration manager for pg_ad_optimizer.
Loads YAML configurations and environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except ImportError:
    _HAS_DOTENV = False

from src.exceptions import ConfigError
from src.logging import get_logger

logger = get_logger("config_loader")


class AppConfig:
    """Singleton-style Application Configuration holder."""

    def __init__(self, config_dir: Optional[str] = None):
        # Load .env file if dotenv is available
        if _HAS_DOTENV:
            try:
                load_dotenv(override=True)
            except Exception:
                pass

        self.root_dir = Path(__file__).resolve().parent.parent
        self.config_dir = Path(config_dir) if config_dir else self.root_dir / "config"

        # Load YAML files
        self.settings = self._load_yaml("settings.yaml")
        self.pg_brands = self._load_yaml("pg_brands.yaml")
        self.need_want = self._load_yaml("need_want_mapping.yaml")
        self.financials = self._load_yaml("financials.yaml")
        self.supply = self._load_yaml("supply.yaml")

        # Core Parameters
        self.project_name: str = self.settings.get("project_name", "pg_ad_optimizer")
        self.random_seed: int = int(self.settings.get("random_seed", 42))
        self.base_ad_budget: float = float(self.settings.get("base_ad_budget", 100000.0))
        self.currency: str = self.settings.get("currency", "USD")
        self.target_roi: float = float(self.settings.get("target_roi", 1.20))
        self.target_roas: float = float(self.settings.get("target_roas", 4.00))
        self.average_margin_percentage: float = float(self.settings.get("average_margin_percentage", 0.35))
        self.average_selling_price: float = float(self.settings.get("average_selling_price", 12.50))
        self.need_zone_items_limit: int = int(self.settings.get("need_zone_items_limit", 10))
        self.minimum_orders_for_confidence: int = int(self.settings.get("minimum_orders_for_confidence", 30))

        # Brand Lists
        self.include_brand_keywords: List[str] = self.pg_brands.get("include_keywords", [])
        self.exclude_brand_keywords: List[str] = self.pg_brands.get("exclude_keywords", [])

        # Need / Want Categories
        self.need_departments: List[str] = [d.lower() for d in self.need_want.get("need_departments", [])]
        self.want_departments: List[str] = [d.lower() for d in self.need_want.get("want_departments", [])]
        self.need_aisles: List[str] = [a.lower() for a in self.need_want.get("need_aisles", [])]
        self.want_aisles: List[str] = [a.lower() for a in self.need_want.get("want_aisles", [])]

        # Financials
        self.company_name: str = self.financials.get("company", "The Procter & Gamble Company")
        self.fiscal_year: str = self.financials.get("fiscal_year", "FY2024")
        self.total_revenue: float = float(self.financials.get("total_revenue", 84039000000.0))
        self.advertising_expense: float = float(self.financials.get("advertising_expense", 8560000000.0))
        self.marketing_intensity: float = float(self.financials.get("marketing_intensity", 0.101857))
        self.category_revenue_shares: Dict[str, float] = self.financials.get("category_revenue_shares", {})

        # Paths
        paths_cfg = self.settings.get("paths", {})
        self.raw_cache_dir: Path = self.root_dir / paths_cfg.get("raw_cache_dir", "data/cache")
        self.processed_dir: Path = self.root_dir / paths_cfg.get("processed_dir", "data/processed")
        self.output_dir: Path = self.root_dir / paths_cfg.get("output_dir", "data/output")
        self.sqlite_db_path: Path = self.root_dir / paths_cfg.get("sqlite_db", "data/processed/pg_ad_optimizer.db")

        # Credentials
        self.kaggle_api_token: Optional[str] = os.getenv("KAGGLE_API_TOKEN")
        self.kaggle_username: Optional[str] = os.getenv("KAGGLE_USERNAME")
        self.kaggle_key: Optional[str] = os.getenv("KAGGLE_KEY")

        # Ensure directories exist
        for d in [self.raw_cache_dir, self.processed_dir, self.output_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}. Using empty default.")
            return {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content or {}
        except Exception as e:
            raise ConfigError(f"Failed to parse YAML configuration at {filepath}: {e}")


# Global Config instance accessor
_global_config: Optional[AppConfig] = None


def get_config(config_dir: Optional[str] = None) -> AppConfig:
    global _global_config
    if _global_config is None or config_dir is not None:
        _global_config = AppConfig(config_dir=config_dir)
    return _global_config
