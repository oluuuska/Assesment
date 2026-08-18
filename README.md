GENOME — Relationship Trajectory Angle

An analysis layer on top of the GENOME geopolitical event dataset that reads a country's stream of events as a single cooperation–conflict tone signal over time, and detects when two countries' tone signals move together over the long run.

Domain angle and why it's interesting

GENOME can already be navigated by country, organisation, and leader. Those lenses answer "what is happening around actor X?" This project adds a trajectory / co-movement lens: instead of treating events as isolated records, it collapses each actor's daily events into a signed intensity score (cooperation positive, conflict negative — a Goldstein-style scale) and tracks how that score evolves.

That reframing lets an analyst ask questions the existing angles don't surface:

- Is the overall tone toward or from a country trending warmer or colder?
- Do two countries' relationships track each other — e.g. do tensions with one reliably accompany tensions with another — suggesting a shared driver or bloc dynamic?

The co-movement question is tested formally with a cointegration test, which looks for a shared long-term trend rather than mere day-to-day correlation.

Key design choices, assumptions, and trade-offs
Event weighting. Each of the 16 PLOVER event types is mapped to a signed weight in genome/config.py. The ordering is Goldstein-style; the exact numbers are a modelling choice, kept in one place so they are easy to inspect and adjust. Trade-off: this collapses GENOME's verbal/material axis into a single scale, trading nuance for a legible one-line signal.
One signal per actor per day. Daily mean weight is the unit of analysis. Low-volume days therefore carry as much visual weight as busy ones; event counts should be read alongside the trend.
Cointegration assumptions are enforced, not assumed. Each series is ADF-tested for a unit root first, pairs are required to share a minimum number of overlapping days, and p-values are FDR-corrected across all tested pairs to avoid manufacturing false positives when many pairs are compared.
Missing days are not zero-filled. Only days where both actors actually have events are used, so the trend is not distorted by invented observations.

How to run
1. Install dependencies
bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Provide your API key

The key is read from an environment variable and is never committed.

bash
cp .env.example .env             # then edit .env and paste your key
export GENOME_API_KEY="your_key" # or set it in your shell / notebook

In a notebook (Colab included) you can instead do:

python
import os
os.environ["GENOME_API_KEY"] = "your_key"
3. Launch the interface

The UI is built with ipywidgets, so it runs in Jupyter or Colab:

python
from app import main
main()

Enter one or more actor countries (comma-separated), an optional recipient and date range, and press GO. Results render in a styled panel with a moving-average plot below.


Repository layout
genome-project/
├── genome/                 # the analysis package
│   ├── __init__.py
│   ├── config.py           # base URL, API-key loading, event weights
│   ├── api.py              # retrieval from the GENOME API
│   ├── processing.py       # cleaning + weight feature engineering
│   ├── analysis.py         # stats, moving averages, cointegration
│   └── viz.py              # HTML summary panel + plotting
├── app.py                  # ipywidgets UI wiring the pipeline together
├── requirements.txt
├── .env.example            # template for the API key (.env is git-ignored)
├── .gitignore
└── README.md
