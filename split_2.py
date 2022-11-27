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

sentiments_file = './data/sentiments.txt'
comments_path = './data/comments/'
threads = 3

csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

print(f'Loading existing comments from directory')
comments_files = os.listdir(comments_path)

print(f'Loading sentiments from flat file')
sentiments = {}

with open(sentiments_file, 'r') as psvfile:
	for row in csv.reader(psvfile, dialect='piper'):
		key = row[0]
		value = row[1]
		sentiments[key] = value

for comments_file in comments_files:
	date = comments_file[:10]
	
	if date in sentiments:
		print(f'Skipping {comments_file}, this date has already been evaluated')

#filename = f'{comments_path}{value}.txt'

thread = 0
splitname = ''
stride = math.ceil(len(sentiments)/threads)
counter = 0

for i in range(0, len(sentiments), stride):
	splitname = f'./{counter}.py'
		
	with open(splitname, 'w') as f:
		f.write('from sentiment import calculate_aggregate_sentiment\n')

	for j in range(i, i + stride - 1):
		
		if j >= len(sentiments):
			continue
		
		value = list(sentiments.items())[j]
		
		with open(splitname, 'a') as f:
			f.write(f'calculate_aggregate_sentiment(\'./data/comments/{value[0]}.txt\')\n')

	counter = counter + 1
