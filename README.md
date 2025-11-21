# Option Pricing Utilities

This repository contains pricing utilities for plain-vanilla and custom options:

- **Binomial CRR tree** for European calls/puts (`binomial_option.py`).
- **Monte Carlo simulation with user-defined payoffs** (`monte_carlo_option.py`).
- **Web UI for Monte Carlo pricing** (`web_option_server.py`).

## Binomial model usage

Run the module directly to see an example price for a 1-year at-the-money call:

```bash
python binomial_option.py
```

You can also import the function in your own scripts:

```python
from binomial_option import OptionSpec, price_option

spec = OptionSpec(kind="call", strike=100, maturity=1)
price = price_option(
    spot=100,
    option=spec,
    rate=0.05,
    volatility=0.2,
    steps=200,
)
print(price)
```

### Parameters
- `spot`: Current underlying price (positive float)
- `option`: `OptionSpec` describing option type, strike, and maturity
- `rate`: Continuously-compounded risk-free rate (e.g., `0.05` for 5%)
- `volatility`: Annualized volatility of the underlying (positive float)
- `steps`: Number of time steps for the binomial tree (positive integer)

### Notes
- The implementation validates inputs and raises `ValueError` for invalid configurations.
- Risk-neutral probability is derived as `(exp(rate * dt) - d) / (u - d)` with up/down factors `u = exp(volatility * sqrt(dt))` and `d = 1/u`.

## Monte Carlo with custom payoffs

`monte_carlo_option.py` prices options under geometric Brownian motion using Monte Carlo simulation. The payoff is supplied by you, so you can model exotic or path-dependent contracts.

### Example: run from the command line

Provide core parameters followed by a Python expression for the payoff. Use `S` for the terminal price or `path` for the full simulated path (including the starting spot).

```bash
python monte_carlo_option.py 100 0.05 0.2 1 252 20000 "max(S - 100, 0)" --seed 42
```

Explanation of the positional arguments:

1. `spot` – Current underlying price.
2. `rate` – Annualized continuously-compounded risk-free rate.
3. `volatility` – Annualized volatility of the underlying.
4. `maturity` – Time to maturity in years.
5. `steps` – Number of time steps per simulated path (e.g., 252 for daily steps in a year).
6. `paths` – Number of Monte Carlo simulation paths.
7. `payoff` – Python expression for the payoff using `S` or `path`.

### Example: programmatic usage

You can also pass a callable directly for full flexibility:

```python
from monte_carlo_option import monte_carlo_price

def asian_call_payoff(path):
    average_price = sum(path) / len(path)
    return max(average_price - 100, 0)

price = monte_carlo_price(
    spot=100,
    rate=0.05,
    volatility=0.2,
    maturity=1,
    steps=252,
    paths=50_000,
    payoff=asian_call_payoff,
    seed=123,
)
print(price)
```

## Web-based Monte Carlo calculator

Launch a lightweight Flask server that exposes a browser form for pricing with custom payoff expressions:

```bash
pip install flask
python web_option_server.py
```

By default the server listens on `http://localhost:8000/price`. Fill in the inputs:

- Spot, rate, volatility, maturity, steps, and number of simulation paths
- Payoff expression using `S` (terminal price) or `path` (entire simulated path)
- Optional RNG seed for reproducibility

The page returns the estimated discounted price or a validation error. You can set alternative host/port values by modifying the `app.run` call in `web_option_server.py`.
