"""
Fuzzy Logic Expert System for Smooth Continuous Budget Multiplier Inference.
Implements Fuzzification, Mamdani IF-THEN Inference, and Centroid Defuzzification.
Prevents rigid step-function cliffs between discrete multiplier tiers.
"""

from typing import Dict, Tuple
import numpy as np
from src.logging import get_logger

logger = get_logger("fuzzy_engine")


def _triangular_membership(x: float, a: float, b: float, c: float) -> float:
    """Computes triangular fuzzy membership degree in range [0, 1]."""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a) if b > a else 1.0
    else:
        return (c - x) / (c - b) if c > b else 1.0


def _trapezoidal_membership(x: float, a: float, b: float, c: float, d: float) -> float:
    """Computes trapezoidal fuzzy membership degree in range [0, 1]."""
    if x <= a or x >= d:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a) if b > a else 1.0
    elif b < x <= c:
        return 1.0
    else:
        return (d - x) / (d - c) if d > c else 1.0


class FuzzyBudgetInferenceSystem:
    """
    Mamdani Fuzzy Logic Expert System for continuous ad budget multiplier evaluation.
    Inputs:
      - Demand Need Share (0.0 to 1.0)
      - Supply Availability Score (0.0 to 1.2)
    Output:
      - Continuous Budget Multiplier (0.0 to 1.65)
    """

    def __init__(self):
        pass

    def fuzzify_demand(self, share: float) -> Dict[str, float]:
        """Calculates membership for Demand: Low, Moderate, High, Dominant."""
        s = max(0.0, min(1.0, float(share)))
        return {
            "low": _trapezoidal_membership(s, -0.1, 0.0, 0.10, 0.25),
            "moderate": _triangular_membership(s, 0.15, 0.35, 0.55),
            "high": _triangular_membership(s, 0.45, 0.65, 0.85),
            "dominant": _trapezoidal_membership(s, 0.75, 0.85, 1.0, 1.1),
        }

    def fuzzify_supply(self, score: float) -> Dict[str, float]:
        """Calculates membership for Supply: Critical, Constrained, Healthy, Surplus."""
        sc = max(0.0, min(1.5, float(score)))
        return {
            "critical": _trapezoidal_membership(sc, -0.1, 0.0, 0.50, 0.65),
            "constrained": _triangular_membership(sc, 0.55, 0.70, 0.85),
            "healthy": _triangular_membership(sc, 0.75, 0.95, 1.05),
            "surplus": _trapezoidal_membership(sc, 0.95, 1.05, 1.5, 2.0),
        }

    def evaluate_fuzzy_multiplier(self, need_share: float, supply_score: float) -> float:
        """
        Applies fuzzy rule base and computes crisp output using Centroid Defuzzification.
        Rules:
          R1: IF Supply is Critical -> Multiplier is ZERO (0.0)
          R2: IF Supply is Constrained & Demand is Low -> Multiplier is MINIMAL (0.3)
          R3: IF Supply is Constrained & Demand is High -> Multiplier is HALF (0.6)
          R4: IF Supply is Healthy & Demand is Low -> Multiplier is AWARENESS_BOOST (1.4)
          R5: IF Supply is Healthy & Demand is Moderate -> Multiplier is NORMAL (1.0)
          R6: IF Supply is Healthy & Demand is High -> Multiplier is EXPANSION (1.35)
          R7: IF Supply is Healthy & Demand is Dominant -> Multiplier is MAINTAIN (0.85)
          R8: IF Supply is Surplus & Demand is High -> Multiplier is SURPLUS_MAX (1.50)
        """
        dem = self.fuzzify_demand(need_share)
        sup = self.fuzzify_supply(supply_score)

        # Rule Activations (Mamdani Min Operator)
        # Consequent representative centers for singleton defuzzification
        rules = [
            (sup["critical"], 0.0),                                                # R1: Stockout protection
            (min(sup["constrained"], dem["low"]), 0.25),                          # R2
            (min(sup["constrained"], max(dem["moderate"], dem["high"])), 0.55),    # R3
            (min(sup["healthy"], dem["low"]), 1.45),                              # R4: Awareness push
            (min(sup["healthy"], dem["moderate"]), 1.00),                         # R5: Normal
            (min(sup["healthy"], dem["high"]), 1.35),                             # R6: Growth
            (min(sup["healthy"], dem["dominant"]), 0.85),                         # R7: Maintain
            (min(sup["surplus"], max(dem["moderate"], dem["high"])), 1.50),       # R8: Aggressive
        ]

        # Centroid Defuzzification: Sum(weight * center) / Sum(weight)
        numerator = sum(weight * center for weight, center in rules)
        denominator = sum(weight for weight, _ in rules)

        if denominator == 0:
            return 1.0

        fuzzy_multiplier = round(float(numerator / denominator), 3)
        return fuzzy_multiplier
