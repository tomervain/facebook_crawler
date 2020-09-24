from dataclasses import dataclass


@dataclass
class Page:
    """Holds data of scraped Facebook page."""
    fullname: str
    username: str
    likes: int = 0
    followers: int = 0

    def set_likes_followers(self, data_tuple: tuple):
        """Sets page's likes and followers count

        Args:
            data_tuple (tuple): Tuple storing likes and followers
        """
        self.likes, self.followers = data_tuple
        