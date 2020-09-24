class Page:
    """Holds data of scraped Facebook page.
    """
    def __init__(self, fullname: str, username: str):
        self.fullname = fullname
        self.username = username
        self.likes = 0
        self.followers = 0

    def __str__(self):
        return 'Page: {}, {} likes and {} followers, username: {}'.format(self.fullname, self.likes, self.followers, self.username)
