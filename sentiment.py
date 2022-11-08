import pandas as pd
import re
from textblob import TextBlob

def sanitizePost(text):
    return ' '.join(re.sub('[0-9]+', '', text).split())

df = pd.read_csv('data/comments/2022-10-31.txt', sep='|', index_col=False,  
    names=['id', 'linkid', 'parentid', 'score', 'body', 'timestamp'])

for index, row in df.iterrows():
    print(row['id'])
   #print(row['id'], sanitizePost(row['body']))

print(df)

