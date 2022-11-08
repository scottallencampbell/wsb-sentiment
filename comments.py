import json
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from posts import getExistingPosts
from api import redditApi

path = './data/comments/'

def downloadComments():
    print(f'Downloading comments')
    posts = getExistingPosts()

    for key in posts:
        filename = f'{path}{posts[key]}.txt'

        if not os.path.exists(filename):
            downloadCommentsByPost(key, posts[key], filename)
        else:
            print(f'Skipping {posts[key]}, file already exists')

def downloadComment(post_id, date, filename):
    print(f'Downloading comments for {date}')
    start = time.time()
    comments = []
    submission = redditApi.submission(post_id)

    submission.comments.replace_more(limit=None)

    # only gettting top-level comments for now
    for comment in submission.comments:
        comments.append([
            comment.id[-6:], 
            comment.link_id[-6:], 
            comment.parent_id[-6:], 
            str(comment.score), 
            comment.body.replace('|', '').replace('\r', ' ').replace('\n', ' '),
            datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        ])
            
    with open(filename, 'w', encoding='utf-8') as f:
        for comment in comments:
            f.write('|'.join(comment) + '\r')

    end = time.time()
    print(f'Downloaded {len(submission.comments)} comments for {date} in {int(end - start)} seconds')


