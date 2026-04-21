import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # Account
    username: str = os.getenv("IG_USERNAME", "")
    password: str = os.getenv("IG_PASSWORD", "")

    # Delays (seconds) — anti-ban
    delay_min: float = float(os.getenv("DELAY_MIN", "2.0"))
    delay_max: float = float(os.getenv("DELAY_MAX", "6.0"))

    # Daily limits
    max_follows_per_day: int = int(os.getenv("MAX_FOLLOWS", "50"))
    max_likes_per_day: int = int(os.getenv("MAX_LIKES", "100"))
    max_comments_per_day: int = int(os.getenv("MAX_COMMENTS", "20"))

    # Storage paths
    data_dir: str = "data"
    logs_dir: str = "logs"

    # Proxy (optional)
    proxy: str = os.getenv("PROXY", "")


settings = Settings()
