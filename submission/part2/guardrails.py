import ast
from typing import List, Dict, Any

class GuardrailError(Exception):
    pass

class Guardrail:
    ALLOWED_FLOATS = {0.3, 0.5, -3.0, 3.0, 0.0, 1.0}

    @staticmethod
    def static_check(code: str) -> List[str]:
        issues = []
        try:
            tree = ast.parse(code)
        except Exception as e:
            issues.append(f"syntax_error: {e}")
            return issues
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name == "random":
                        issues.append("forbidden_import_random")
                    if name in ("requests", "http"):
                        issues.append(f"forbidden_import_{name}")
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "random":
                    issues.append("forbidden_import_random")
                if "requests" in module or "http" in module:
                    issues.append(f"forbidden_import_{module}")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("get", "post") and isinstance(node.func.value, ast.Name) and node.func.value.id == "requests":
                        issues.append("forbidden_requests_call")
            if isinstance(node, ast.Constant):
                if isinstance(node.value, float):
                    if float(node.value) not in Guardrail.ALLOWED_FLOATS:
                        issues.append(f"forbidden_float_literal:{node.value}")
        return sorted(set(issues))

    @staticmethod
    def runtime_validate_inputs(predictions: List[Dict[str, Any]]) -> None:
        if not isinstance(predictions, list):
            raise GuardrailError("inputs_must_be_list")
        for item in predictions:
            if not isinstance(item, dict):
                raise GuardrailError("each_prediction_must_be_dict")
            required = {"ticker", "raw_score", "confidence", "sector"}
            if not required.issubset(set(item.keys())):
                raise GuardrailError("input_schema_mismatch")
            if not isinstance(item["ticker"], str):
                raise GuardrailError("ticker_must_be_string")
            if not isinstance(item["sector"], str):
                raise GuardrailError("sector_must_be_string")
            try:
                float(item["raw_score"])
            except Exception:
                raise GuardrailError("raw_score_must_be_numeric")
            try:
                c = float(item["confidence"])
            except Exception:
                raise GuardrailError("confidence_must_be_numeric")
            if c < 0.0 or c > 1.0:
                raise GuardrailError("confidence_out_of_bounds")

    @staticmethod
    def runtime_validate_outputs(outputs: List[Dict[str, Any]]) -> None:
        if not isinstance(outputs, list):
            raise GuardrailError("outputs_must_be_list")
        for item in outputs:
            required = {"ticker", "final_score", "sector", "excluded", "exclusion_reason"}
            if not required.issubset(set(item.keys())):
                raise GuardrailError("output_schema_mismatch")
            if not isinstance(item["ticker"], str):
                raise GuardrailError("output_ticker_type")
            try:
                float(item["final_score"])
            except Exception:
                raise GuardrailError("final_score_must_be_numeric")
            if not isinstance(item["sector"], str):
                raise GuardrailError("output_sector_type")
            if not isinstance(item["excluded"], bool):
                raise GuardrailError("excluded_must_be_bool")
            if item["exclusion_reason"] is not None and not isinstance(item["exclusion_reason"], str):
                raise GuardrailError("exclusion_reason_type")
