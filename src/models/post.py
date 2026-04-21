from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Post:
    pk: str
    user_pk: str
    username: str
    media_type: int  # 1=photo, 2=video, 8=album
    like_count: int = 0
    comment_count: int = 0
    caption: str = ""
    taken_at: Optional[datetime] = None
    is_liked: bool = False
