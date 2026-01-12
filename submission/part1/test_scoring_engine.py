import pytest
from scoring_engine import ScoringEngine


def test_empty_input():
    engine = ScoringEngine()
    result = engine.process([])
    assert result == []

def test_basic_operation():
    engine = ScoringEngine()
    preds = [
        {"ticker": "AAA", "raw_score": 10.0, "confidence": 0.8, "sector": "X"},
        {"ticker": "BBB", "raw_score": 12.0, "confidence": 0.9, "sector": "X"},
        {"ticker": "CCC", "raw_score": 8.0, "confidence": 0.95, "sector": "X"},
    ]
    out = engine.process(preds)
    assert len(out) == 3
    assert all("final_score" in r for r in out)
    for r in out:
        assert isinstance(r["final_score"], float)
        assert r["excluded"] in (True, False)

def test_stddev_zero():
    engine = ScoringEngine()
    preds = [
        {"ticker": "S1", "raw_score": 5.0, "confidence": 0.5, "sector": "Z"},
        {"ticker": "S2", "raw_score": 5.0, "confidence": 0.4, "sector": "Z"},
    ]
    out = engine.process(preds)
    assert out[0]["final_score"] == 0.0
    assert out[1]["final_score"] == 0.0

def test_invalid_input_type():
    engine = ScoringEngine()
    with pytest.raises(ValueError):
        engine.process("not a list")

def test_confidence_range_violation():
    engine = ScoringEngine()
    preds = [{"ticker": "X", "raw_score": 1.0, "confidence": 1.5, "sector": "A"}]
    with pytest.raises(ValueError):
        engine.process(preds)

def test_exclusion_reasons_order_and_combination():
    engine = ScoringEngine()
    preds = [
        {"ticker": "T1", "raw_score": 0.0, "confidence": 0.2, "sector": "A"},
        {"ticker": "T2", "raw_score": 0.0, "confidence": 0.4, "sector": "A"},
    ]
    out = engine.process(preds)
    assert out[0]["excluded"] is True
    assert out[0]["exclusion_reason"] == "low_confidence; low_magnitude"
    assert out[1]["excluded"] is True
    assert out[1]["exclusion_reason"] == "low_magnitude"
