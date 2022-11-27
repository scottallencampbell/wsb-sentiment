import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import seaborn as sns
import tqdm
import os
import csv
from transformers import AutoTokenizer
from transformers import TFAutoModelForSequenceClassification
from scipy.special import softmax

sentiments_filename = './data/sentiments.txt'
comments_path = './data/comments/'
model_ref = f'cardiffnlp/twitter-roberta-base-sentiment'
tokenizer = AutoTokenizer.from_pretrained(model_ref)
model = TFAutoModelForSequenceClassification.from_pretrained(model_ref)

csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)

def sanitize_post(text):
    return re.sub(r'[^a-zA-Z0-9!\',-\\?\\.\\ ]','', text)

def calculate_sentiment(text):
    try:
        sanitized = sanitize_post(text)
        
        if sanitized == 'deleted' or sanitized == '[deleted]':
            print(f'Ignoring deleted text')
            return None

        encoded_text = tokenizer(sanitized, return_tensors='tf')
        output = model(**encoded_text)
        scores = output[0][0].numpy()
        sentiment = softmax(scores)
        return sentiment
    except:
        print(f'Failed to get sentiment for {text}')
        return None

def update_sentiments():  
    print(f'Loading existing sentiments from flat file')
    existing_sentiments = {}
    
    if not os.path.exists(sentiments_filename):
        with open(sentiments_filename, 'a') as f:
            f.write('date|weekday|count|sentiment_mean|sentiment_std|impact_mean|impact_std\n')
    else:
        with open(sentiments_filename, 'r') as psvfile:
            for row in csv.reader(psvfile, dialect='piper'):
                key, value = row[:2]
                existing_sentiments[key] = value

    print(f'Getting comments files')
    comments_files = os.listdir(comments_path)

    for comments_file in comments_files:
        date = comments_file[-14:-4]
        
        if date in existing_sentiments:
            print(f'Skipping {date}.txt, this date has already been evaluated')
        else:
            print(f'Calculating sentiment for {date}.txt')
            calculate_aggregate_sentiment(f'{comments_path}{comments_file}')

def calculate_aggregate_sentiment(filename):
    
    df = pd.read_csv(filename, sep='|', index_col=False,  
        names=['id', 'linkid', 'parentid', 'score', 'body', 'timestamp'])

    if len(df) == 0:
        return

    results = {}

    for i, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        id = row['id']
        body = row['body']
        sentiment = calculate_sentiment(body)

        if sentiment is not None:
            results[id] = sentiment

    roberta = pd.DataFrame(results).T
    roberta.columns = ['neg', 'neu', 'pos']
    roberta = roberta.reset_index().rename(columns={'index': 'id'})
    roberta = roberta.merge(df, how='left')
    roberta['sentiment'] = roberta['pos'] - roberta['neg']
    roberta['impact'] = roberta['sentiment'] * roberta['score']

    save_sentiment(filename, roberta)

def save_sentiment(filename, roberta):
    date = filename[-14:-4]
    weekday = datetime.strptime(date, '%Y-%m-%d').weekday()
    count = roberta.shape[0]

    sentiment_mean = roberta['sentiment'].mean()
    sentiment_std = roberta['sentiment'].std()

    impact_mean = roberta['impact'].mean()
    impact_std = roberta['impact'].std()

    vals = '|'.join([
        date,
        str(weekday),
        str(count),
        str(sentiment_mean),
        str(sentiment_std),
        str(impact_mean),
        str(impact_std)
    ]) + '\n'

    with open(sentiments_filename, 'a') as f:
        f.write(vals)
