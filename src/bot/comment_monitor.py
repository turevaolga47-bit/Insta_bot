"""
Polling-монитор комментариев через instagrapi.
Используй для быстрого теста на личном аккаунте.
НЕ рекомендуется для production — нарушает ToS Instagram.
"""
import time
import random
import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from src.utils.logger import log
from src.utils.delays import human_delay

KEYWORDS = [kw.upper() for kw in os.environ.get("TRIGGER_KEYWORDS", "РЕТРИТ,ХОЧУ,INFO").split(",")]
RETREAT_LINK = os.environ.get("RETREAT_LINK", "https://t.me/ваш_канал")

DM_TEMPLATES = [
    (
        "Привет! Увидела твой комментарий 🌿\n\n"
        f"Вот ссылка на программу Чёрного Ретрита → {RETREAT_LINK}\n\n"
        "Если есть вопросы — просто напиши сюда, отвечу лично 💛"
    ),
    (
        "Привет! 👋 Держи подробности о ретрите:\n"
        f"{RETREAT_LINK}\n\n"
        "Если хочешь — могу рассказать больше о формате. Просто ответь сюда 🤍"
    ),
]


class CommentMonitor:
    def __init__(self, client: Client):
        self._cl = client
        self._seen: set[str] = set()

    def monitor_post(self, media_url: str, interval: int = 120) -> None:
        """Мониторить комментарии к посту/Reels и слать DM при ключевом слове."""
        try:
            pk       = self._cl.media_pk_from_url(media_url)
            media_id = self._cl.media_id(pk)
        except Exception as e:
            log.error(f"Cannot resolve media URL: {e}")
            return

        log.info(f"Monitoring comments on media {media_id} (interval={interval}s)")

        while True:
            try:
                self._check_comments(media_id)
            except LoginRequired:
                log.error("Session expired — re-login required")
                break
            except Exception as e:
                log.error(f"Monitor error: {e}")

            time.sleep(interval + random.randint(-20, 20))

    def monitor_recent_posts(self, amount: int = 3, interval: int = 180) -> None:
        """Мониторить комментарии к последним N постам аккаунта."""
        try:
            user_id = self._cl.user_id_from_username(self._cl.username)
            medias  = self._cl.user_medias(user_id, amount=amount)
        except Exception as e:
            log.error(f"Cannot fetch recent posts: {e}")
            return

        media_ids = [str(m.id) for m in medias]
        log.info(f"Monitoring {len(media_ids)} recent posts")

        while True:
            for media_id in media_ids:
                try:
                    self._check_comments(media_id)
                except Exception as e:
                    log.error(f"Error checking media {media_id}: {e}")
                time.sleep(3)

            time.sleep(interval + random.randint(-30, 30))

    def _check_comments(self, media_id: str) -> None:
        comments = self._cl.media_comments(media_id, amount=50)
        new_comments = [c for c in comments if str(c.pk) not in self._seen]

        for comment in new_comments:
            self._seen.add(str(comment.pk))
            text = comment.text.upper()

            if any(kw in text for kw in KEYWORDS):
                username = comment.user.username
                user_pk  = comment.user.pk
                log.info(f"Keyword triggered by @{username}: '{comment.text}'")

                # Публичный ответ на комментарий
                self._reply_comment(media_id, str(comment.pk), username)
                human_delay(2, 5)

                # Отправить DM
                self._send_dm(user_pk, username)
                human_delay(5, 10)

    def _reply_comment(self, media_id: str, comment_id: str, username: str) -> None:
        try:
            self._cl.media_comment(
                media_id,
                f"@{username} написала тебе в директ! Проверяй 🤍",
                replied_to_comment_id=int(comment_id),
            )
            log.info(f"Replied to comment by @{username}")
        except Exception as e:
            log.error(f"Reply failed: {e}")

    def _send_dm(self, user_pk: int, username: str) -> None:
        text = random.choice(DM_TEMPLATES)
        try:
            self._cl.direct_send(text, user_ids=[user_pk])
            log.info(f"DM sent to @{username}")
        except Exception as e:
            log.error(f"DM failed for @{username}: {e}")
