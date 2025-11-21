# Binomial Option Pricing Model

This repository implements a simple binomial option pricing model (Cox–Ross–Rubinstein) in Python. The `binomial_option.py` module exposes a `price_option` function and an `OptionSpec` dataclass for pricing European call and put options.

## Usage

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
