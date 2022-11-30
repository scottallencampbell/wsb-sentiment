import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import seaborn as sns
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

plt.style.use('ggplot')

def sanitizePost(text):
    return ' '.join(re.sub('[0-9]+', '', text).split())

df = pd.read_csv('data/comments/2022-10-31.txt', sep='|', index_col=False,  
    names=['id', 'linkid', 'parentid', 'score', 'body', 'timestamp'])

sia = SentimentIntensityAnalyzer()
results = {}

for i, row in df.iterrows():
    id = row['id']
    body = row['body']
    score = row['score']
    rating = sia.polarity_scores(body)
    results[id] = rating

vaders = pd.DataFrame(results).T
vaders = vaders.reset_index().rename(columns={'index': 'id'})
vaders = vaders.merge(df, how='left')


print(vaders.head())

