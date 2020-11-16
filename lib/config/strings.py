# URL strings
FACEBOOK_PAGE_MAIN = "https://www.facebook.com/%s"
FACEBOOK_PAGE_POSTS = "https://m.facebook.com/%s/posts"
POST_PAGE = "https://m.facebook.com/%d"
POST_REACTIONS = "https://m.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier=%d"
POST_REGULAR = 'https://www.facebook.com/%s/posts/%d'

# expected conditions for timeout messages
WTO_POSTS_VISIBLE = "Not all Post elements were visible"

# js scripts
CLEAR_ITEMS = """
items = document.querySelectorAll("%s")
for(item of items) {
    item.parentNode.removeChild(item)
    item = null
}
items = null
"""

LEAVE_MAIN_POST = """
others = document.querySelector("div[class = 'd2edcug0 oh7imozk abvwweq7 ejjq64ki']")
others.parentNode.removeChild(others)
others = null
"""

# logging messages
log_messages = {
    "PAGE_LOAD_JSON": "successfully loaded %d pages from json file",
    "PAGE_START": "scraping page data for %s...",
    "PAGE_END": "done scraping page data for %s, time elapsed: %s",
    "POST_START": "scraping posts for %s...",
    "POST_END": "done scraping total of %d posts for %s, time elapsed: %s",
    "TOTAL_POSTS": "scraping %d posts for %s...",
    "COMM_START": "scraping %s id %d...",
    "COMM_END": "done scraping %d comments from post, time elapsed: %s",
    "TOTAL_COMMS": "total comments scraped for %s: %d, time elapsed: %s",
    "CRAWLER_DONE": "Crawler done! total crawling time: %s"
}
