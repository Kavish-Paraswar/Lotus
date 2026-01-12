# Scoring Engine - Technical Assessment Submission

This submission implements YAML logic specifications as a **deterministic compilation task**, not a design exercise. The Scoring Engine translates formal specifications into production-grade Python with zero interpretation, creative liberty, or assumption-making beyond what is required for correctness.

## Overview

**What This Does:**
- Implements a production-ready ScoringEngine that normalizes predictions using z-score method, applies confidence adjustments, filters based on thresholds, and clips output to specified bounds
- Enforces a guardrail layer that validates schema correctness, prevents specification violations, and ensures deterministic behavior
- Analyzes three faulty specifications to document why they cannot be deterministically implemented

**Key Principle:**
Act as a **compiler, not a designer**. Translate exactly what is specified, flag ambiguities rather than resolve them, and reject incomplete specifications before implementation.

---

## Project Structure

```
submission/
├── part1/
│   ├── scoring_engine.py          # Main ScoringEngine implementation
│   └── test_scoring_engine.py     # Comprehensive unit tests
├── part2/
│   ├── guardrails.py              # Validation and guardrail framework
│   └── test_guardrails.py         # Guardrail violation detection tests
├── part3/
│   └── error_analysis.md          # Analysis of three faulty specs
└── README.md                      # This file
```

---

## Part 1: Scoring Engine Implementation

### What It Does

The `ScoringEngine` class processes predictions and applies deterministic transformations:

1. **Input Validation** - Ensures all predictions conform to schema (ticker, raw_score, confidence, sector)
2. **Sector-wise Z-Score Normalization** - Normalizes scores within each sector independently
3. **Confidence Adjustment** - Multiplies normalized score by confidence value
4. **Filtering** - Excludes predictions failing these conditions:
   - `confidence >= 0.3`
   - `abs(normalized_score) >= 0.5`
5. **Output Bounds** - Clips final scores to [-3.0, 3.0]

### Mathematical Formula

```
normalized_score = (raw_score - sector_mean) / sector_stddev
final_score = normalized_score * confidence
final_score = clip(final_score, -3.0, 3.0)
```

### Usage

```python
from scoring_engine import ScoringEngine

engine = ScoringEngine(min_bound=-3.0, max_bound=3.0, clip=True)

predictions = [
    {"ticker": "AAPL", "raw_score": 0.85, "confidence": 0.95, "sector": "TECH"},
    {"ticker": "MSFT", "raw_score": 0.72, "confidence": 0.88, "sector": "TECH"},
    {"ticker": "JPM", "raw_score": 0.65, "confidence": 0.25, "sector": "FINANCE"},
]

results = engine.process(predictions)
```

### Running Tests

```bash
cd part1
pytest test_scoring_engine.py -v
```

Tests cover:
- Normal operation with mixed sectors
- Edge cases (single sector, identical scores, division by zero)
- Boundary conditions (min/max bounds, clipping)
- Invalid inputs (missing fields, wrong types, invalid confidence)

---

## Part 2: Guardrail Implementation

### What It Does

The `Guardrail` class enforces logic boundaries through static and runtime validation:

**Static Analysis:**
- Detects forbidden imports (`random`, `requests`, `http`)
- Detects unauthorized hardcoded float literals
- Detects external API calls
- Validates syntax

**Runtime Validation:**
- Validates input schema (required fields, correct types)
- Validates output schema (correct structure and types)
- Ensures reproducible outputs

### Usage

```python
from guardrails import Guardrail

# Static check on code string
issues = Guardrail.static_check(code_str)
if issues:
    print(f"Found violations: {issues}")

# Runtime input validation
Guardrail.runtime_validate_inputs(predictions)

# Runtime output validation
Guardrail.runtime_validate_outputs(results)
```

### Running Tests

```bash
cd part2
pytest test_guardrails.py -v
```

Tests verify:
- Detection of forbidden imports
- Detection of hardcoded literals outside spec
- Rejection of malformed inputs
- Enforcement of output schema

---

## Part 3: Faulty Specifications Analysis

Three YAML specifications were analyzed to document why they cannot be deterministically implemented:

### Faulty Spec 1: RiskManager

**Problem:** References undefined "optimal_kelly_fraction" formula and uses undefined variables

**Why It Fails:** Kelly fraction formula requires explicit inputs (win probability, payout odds); no such inputs are specified

**Required Questions:**
- What is the exact formula for optimal_kelly_fraction?
- What are the input parameters and their units?
- What are the ranges for position size?

### Faulty Spec 2: PortfolioBuilder

**Problem:** Specifies allocation using subjective phrase "use best judgment"

**Why It Fails:** "Best judgment" is not a deterministic algorithm and cannot be compiled

**Required Questions:**
- What is the objective function? (Maximize Sharpe, minimize variance, etc.)
- What are the constraints? (Risk budget, liquidity, sector caps)
- What data sources are available?

### Faulty Spec 3: ExecutionEngine

**Problem:** Uses vague conditions like "market is favorable" and "minimize as much as possible"

**Why It Fails:** No quantifiable thresholds or objective metrics provided

**Required Questions:**
- How is "market is favorable" defined? (Specific indicators and thresholds)
- What is the target slippage in basis points?
- What are the execution time constraints?

See [error_analysis.md](part3/error_analysis.md) for complete analysis.

---

## How to Run Everything

### Setup
```bash
pip install pytest
```

### Run All Tests
```bash
pytest -v
```

### Run Specific Tests
```bash
pytest part1/test_scoring_engine.py -v
pytest part2/test_guardrails.py -v
```

---

## Key Implementation Details

### Why Z-Score (Not Min-Max)

Z-score normalization is specified in the YAML. It handles outliers better and produces unbounded values that are then clipped, matching the spec exactly.

### Population vs Sample Standard Deviation

Implementation uses population stddev (dividing by n, not n-1) as this is the standard for normalization when treating a sector's data as the complete population for that scoring window.



