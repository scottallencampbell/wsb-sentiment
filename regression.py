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

sentiments_filename = './data/sentiments.txt'
prices_filename = './data/sp500.txt'

prices = pd.read_csv(prices_filename, sep='|', index_col=False)
prices['date'] = pd.to_datetime(prices['date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
prices['change'] = prices['close'] - prices['open']
prices['change%'] = 100 * prices['change'] / prices['open']

sentiments = pd.read_csv(sentiments_filename, sep='|', index_col=False)

df = pd.merge(prices, sentiments, on='date')

#plt.figure()
#sns.pairplot(df[['change%', 'sentiment_mean', 'sentiment_std', 'impact_mean', 'impact_std']],  markers=["o", "s"])
#plt.show()

X = df[['count', 'sentiment_mean', 'sentiment_std', 'impact_mean', 'impact_std']]
y = df['change%']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

lr = LinearRegression()
lr.fit(X_train, y_train)