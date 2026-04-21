from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from src.config.settings import settings
from src.utils.logger import log
import json
from pathlib import Path


SESSION_FILE = Path("data/accounts/session.json")


class InstagramClient:
    def __init__(self):
        self._cl = Client()
        if settings.proxy:
            self._cl.set_proxy(settings.proxy)

    def login(self) -> bool:
        if SESSION_FILE.exists():
            try:
                self._cl.load_settings(SESSION_FILE)
                self._cl.login(settings.username, settings.password)
                log.info("Logged in via saved session")
                return True
            except Exception as e:
                log.warning(f"Session load failed: {e}, re-logging")

        try:
            self._cl.login(settings.username, settings.password)
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._cl.dump_settings(SESSION_FILE)
            log.info("Logged in successfully")
            return True
        except ChallengeRequired:
            log.error("Challenge required — solve manually in browser first")
            return False
        except Exception as e:
            log.error(f"Login failed: {e}")
            return False

    @property
    def cl(self) -> Client:
        return self._cl
