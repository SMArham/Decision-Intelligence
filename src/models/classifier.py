"""
Machine Learning Classifier for Need vs Want item propensity.
Trains a model to predict the probability of an item belonging to the Essential Need zone.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from src.config import get_config
from src.logging import get_logger

logger = get_logger("ml_classifier")


class NeedPropensityClassifier:
    """Classifies items into Need vs Want propensity based on cart position and item signals."""

    def __init__(self):
        self.config = get_config()
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=6,
            random_state=self.config.random_seed,
            class_weight="balanced"
        )
        self.feature_names = [
            "add_to_cart_order",
            "basket_size",
            "relative_cart_position",
            "reordered",
            "department_id",
            "aisle_id",
        ]
        self.is_trained = False
        self.metrics: Dict[str, float] = {}

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Extracts numerical features and target variable."""
        df_feat = df.copy()
        
        if "relative_cart_position" not in df_feat.columns:
            df_feat["relative_cart_position"] = df_feat["add_to_cart_order"] / df_feat["basket_size"].replace(0, 1)

        # Fallbacks for missing columns
        for col in self.feature_names:
            if col not in df_feat.columns:
                df_feat[col] = 0

        X = df_feat[self.feature_names].fillna(0)

        y = None
        if "is_need_department" in df_feat.columns:
            y = df_feat["is_need_department"].astype(int)

        return X, y

    def train(self, df_features: pd.DataFrame) -> Dict[str, float]:
        """Trains the Random Forest classifier and records evaluation metrics."""
        X, y = self.prepare_features(df_features)

        if y is None or len(np.unique(y)) < 2:
            logger.warning("Insufficient distinct target classes to train ML classifier. Skipping.")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=self.config.random_seed, stratify=y
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        }

        logger.info(f"Trained Need Classifier: Accuracy={self.metrics['accuracy']:.2%}, ROC-AUC={self.metrics['roc_auc']:.3f}")
        return self.metrics

    def predict_propensity(self, df_features: pd.DataFrame) -> np.ndarray:
        """Returns predicted probability of being an Essential Need item."""
        if not self.is_trained:
            logger.warning("Model not yet trained. Returning default rule-based proxy.")
            return np.where(df_features["add_to_cart_order"] <= 10, 0.85, 0.20)
        X, _ = self.prepare_features(df_features)
        return self.model.predict_proba(X)[:, 1]

    def save(self, filepath: Path) -> None:
        """Saves trained model artifact."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "metrics": self.metrics, "features": self.feature_names}, filepath)
        logger.info(f"Saved ML model artifact to {filepath}")
