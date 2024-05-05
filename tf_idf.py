import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

data = pd.read_csv("learn-ai-bbc/bbc_news_train.csv", usecols=['Text'])['Text'].tolist()
data.extend(pd.read_csv("learn-ai-bbc/bbc_news_test.csv", usecols=['Text'])['Text'].tolist())

tfidfvectorizer = TfidfVectorizer(analyzer='word',stop_words= 'english')
tfidf_wm = tfidfvectorizer.fit_transform(data)

joblib.dump()

print(tfidf_wm)
