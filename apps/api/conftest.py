"""Point tests at an in-memory database before the app engine is created.

The running API always uses Postgres from Docker. Tests stay on SQLite so they do not need that container.
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
