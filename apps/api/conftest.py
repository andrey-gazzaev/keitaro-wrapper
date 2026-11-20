"""Point tests at an in-memory database before the app engine is created.

The running API always uses Postgres from Docker. Tests stay on SQLite so they do not need that container.
"""

import os

from dotenv import load_dotenv

load_dotenv(override=False)
os.environ.setdefault("CAMPAIGN_PREFIX", "test_gazzaev_")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
