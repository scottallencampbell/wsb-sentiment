from posts import download_posts
from comments import download_comments
from comments import download_comments_by_post
from sentiment import update_sentiments

#posts = download_posts()
#comments = download_comments()

update_sentiments()

# download_comments_by_post('yi6wh1', '2022-10-31', 'data/comments/2022-10-31.txt')