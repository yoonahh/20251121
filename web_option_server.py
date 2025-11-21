"""Simple web UI for Monte Carlo option pricing with custom payoffs."""
from __future__ import annotations

from flask import Flask, redirect, render_template_string, request, url_for

from monte_carlo_option import monte_carlo_price, parse_payoff_expression


def create_app() -> Flask:
    app = Flask(__name__)

    template = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Monte Carlo Option Pricer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2rem auto; max-width: 800px; line-height: 1.5; }
            form { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem 1.5rem; }
            label { display: flex; flex-direction: column; font-weight: 600; }
            input[type="text"], input[type="number"] { padding: 0.4rem; font-size: 1rem; }
            .full { grid-column: 1 / -1; }
            .actions { grid-column: 1 / -1; }
            .error { color: #b00020; font-weight: 600; margin-top: 1rem; }
            .result { background: #f5f5f5; padding: 1rem; border-radius: 6px; margin-top: 1rem; }
            .hint { font-size: 0.95rem; color: #444; margin-top: -0.4rem; }
        </style>
    </head>
    <body>
        <h1>Monte Carlo Option Pricer</h1>
        <p>Simulate option prices under geometric Brownian motion. Supply a payoff expression using <code>S</code> for the terminal price or <code>path</code> for the full simulated path.</p>
        <form method="post" action="{{ url_for('price') }}">
            <label>Spot
                <input type="number" name="spot" step="any" value="{{ request.form.get('spot', '100') }}" required>
            </label>
            <label>Rate (r)
                <input type="number" name="rate" step="any" value="{{ request.form.get('rate', '0.05') }}" required>
                <span class="hint">Continuously compounded annual rate (e.g., 0.05 for 5%).</span>
            </label>
            <label>Volatility (sigma)
                <input type="number" name="volatility" step="any" value="{{ request.form.get('volatility', '0.2') }}" required>
            </label>
            <label>Maturity (years)
                <input type="number" name="maturity" step="any" value="{{ request.form.get('maturity', '1') }}" required>
            </label>
            <label>Steps per path
                <input type="number" name="steps" step="1" min="1" value="{{ request.form.get('steps', '252') }}" required>
            </label>
            <label>Simulation paths
                <input type="number" name="paths" step="1" min="1" value="{{ request.form.get('paths', '20000') }}" required>
            </label>
            <label class="full">Payoff expression
                <input type="text" name="payoff" value="{{ request.form.get('payoff', 'max(S - 100, 0)') }}" required>
                <span class="hint">Use Python syntax; available names: <code>S</code>, <code>path</code>, <code>math</code>, <code>max</code>, <code>min</code>, <code>abs</code>.</span>
            </label>
            <label>Seed (optional)
                <input type="number" name="seed" step="1" value="{{ request.form.get('seed', '') }}">
            </label>
            <div class="actions">
                <button type="submit">Price Option</button>
            </div>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        {% if result is not none %}
            <div class="result">Estimated price: <strong>{{ "%.6f"|format(result) }}</strong></div>
        {% endif %}
    </body>
    </html>
    """

    def parse_number(value: str, *, allow_int: bool = False) -> float:
        number: float | int
        if allow_int:
            number = int(value)
        else:
            number = float(value)
        return float(number)

    @app.get("/")
    def index():
        return redirect(url_for("price"))

    @app.route("/price", methods=["GET", "POST"])
    def price():
        error: str | None = None
        result: float | None = None

        if request.method == "POST":
            form = request.form
            try:
                spot = parse_number(form["spot"])
                rate = parse_number(form["rate"])
                volatility = parse_number(form["volatility"])
                maturity = parse_number(form["maturity"])
                steps = parse_number(form["steps"], allow_int=True)
                paths = parse_number(form["paths"], allow_int=True)
                payoff_expr = form["payoff"].strip()
                seed_raw = form.get("seed", "").strip()
                seed = int(seed_raw) if seed_raw else None

                payoff = parse_payoff_expression(payoff_expr)
                result = monte_carlo_price(
                    spot=spot,
                    rate=rate,
                    volatility=volatility,
                    maturity=maturity,
                    steps=int(steps),
                    paths=int(paths),
                    payoff=payoff,
                    seed=seed,
                )
            except (ValueError, KeyError) as exc:  # invalid numeric input or missing field
                error = str(exc)
            except Exception as exc:  # catch unexpected payoff errors
                error = f"Failed to price option: {exc}"

        return render_template_string(
            template,
            request=request,
            error=error,
            result=result,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
