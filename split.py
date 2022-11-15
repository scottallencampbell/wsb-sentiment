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

csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

print(f'Loading posts from flat file')
posts = {}

with open(filename, 'r') as psvfile:
	for row in csv.reader(psvfile, dialect='piper'):
		key, value = row
		posts[key] = value

last = ''
splitname = ''

for key in sorted(posts):
	value = posts[key]

	if last != value[:7]:
		last = value[:7]
		splitname = f'./{last}.py'

		with open(splitname, 'a') as f:
			f.write('from comments import download_comments_by_post\n')

	with open(splitname, 'a') as f:
		f.write(f'download_comments_by_post(\'{key}\', \'{value}\', \'data/comments/{value}.txt\')\n')

