from src.api.client import InstagramClient
from src.utils.delays import human_delay
from src.utils.logger import log


class FollowService:
    def __init__(self, client: InstagramClient):
        self._cl = client.cl

    def follow(self, user_pk: str) -> bool:
        try:
            result = self._cl.user_follow(user_pk)
            if result:
                log.info(f"Followed user {user_pk}")
            human_delay()
            return result
        except Exception as e:
            log.error(f"Follow failed for {user_pk}: {e}")
            return False

    def unfollow(self, user_pk: str) -> bool:
        try:
            result = self._cl.user_unfollow(user_pk)
            if result:
                log.info(f"Unfollowed user {user_pk}")
            human_delay()
            return result
        except Exception as e:
            log.error(f"Unfollow failed for {user_pk}: {e}")
            return False

    def follow_user_followers(self, target_username: str, limit: int = 20) -> int:
        try:
            target = self._cl.user_info_by_username(target_username)
            followers = self._cl.user_followers(target.pk, amount=limit)
            count = 0
            for pk in followers:
                if self.follow(str(pk)):
                    count += 1
            log.info(f"Followed {count} followers of @{target_username}")
            return count
        except Exception as e:
            log.error(f"follow_user_followers error: {e}")
            return 0
