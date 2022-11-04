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

start_time = datetime.utcnow()

def getExistingPosts():    
	print(f'Loading posts from flat file')
	existing_posts = {}
	csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

	with open(filename, 'r') as psvfile:
		for row in csv.reader(psvfile, dialect='piper'):
			key, value = row
			existing_posts[key] = value
	
	print(f'Loaded {len(existing_posts)} posts from flat file')
	return existing_posts

def downloadPosts():
	print(f'Saving posts to {filename}')
	existing_posts = {}
	
	if os.path.exists(filename):
		existing_posts = getExistingPosts()

	count = 0
	previous_epoch = int(start_time.timestamp())
	
	while True:
		new_url = url + str(previous_epoch)
		print(new_url)
		
		json_text = requests.get(new_url, headers={'User-Agent': 'wsb-sentiment'})
		time.sleep(1)  

		try:
			print('--> got data')
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
				print(f'-->  writing! {id} not in existing posts list')
				savePost(object)	
			else:
				print(f'-->  skipping :) {id} already in existing posts list')

		print('Downloaded {} posts through {}'.format(count, datetime.fromtimestamp(previous_epoch).strftime('%Y-%m-%d')))
		
	print(f'Saved {count} posts')
	
def savePost(object):
	try:
		title = str(object['title'])
		
		if object['is_self'] and 'selftext' in object and title.startswith('Daily Discussion'):	
			date = getDateFromTitle(title)

			if (date is not None):
				vals = '|'.join([
						str(object['id']), 
						date.strftime('%Y-%m-%d')
					]) + '\r'

				with open(filename, 'a') as f:
					f.write(vals)

	except Exception as err:
		print(f'Couldn''t interpret post: {object["url"]}')
		print(traceback.format_exc())

def getDateFromTitle(title):
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
