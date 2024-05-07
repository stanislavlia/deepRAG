import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import re
import string



def remove_url(text):
 return re.sub(r'https?:\S*', '', text)

def remove_mentions_and_tags(text):
    text = re.sub(r'@\S*', '', text)
    return re.sub(r'#\S*', '', text)


def remove_special_characters(text):
    # define the pattern to keep
    pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]' 
    return re.sub(pat, '', text)


def remove_numbers(text):
    pattern = r'[^a-zA-z.,!?/:;\"\'\s]' 
    return re.sub(pattern, '', text)

def remove_punctuation(text):
    return ''.join([c for c in text if c not in string.punctuation])


def clean_text(text):

    lowered_text = text.lower()
    removed_tags_text = remove_mentions_and_tags(lowered_text)
    removed_urls_text = remove_url(removed_tags_text)
    removed_spec_chars_text = remove_special_characters(removed_urls_text)
    cleaned_text = remove_numbers(removed_spec_chars_text)


    return cleaned_text
    

data = pd.read_csv("/home/jgoldste/projects/ft_search/learn-ai-bbc/bbc_news_train.csv", usecols=['Text'])['Text'].tolist()
data.extend(pd.read_csv("/home/jgoldste/projects/ft_search/learn-ai-bbc/bbc_news_test.csv", usecols=['Text'])['Text'].tolist())
data = [clean_text(s) for s in data]

tfidfvectorizer = TfidfVectorizer(analyzer='word',
                                  stop_words= 'english',
                                 max_features=3000)


tfidfvectorizer.fit(data)

joblib.dump(tfidfvectorizer, '/home/jgoldste/projects/ft_search/wm_handling/tfidf_vec.joblib')

tfidfvectorizer_new = joblib.load('/home/jgoldste/projects/ft_search/wm_handling/tfidf_vec.joblib')

print(*sorted(list(tfidfvectorizer_new.vocabulary_.keys()))[:100], sep='\n')