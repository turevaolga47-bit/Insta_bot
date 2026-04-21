from src.api.client import InstagramClient
from src.services.follow import FollowService
from src.services.like import LikeService
from src.services.comment import CommentService
from src.utils.logger import log


class InstaBot:
    def __init__(self):
        self._client = InstagramClient()
        self.follow_svc: FollowService = None
        self.like_svc: LikeService = None
        self.comment_svc: CommentService = None

    def start(self) -> bool:
        if not self._client.login():
            return False
        self.follow_svc = FollowService(self._client)
        self.like_svc = LikeService(self._client)
        self.comment_svc = CommentService(self._client)
        log.info("InstaBot started")
        return True

    def run_follow_campaign(self, target: str, limit: int = 20) -> None:
        log.info(f"Follow campaign → @{target}, limit={limit}")
        self.follow_svc.follow_user_followers(target, limit)

    def run_hashtag_like(self, hashtag: str, amount: int = 10) -> None:
        log.info(f"Hashtag like campaign → #{hashtag}, amount={amount}")
        self.like_svc.like_hashtag_posts(hashtag, amount)
