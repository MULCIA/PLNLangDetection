# We Need to download full europarl at http://nltk.ldc.upenn.edu/packages/corpora/europarl_raw.zip

# ~$ python3 train.py languages.txt europarl_raw

import os
import re
import argparse
import pickle
import random

from os import listdir

from os.path import isfile, join

from tqdm import tqdm

from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

def get_directories(data_path, languages):
    directories = [d for d in listdir(data_path) if not d.startswith('.')]
    for language in languages:
        if language not in directories:
            print("Cannot find '" + language + "'' directory into filesystem.")
            print("Please, check if exists '" + language + "'' into europarl_raw directory or remove from languages.txt.")
            languages = list()
            break
    return languages

def find_files(data_path, languages_for_training):
    files = dict()
    languages = get_directories(data_path, languages_for_training) 
    for lang in languages:
        files[lang] = [f for f in listdir('%s/%s/'%(data_path,lang)) if not f.startswith('.')]
        print("%s : %i ficheros" %(lang,len(files[lang])))
    return files

def get_chunks(words):
    sentences = list()

    offset = 0
    chunk_len = random.randint(1,20)
    rest = len(words) - chunk_len
    
    while rest > 0:
        chunk = words[offset:offset+chunk_len]
        sentences.append(' '.join(chunk))
        offset += chunk_len
        chunk_len = random.randint(1,20)
        rest -= chunk_len

    return sentences

def get_sentences(text):
    words = re.compile('\w+').findall(text)
    return get_chunks(words) 

def parse_files(data_path):
    X_set = list()
    y_set = list()
    languages = [d for d in listdir(data_path) if not d.startswith('.')]
    for lang in languages:
        files = [f for f in listdir('%s/%s/'%(data_path,lang)) if not f.startswith('.')]
        for fil in tqdm(files):
            with open('%s/%s/%s'%(data_path, lang, fil)) as f:
                sentences = get_sentences(f.read())
                for sentence in sentences:
                    X_set.append(sentence)
                    y_set.append(lang)
    return X_set,y_set

if __name__ == "__main__":

    #Get arguments
    parser = argparse.ArgumentParser(description='Train model for document classification')
    parser.add_argument('languages', metavar='M', type=str, help='Languages for training')
    parser.add_argument('dataset', metavar='D', type=str, help='Folder containing the documents within the subfolders')
    args = parser.parse_args()

    #Find and Report
    languages_for_training = list(open(args.languages,'r'))[0].rstrip().split(',') #Remove \n
    
    files = find_files(args.dataset, languages_for_training)

    #Get dataset
    X_train, y_train = parse_files(args.dataset)

    pipe = Pipeline([
        ('vectorizer', TfidfVectorizer(stop_words=stopwords.words('english'), min_df=0)),
        ('classifier', MultinomialNB(alpha=0.0005)),
    ])

    model = pipe.fit(X_train,y_train)

    with open('model.pickle', 'wb') as f:
        pickle.dump(pipe, f, protocol=2)