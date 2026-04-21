import random
import time
from src.config.settings import settings


def human_delay(min_s: float = None, max_s: float = None) -> None:
    lo = min_s if min_s is not None else settings.delay_min
    hi = max_s if max_s is not None else settings.delay_max
    time.sleep(random.uniform(lo, hi))


def long_pause(min_s: float = 30, max_s: float = 90) -> None:
    time.sleep(random.uniform(min_s, max_s))
