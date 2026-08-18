"""Shared configuration for the GENOME analysis package.

The API key is read from the GENOME_API_KEY environment variable so that no
secret is ever committed to the repository. See the README for how to set it.
"""

import os

BASE_URL = "https://genome.app.hcss.nl/api"

# Read the key from the environment. Never hardcode it here.
API_KEY = os.environ.get("GENOME_API_KEY", "")

# Signed intensity weights for each PLOVER event type, on a cooperation(+) /
# conflict(-) scale. This is a Goldstein-style ordering; the exact values are a
# modelling choice and are documented (and stress-tested) in the analysis.
EVENT_WEIGHTS = {
    "AID": 10,
    "COOPERATE": 8,
    "RETREAT": 5,
    "AGREE": 4,
    "SUPPORT": 3,
    "CONCEDE": 2,
    "CONSULT": 1,
    "REQUEST": -1,
    "REJECT": -3,
    "ACCUSE": -4,
    "THREATEN": -5,
    "PROTEST": -6,
    "MOBILIZE": -7,
    "SANCTION": -8,
    "COERCE": -9,
    "ASSAULT": -10,
}
