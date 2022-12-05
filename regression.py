import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import seaborn as sns
import os
import csv
from scipy.special import softmax
import dateparser
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import keras.api._v2.keras as keras
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Dropout, BatchNormalization, Activation
from keras.models import Sequential
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import minmax_scale

sentiments_filename = './data/sentiments.txt'
prices_filename = './data/sp500.txt'
maximum_days_delayed = 3

def plot(df):

    fig, ax = plt.subplots()
    ax.plot(df['date_date'], df['close'], color='green')
    ax.tick_params(axis='y', labelcolor='green')

    ax2 = ax.twinx()

    ax2.plot(df['date_date'], df['sentiment_mean'], color='red')
    ax2.tick_params(axis='y', labelcolor='red')

prices = pd.read_csv(prices_filename, sep='|', index_col=False).sort_values('date')
prices['change'] = prices['close'] - prices['open']
prices['change%'] = 100 * prices['change'] / prices['open']
prices['up_down'] = np.where(prices['change'] > 0, 1, 0)
prices['date'] = pd.to_datetime(prices['date'])

sentiments = pd.read_csv(sentiments_filename, sep='|', index_col=False).sort_values('date')
sentiments['date'] = pd.to_datetime(sentiments['date'])
sentiments.insert(1, 'next_market_date', sentiments['date'])

# I'm sure there's a much more elegant way to join sentiments to the next day's market movement

for i in range(len(sentiments)):
    date = sentiments.loc[i, 'date']
    
    # Compare sentiment to next day market movement
    
    next_market_date = prices[prices['date'] > date]
    
    if len(next_market_date) > 0:        
        sentiments.loc[i, 'next_market_date'] = next_market_date.iloc[0]['date']

    # Compare but look at sentiment one day after market day

    #next_market_date = prices[prices['date'] < date]
    
    #if len(next_market_date) > 0:        
    #    sentiments.loc[i, 'next_market_date'] = next_market_date.iloc[-1]['date']

sentiments.rename(columns={'date': 'sentiment_date'}, inplace=True)

delayed = sentiments[(sentiments['next_market_date'] - sentiments['sentiment_date']).dt.days > maximum_days_delayed].index
sentiments.drop(delayed, inplace=True)

df = pd.merge(prices, sentiments, how='inner', left_on='date', right_on='next_market_date')

# df[['change%', 'sentiment_mean', 'sentiment_std', 'impact_mean', 'impact_std', 'weekday', 'count']] = minmax_scale(df[['change%', 'sentiment_mean', 'sentiment_std', 'impact_mean', 'impact_std', 'weekday', 'count']])
df['change%'] = minmax_scale(df['change%'])

#plot(df)
#X = df[['count', 'sentiment_mean', 'sentiment_std', 'impact_mean', 'impact_std']]
X = df[['sentiment_mean', 'sentiment_std', 'weekday', 'count']]
#X = df[['sentiment_mean', 'sentiment_std', 'weekday']]
#y = df['change%']
y = df['up_down']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

lr = LinearRegression()
lr.fit(X_train, y_train)
lr.score(X_test, y_test)

nn = Sequential([
    Dense(4, input_shape=(4,), activation='relu'),
    Dense(12, activation='relu'),
    Dense(1, activation='sigmoid')
    ])

nn.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

nn.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=10)