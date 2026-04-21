from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    pk: str
    username: str
    full_name: str = ""
    is_private: bool = False
    follower_count: int = 0
    following_count: int = 0
    media_count: int = 0
    is_followed: bool = False
    is_follower: bool = False
    biography: str = ""
    profile_pic_url: str = ""
