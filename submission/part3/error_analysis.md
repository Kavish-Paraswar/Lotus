# Error Analysis - Faulty Specifications

## Spec 1: RiskManager

### What is missing or ambiguous

The spec mentions "optimal_kelly_fraction" as a formula but never defines it. There's no actual equation, no input parameters (like win probability or payout odds)—nothing to work with.

Also, the constraint `position <= max_size` uses variables that are never defined. What's `max_size`? What's `position`? What are the units? There's no context.

### Why it cannot be deterministically implemented

I can't invent a Kelly fraction formula if it's not in the spec. Kelly fraction needs specific inputs and a clear mathematical definition. Without that, I'm just guessing, which isn't implementation—it's making things up.

Same problem with `max_size` and `position`. I have no idea what they represent or what constraints apply.

### What questions you would ask the Logic Designer

- What's the exact formula for optimal_kelly_fraction? Give me the math.
- What inputs does it need? (win probability, payout odds, bankroll, something else?)
- What are `max_size` and `position` exactly? What units are they in?
- Can positions be fractional or do they need to be whole numbers? What's the range?

---

## Spec 2: PortfolioBuilder

### What is missing or ambiguous

The spec says to use "best judgment" for allocation. That's not an algorithm—that's completely subjective. There's no objective function, no optimization goal, no constraints. No data sources, no risk limits, nothing concrete.

### Why it cannot be deterministically implemented

I need deterministic rules that always produce the same output for the same input. "Best judgment" is different for every person. It can't be coded because there's no actual logic to implement.

### What questions you would ask the Logic Designer

- What's the goal? (Maximize Sharpe ratio? Minimize variance? Target a specific return or volatility?)
- What are the constraints? (Risk budget, sector caps, position limits, liquidity requirements?)
- What instruments can we allocate to?
- What data sources should we use?

---

## Spec 3: ExecutionEngine

### What is missing or ambiguous

"Market is favorable" has no definition. Does it mean a certain price level? A volume spike? A volatility band? It's completely vague.

Also, "minimize slippage as much as possible" doesn't tell me what to actually do. Minimize compared to what baseline? What's the acceptable range? Are there tradeoffs?

### Why it cannot be deterministically implemented

Deterministic execution needs measurable conditions and clear thresholds. I can't code "favorable" because it's not a condition—it's a feeling. "As much as possible" isn't a rule, it's a wish.

### What questions you would ask the Logic Designer

- Define "market is favorable" with actual metrics and thresholds. What indicators should I check? What values trigger execution?
- What's the target for slippage? (In basis points? Percentage? Dollars?)
- If we're minimizing slippage, what can we trade off? (Speed? Price impact?)
- How long do we have to execute? Are there time limits?
