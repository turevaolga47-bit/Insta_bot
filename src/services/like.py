from src.api.client import InstagramClient
from src.utils.delays import human_delay
from src.utils.logger import log


class LikeService:
    def __init__(self, client: InstagramClient):
        self._cl = client.cl

    def like_post(self, media_pk: str) -> bool:
        try:
            result = self._cl.media_like(media_pk)
            if result:
                log.info(f"Liked post {media_pk}")
            human_delay()
            return result
        except Exception as e:
            log.error(f"Like failed for {media_pk}: {e}")
            return False

    def like_user_posts(self, user_pk: str, amount: int = 3) -> int:
        try:
            medias = self._cl.user_medias(user_pk, amount=amount)
            count = sum(1 for m in medias if self.like_post(str(m.pk)))
            log.info(f"Liked {count}/{amount} posts of user {user_pk}")
            return count
        except Exception as e:
            log.error(f"like_user_posts error: {e}")
            return 0

    def like_hashtag_posts(self, hashtag: str, amount: int = 10) -> int:
        try:
            medias = self._cl.hashtag_medias_recent(hashtag, amount=amount)
            count = sum(1 for m in medias if self.like_post(str(m.pk)))
            log.info(f"Liked {count} posts with #{hashtag}")
            return count
        except Exception as e:
            log.error(f"like_hashtag_posts error: {e}")
            return 0
