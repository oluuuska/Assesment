GENOME — Relationship Trajectory Angle

An analysis layer on top of the GENOME geopolitical event dataset. It reads a country's stream of events as a single cooperation–conflict tone signal over time, and tests whether two countries' tone signals move together over the long run.

Domain angle and why it's interesting

GENOME can already be navigated by country, organisation, and leader. Those lenses answer "what is happening around actor X?" This project adds a trajectory / co-movement lens: instead of treating events as isolated records, it collapses each actor's daily events into a signed intensity score (cooperation positive, conflict negative — a Goldstein-style scale) and tracks how that score evolves.

That reframing lets an analyst ask questions the existing angles don't surface:

Is the tone an actor directs toward a country trending warmer or colder?
Do two countries' relationships track each other over the long run — e.g. does a shared negative stance toward a third state also mean a shared trajectory?

The co-movement question is tested with a cointegration test, which looks for a shared long-term stochastic trend rather than mere day-to-day correlation.

Key design choices, assumptions, and trade-offs
Event weighting. Each of the 16 PLOVER event types is mapped to a signed weight in genome/config.py, on a Goldstein-style cooperation(+)/conflict(−) scale. The exact numbers are a modelling choice, kept in one place so they are easy to inspect and adjust. Trade-off: this collapses GENOME's verbal/material axis into a single scalar, trading nuance for a legible one-line signal.
One signal per actor per day. The unit of analysis is the daily mean weight. A day with one event and a day with fifty count equally, so event volume should be read alongside the trend.
Actor role only. The tool measures the tone an actor initiates; it does not yet use GENOME's Recipient or Third-Party roles.
Cointegration assumptions are enforced, not assumed. Each series is ADF-tested for a unit root first, pairs must share a minimum number of overlapping days, and p-values are FDR-corrected (Benjamini–Hochberg) across all tested pairs to avoid false positives when many pairs are compared. Pairs where a series is stationary are reported and skipped, since the cointegration assumption does not hold.
Missing days are not zero-filled. Only calendar days where both actors actually have events enter a pairwise test, so the result is not distorted by invented observations. (This is also why overlapping-day coverage is often thin.)
Requirements

Python 3.9+ and the packages in requirements.txt (requests, pandas, numpy, matplotlib, statsmodels, ipywidgets).

How to run
Install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
Provide your API key

The key is read from the GENOME_API_KEY environment variable and is never committed to the repo.

export GENOME_API_KEY="your_key"    # Windows (PowerShell): $env:GENOME_API_KEY="your_key"

In a notebook (Colab included) you can instead set it inline before importing:

import os
os.environ["GENOME_API_KEY"] = "your_key"
Launch the interface

The UI is built with ipywidgets, so it runs inside Jupyter or Colab. In a notebook cell:

from app import main
main()

Enter one or more actor countries (comma-separated), an optional recipient and date range, and press GO. The results panel prints summary statistics and the cointegration results, with a 7-day moving-average plot below.

Running python app.py from a terminal only prints a reminder that the UI is notebook-based; it does not open an interface on its own.

Repository layout
genome/ — analysis package
init.py
config.py — base URL, API-key loading, event weights
api.py — retrieval from the GENOME API
processing.py — cleaning + weight feature engineering
analysis.py — summary stats, 7-day moving average, cointegration
viz.py — HTML summary panel + moving-average plot
app.py — ipywidgets UI wiring the pipeline together
requirements.txt
README.md
