"""Binomial option pricing using the Cox-Ross-Rubinstein model.

The module exposes :func:`price_option` which computes the price of a
European call or put option using a recombining binomial tree.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

OptionKind = Literal["call", "put"]


@dataclass(frozen=True)
class OptionSpec:
    """Specification for the option contract.

    Attributes:
        kind: "call" for a call option or "put" for a put option.
        strike: Strike price of the option.
        maturity: Time to maturity (in years).
    """

    kind: OptionKind
    strike: float
    maturity: float

    def __post_init__(self) -> None:
        if self.kind not in ("call", "put"):
            raise ValueError("kind must be either 'call' or 'put'")
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")


def price_option(
    spot: float,
    option: OptionSpec,
    rate: float,
    volatility: float,
    steps: int,
) -> float:
    """Price a European option using the binomial tree model.

    Args:
        spot: Current underlying price.
        option: Option contract specification.
        rate: Annualized continuously-compounded risk-free rate (e.g. 0.05 for 5%).
        volatility: Annualized volatility of the underlying.
        steps: Number of time steps in the tree (must be > 0).

    Returns:
        The fair price of the option.

    Raises:
        ValueError: If any of the inputs are invalid.
    """

    if spot <= 0:
        raise ValueError("spot must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if steps <= 0:
        raise ValueError("steps must be a positive integer")

    dt = option.maturity / steps
    u = math.exp(volatility * math.sqrt(dt))
    d = 1 / u
    disc = math.exp(-rate * dt)
    p = (math.exp(rate * dt) - d) / (u - d)

    if not (0 <= p <= 1):
        raise ValueError("Computed risk-neutral probability is invalid; check parameters")

    # Terminal payoffs
    prices = [spot * (u ** j) * (d ** (steps - j)) for j in range(steps + 1)]
    if option.kind == "call":
        payoffs = [max(price - option.strike, 0) for price in prices]
    else:
        payoffs = [max(option.strike - price, 0) for price in prices]

    # Backward induction through the tree
    for step in range(steps - 1, -1, -1):
        payoffs = [
            disc * (p * payoffs[j + 1] + (1 - p) * payoffs[j]) for j in range(step + 1)
        ]

    return payoffs[0]


if __name__ == "__main__":
    # Demonstration values for a 1-year at-the-money call.
    spec = OptionSpec(kind="call", strike=100, maturity=1)
    price = price_option(
        spot=100,
        option=spec,
        rate=0.05,
        volatility=0.2,
        steps=100,
    )
    print(f"Estimated option price: {price:.4f}")
