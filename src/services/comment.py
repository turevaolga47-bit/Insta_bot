import random
from pathlib import Path
from src.api.client import InstagramClient
from src.utils.delays import human_delay
from src.utils.logger import log

_COMMENTS_FILE = Path(__file__).parents[2] / "data" / "texts" / "comments.txt"

def _load_comments() -> list[str]:
    if _COMMENTS_FILE.exists():
        lines = [l.strip() for l in _COMMENTS_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            return lines
    return ["Great post! 🔥", "Love this! ❤️", "Amazing content!"]

DEFAULT_COMMENTS = _load_comments()


class CommentService:
    def __init__(self, client: InstagramClient, comments: list[str] = None):
        self._cl = client.cl
        self._comments = comments or DEFAULT_COMMENTS

    def comment_post(self, media_pk: str, text: str = None) -> bool:
        text = text or random.choice(self._comments)
        try:
            self._cl.media_comment(media_pk, text)
            log.info(f"Commented on {media_pk}: {text!r}")
            human_delay(4, 10)
            return True
        except Exception as e:
            log.error(f"Comment failed for {media_pk}: {e}")
            return False
