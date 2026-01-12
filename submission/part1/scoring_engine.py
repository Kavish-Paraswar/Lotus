from typing import List, Dict, Any, Tuple
from math import sqrt

class ScoringEngine:
    def __init__(self, min_bound: float = -3.0, max_bound: float = 3.0, clip: bool = True, strict: bool = False):
        self.min_bound = float(min_bound)
        self.max_bound = float(max_bound)
        self.clip = bool(clip)
        self.strict = bool(strict)

    @staticmethod
    def _validate_prediction_item(item: Dict[str, Any]) -> None:
        if not isinstance(item, dict):
            raise ValueError("prediction must be a dict")
        required_keys = {"ticker", "raw_score", "confidence", "sector"}
        missing = required_keys - set(item.keys())
        if missing:
            raise ValueError(f"missing keys in prediction: {sorted(list(missing))}")
        if not isinstance(item["ticker"], str):
            raise ValueError("ticker must be a string")
        if not isinstance(item["sector"], str):
            raise ValueError("sector must be a string")
        try:
            float(item["raw_score"])
        except Exception:
            raise ValueError("raw_score must be convertible to float")
        try:
            confidence = float(item["confidence"])
        except Exception:
            raise ValueError("confidence must be convertible to float")
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError("confidence must be in [0.0, 1.0]")

    @staticmethod
    def _population_stddev(values: List[float]) -> float:
        n = len(values)
        if n == 0:
            return 0.0
        mean = sum(values) / n
        var = sum((x - mean) ** 2 for x in values) / n
        return sqrt(var)

    def process(self, predictions: List[Dict[str, Any]], return_metadata: bool = False) -> Any:
        if not isinstance(predictions, list):
            raise ValueError("predictions must be a list")
        for item in predictions:
            self._validate_prediction_item(item)

        sectors = {}
        for item in predictions:
            s = item["sector"]
            sectors.setdefault(s, []).append(float(item["raw_score"]))

        sector_stats = {}
        for s, vals in sectors.items():
            mean = sum(vals) / len(vals) if len(vals) > 0 else 0.0
            stddev = self._population_stddev(vals)
            sector_stats[s] = {"mean": mean, "stddev": stddev, "count": len(vals)}

        output = []
        for item in predictions:
            ticker = item["ticker"]
            sector = item["sector"]
            raw = float(item["raw_score"])
            confidence = float(item["confidence"])
            stats = sector_stats.get(sector, {"mean": 0.0, "stddev": 0.0})
            sector_mean = stats["mean"]
            sector_stddev = stats["stddev"]

            if sector_stddev == 0.0:
                if self.strict:
                    raise ValueError(f"stddev is zero for sector {sector}")
                normalized_score = 0.0
            else:
                normalized_score = (raw - sector_mean) / sector_stddev

            confidence_adjusted = normalized_score * confidence

            reasons = []
            if confidence < 0.3:
                reasons.append("low_confidence")
            if abs(normalized_score) < 0.5:
                reasons.append("low_magnitude")

            excluded = False
            exclusion_reason = None
            if reasons:
                excluded = True
                exclusion_reason = "; ".join(reasons)

            final_score = confidence_adjusted
            if self.clip:
                if final_score < self.min_bound:
                    final_score = self.min_bound
                if final_score > self.max_bound:
                    final_score = self.max_bound

            output.append({
                "ticker": ticker,
                "final_score": float(final_score),
                "sector": sector,
                "excluded": bool(excluded),
                "exclusion_reason": exclusion_reason
            })

        if return_metadata:
            return {
                "results": output,
                "metadata": {
                    "sector_stats": sector_stats,
                    "config": {
                        "min_bound": self.min_bound,
                        "max_bound": self.max_bound,
                        "clip": self.clip,
                        "strict": self.strict
                    }
                }
            }

        return output
