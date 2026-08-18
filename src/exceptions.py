"""
Custom exceptions for pg_ad_optimizer pipeline.
"""


class PGAdOptimizerError(Exception):
    """Base exception class for all errors in pg_ad_optimizer."""
    pass


class KaggleAuthError(PGAdOptimizerError):
    """Raised when Kaggle authentication fails or credentials are missing."""
    pass


class DatasetAccessError(PGAdOptimizerError):
    """Raised when Kaggle dataset download fails or rules are not accepted."""
    pass


class MissingColumnError(PGAdOptimizerError):
    """Raised when an expected column is missing from input or intermediate data."""
    pass


class EmptyDataError(PGAdOptimizerError):
    """Raised when a dataset or filtered view contains zero records."""
    pass


class ConfigError(PGAdOptimizerError):
    """Raised when a YAML or environment configuration is invalid or missing."""
    pass


class BrandMappingError(PGAdOptimizerError):
    """Raised when P&G brand regex mapping fails or generates anomalies."""
    pass


class BudgetCalculationError(PGAdOptimizerError):
    """Raised when budget optimization or ROI constraints fail mathematical limits."""
    pass


class DashboardDataError(PGAdOptimizerError):
    """Raised when data required by Streamlit dashboard is missing or corrupt."""
    pass
