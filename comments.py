import json
import os
import pandas as pd
import time
import datetime
from posts import get_existing_posts
from api import redditApi

path = './data/comments/'

def download_comments():
    print(f'Downloading comments')
    posts = get_existing_posts()

    for key in posts:
        filename = f'{path}{posts[key]}.txt'
        download_comments_by_post(key, posts[key], filename)
        
def download_comments_by_post(post_id, date, filename):
    start = datetime.datetime.now().date()
    
    if start >= datetime.datetime.strptime(date, '%Y-%m-%d').date():
        return
    
    print(f'Downloading comments for {date}')
    
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
            f.write('|'.join(comment) + '\n')

    end = time.time()
    print(f'Downloaded {len(submission.comments)} comments for {date} in {int(end - start)} seconds')


