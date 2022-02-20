from datetime import datetime

import pytest


@pytest.fixture
def timetracker():
    tick = datetime.now()
    yield
    tock = datetime.now()
    diff = tock - tick
    print(f"\n runtime: {diff.total_seconds()}")

