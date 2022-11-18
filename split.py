import requests
import traceback
import time
import json
import csv
import os
import math
from os.path import exists
import dateparser
from datetime import datetime, timedelta

filename = './data/posts.txt'
comments = './data/comments/'
threads = 10

csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

print(f'Loading posts from flat file')
posts = {}

with open(filename, 'r') as psvfile:
	for row in csv.reader(psvfile, dialect='piper'):
		key, value = row	
		filename = f'{comments}{value}.txt'

		if os.path.exists(filename):
			print(f'Skipping {filename}, file already exists')
			continue
		elif int(value[:4]) < 2019 or (int(value[:4]) == 2019 and int(value[5:-3]) < 7):
			print(f'Skipping {filename}, no dates prior to June 2019')
			continue
		else:
			posts[key] = value

thread = 0
splitname = ''
stride = math.floor(len(posts)/threads)
counter = 0

for i in range(0, len(posts), stride):
	splitname = f'./{counter}.py'
		
	with open(splitname, 'w') as f:
		f.write('from comments import download_comments_by_post\n')

	for j in range(i, i + stride - 1):
		
		if j >= len(posts):
			continue
		
		value = list(posts.items())[j]
		
		with open(splitname, 'a') as f:
			f.write(f'download_comments_by_post(\'{value[0]}\', \'{value[1]}\', \'data/comments/{value[1]}.txt\')\n')

	counter = counter + 1