# URL strings
FACEBOOK_PAGE_MAIN = "https://www.facebook.com/%s"
FACEBOOK_PAGE_POSTS = "https://m.facebook.com/%s/posts"
POST_PAGE = "https://m.facebook.com/%d"
POST_REACTIONS = "https://m.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier=%d"

# expected conditions timout messages
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