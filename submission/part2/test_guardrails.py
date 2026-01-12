import pytest
from guardrails import Guardrail, GuardrailError

def test_static_detects_random_import():
    code = "import random\nx = random.random()"
    issues = Guardrail.static_check(code)
    assert "forbidden_import_random" in issues

def test_static_detects_forbidden_float():
    code = "x = 2.71828\n"
    issues = Guardrail.static_check(code)
    assert any(i.startswith("forbidden_float_literal") for i in issues)

def test_runtime_input_validation_accepts_valid():
    preds = [{"ticker": "A", "raw_score": 1.0, "confidence": 0.5, "sector": "S"}]
    Guardrail.runtime_validate_inputs(preds)

def test_runtime_input_validation_rejects_bad_confidence():
    preds = [{"ticker": "A", "raw_score": 1.0, "confidence": 1.5, "sector": "S"}]
    with pytest.raises(GuardrailError):
        Guardrail.runtime_validate_inputs(preds)

def test_runtime_output_validation_accepts_valid():
    outputs = [{"ticker": "A", "final_score": 0.0, "sector": "S", "excluded": False, "exclusion_reason": None}]
    Guardrail.runtime_validate_outputs(outputs)

def test_runtime_output_validation_rejects_bad_types():
    outputs = [{"ticker": "A", "final_score": "bad", "sector": "S", "excluded": False, "exclusion_reason": None}]
    with pytest.raises(GuardrailError):
        Guardrail.runtime_validate_outputs(outputs)
