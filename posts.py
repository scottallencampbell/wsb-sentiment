import requests
import traceback
import time
import json
import csv
import os
from os.path import exists
import dateparser
from datetime import datetime, timedelta

filename = './data/posts.txt'
subreddit = 'wallstreetbets' 
url = f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&title=Daily&limit=1000&sort=desc&before='

csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

def get_existing_posts():    
	print(f'Loading posts from flat file')
	existing_posts = {}

	with open(filename, 'r') as psvfile:
		for row in csv.reader(psvfile, dialect='piper'):
			key, value = row
			existing_posts[key] = value
	
	print(f'Loaded {len(existing_posts)} posts')
	return existing_posts

def download_posts():
	print(f'Saving posts to {filename}')
	existing_posts = {}
	
	if os.path.exists(filename):
		existing_posts = get_existing_posts()

	count = 0
	previous_epoch = int(datetime.utcnow().timestamp())
	
	while True:
		new_url = url + str(previous_epoch)
		print(new_url)
		
		json_text = requests.get(new_url, headers={'User-Agent': 'wsb-sentiment'})
		time.sleep(1)  

		try:
			json_data = json_text.json()
			print(json_data)
		except json.decoder.JSONDecodeError as ex:
			print(f'Exception: {ex}, {json_text}')
			time.sleep(1)
			continue

		if 'data' not in json_data:
			break

		objects = json_data['data']
		
		if len(objects) == 0:
			break

		for object in objects:
			previous_epoch = object['created_utc'] - 1
			count += 1	
			id = str(object['id'])

			if (id not in existing_posts):
				save_post(object)	
			
		print('Downloaded {} posts through {}'.format(count, datetime.fromtimestamp(previous_epoch).strftime('%Y-%m-%d')))
		
	print(f'Saved {count} posts')
	
def save_post(object):
	try:
		title = str(object['title'])
		
		if object['is_self'] and 'selftext' in object and title.startswith('Daily Discussion'):	
			date = get_date_from_title(title)

			if (date is not None):
				vals = '|'.join([
					str(object['id']), 
					date.strftime('%Y-%m-%d')
				]) + '\n'

				with open(filename, 'a') as f:
					f.write(vals)

	except Exception as err:
		print(f'Couldn''t interpret post: {object["url"]}')
		print(traceback.format_exc())

def get_date_from_title(title):
	title = title.replace('Daily Discussion Thread for ', '')
	title = title.replace('Daily Discussion Thread - ', '')

	print(title)
	try:
		date = dateparser.parse(title)
		return date
	except Exception as err:
		print(f'Couldn''t interpret title: {title}')
		
	if (date is None):
		print(f'Couldn''t interpret title: {title}')
