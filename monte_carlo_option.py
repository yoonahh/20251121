"""Monte Carlo option pricing with user-defined payoffs.

This module prices options under geometric Brownian motion by Monte Carlo
simulation. Users supply an arbitrary payoff callable to evaluate each
simulated path, making it easy to support non-standard or path-dependent
contracts.
"""
from __future__ import annotations

import math
import random
from typing import Callable, Sequence


def parse_payoff_expression(expression: str) -> Callable[[Sequence[float]], float]:
    """Create a payoff function from a Python expression string.

    The expression can reference:

    - ``path``: the full simulated price path (list of floats, including spot).
    - ``S``: the terminal price, a shorthand for ``path[-1]``.
    - ``math``: the standard :mod:`math` module for helpers like ``exp`` or
      ``sqrt``.
    - Common Python built-ins ``max``, ``min``, and ``abs``.

    Args:
        expression: A Python expression returning the payoff for a given path.

    Returns:
        A callable that maps a price path to a payoff value.

    Example:
        ``parse_payoff_expression("max(S - 100, 0)")``
    """

    code = compile(expression, "<payoff>", "eval")

    def payoff(path: Sequence[float]) -> float:
        return float(
            eval(
                code,
                {"__builtins__": {}},
                {
                    "path": path,
                    "S": path[-1],
                    "math": math,
                    "max": max,
                    "min": min,
                    "abs": abs,
                },
            )
        )

    return payoff


def monte_carlo_price(
    spot: float,
    rate: float,
    volatility: float,
    maturity: float,
    steps: int,
    paths: int,
    payoff: Callable[[Sequence[float]], float],
    seed: int | None = None,
) -> float:
    """Estimate an option price via Monte Carlo simulation.

    Underlying prices follow a geometric Brownian motion discretized with a
    fixed number of steps. The payoff callable receives the entire simulated
    path, enabling path-dependent options.

    Args:
        spot: Current underlying price (must be positive).
        rate: Annualized continuously-compounded risk-free rate.
        volatility: Annualized volatility of the underlying (must be positive).
        maturity: Time to maturity in years (must be positive).
        steps: Number of time steps in each path (must be positive).
        paths: Number of Monte Carlo simulation paths (must be positive).
        payoff: Callable that returns the payoff for a given price path.
        seed: Optional random seed for reproducibility.

    Returns:
        The discounted Monte Carlo estimate of the option price.
    """

    if spot <= 0:
        raise ValueError("spot must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if maturity <= 0:
        raise ValueError("maturity must be positive")
    if steps <= 0:
        raise ValueError("steps must be a positive integer")
    if paths <= 0:
        raise ValueError("paths must be a positive integer")

    if seed is not None:
        random.seed(seed)

    dt = maturity / steps
    drift = (rate - 0.5 * volatility**2) * dt
    diffusion = volatility * math.sqrt(dt)
    discount = math.exp(-rate * maturity)

    payoff_sum = 0.0
    for _ in range(paths):
        price = spot
        path = [price]
        for _ in range(steps):
            z = random.gauss(0, 1)
            price *= math.exp(drift + diffusion * z)
            path.append(price)
        payoff_sum += payoff(path)

    return discount * (payoff_sum / paths)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Monte Carlo pricing with a user-defined payoff expression",
    )
    parser.add_argument("spot", type=float, help="current underlying price")
    parser.add_argument("rate", type=float, help="risk-free rate (annualized)")
    parser.add_argument("volatility", type=float, help="volatility (annualized)")
    parser.add_argument("maturity", type=float, help="time to maturity in years")
    parser.add_argument("steps", type=int, help="number of time steps per path")
    parser.add_argument("paths", type=int, help="number of Monte Carlo paths")
    parser.add_argument(
        "payoff",
        type=str,
        help=(
            "Python expression for payoff; use 'path' for the price path or 'S' for"
            " the terminal price"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="optional RNG seed for reproducible results",
    )

    args = parser.parse_args()

    payoff_fn = parse_payoff_expression(args.payoff)
    price = monte_carlo_price(
        spot=args.spot,
        rate=args.rate,
        volatility=args.volatility,
        maturity=args.maturity,
        steps=args.steps,
        paths=args.paths,
        payoff=payoff_fn,
        seed=args.seed,
    )
    print(f"Estimated option price: {price:.6f}")
