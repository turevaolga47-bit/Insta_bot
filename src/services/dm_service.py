import os
import random
import requests
from pathlib import Path
from src.utils.logger import log

_DM_FILE = Path(__file__).parents[2] / "data" / "texts" / "dm_templates.txt"

def _load_dm_templates() -> list[str]:
    if _DM_FILE.exists():
        raw = _DM_FILE.read_text(encoding="utf-8")
        templates = [t.strip() for t in raw.split("---") if t.strip()]
        if templates:
            return templates
    return ["Привет! Держи ссылку: {link}"]

DM_TEMPLATES = _load_dm_templates()

RETREAT_LINK = os.environ.get("RETREAT_LINK", "https://t.me/ваш_канал")


class MetaDMService:
    """Отправка DM через официальный Instagram Messaging API (Meta Graph API)."""

    def __init__(self):
        self._access_token = os.environ.get("META_ACCESS_TOKEN", "")
        self._ig_user_id   = os.environ.get("IG_USER_ID", "")
        self._api_version  = "v25.0"
        self._base_url     = f"https://graph.instagram.com/{self._api_version}"

    def send_dm(self, igsid: str, username: str = "") -> bool:
        """Отправить DM пользователю по его IGSID."""
        if not self._access_token or not self._ig_user_id:
            log.error("META_ACCESS_TOKEN or IG_USER_ID not set")
            return False

        text = random.choice(DM_TEMPLATES).format(link=RETREAT_LINK)
        url  = f"{self._base_url}/{self._ig_user_id}/messages"

        payload = {
            "recipient": {"id": igsid},
            "message":   {"text": text},
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type":  "application/json",
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            if r.status_code == 200:
                log.info(f"DM sent to @{username} (igsid={igsid})")
                return True
            log.error(f"DM failed [{r.status_code}]: {r.text}")
            return False
        except Exception as e:
            log.error(f"DM exception: {e}")
            return False

    def refresh_token(self) -> str | None:
        """Обновить долгосрочный токен (вызывать раз в ~55 дней)."""
        url = f"{self._base_url}/refresh_access_token"
        params = {
            "grant_type":   "ig_refresh_token",
            "access_token": self._access_token,
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if "access_token" in data:
                log.info(f"Token refreshed, expires in {data.get('expires_in')} sec")
                return data["access_token"]
            log.error(f"Token refresh failed: {data}")
            return None
        except Exception as e:
            log.error(f"Token refresh exception: {e}")
            return None
