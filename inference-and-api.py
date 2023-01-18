# [START gae_flex_quickstart]
import datetime
import numpy as np
from flask import Flask, request, Response
#from gensim.models import Word2Vec
import xgboost as xgb
import json
from google.cloud import datastore
datastore_client = datastore.Client()
wordMap = json.load(open('keyMap.json'))
bst = xgb.Booster({'nthread': 4})  # init model
bst.load_model('101C-02.model')  # load data

import requests
url = "https://api.yelp.com/v3/businesses/"
headers = {
    "accept": "application/json",
    "Authorization": "[REDACTED]"
}


import spacy
import nltk
import re
from nltk.stem import WordNetLemmatizer
stemmer = WordNetLemmatizer()
nltk.download('wordnet')
nltk.download('omw-1.4')
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)


@app.route('/')
def root():
    # get text
    text = request.args.get('q')
    if(text == None):
        return Response("{'error': 'No query parameter passed'}", status=400, mimetype='application/json')

    try:
        text_arr = process(str(text))

        if len(text_arr) < 1:
            return Response("{'error': 'Length of preprocessed query is zero'}", status=400, mimetype='application/json')

        # average all the words
        conglomerate = np.zeros(50)
        for vec in text_arr:
            conglomerate = np.add(conglomerate, np.array(vec))
        conglomerate = np.divide(conglomerate, np.ones_like(conglomerate)*len(text_arr))

        print(conglomerate)

        ypred = bst.predict(xgb.DMatrix(conglomerate.reshape((1,-1))))

        sorted_first_10 = np.argsort(ypred[0])[::-1][:10]
        print(sorted_first_10)

        ids = [wordMap[str(id)] for id in sorted_first_10]
        print(ids)
        restaurants = []

        for id in ids:
            response = requests.get(url + id, headers=headers)
            print(response.text)
            restaurants.append(response.text)

        
        http_response = Response(json.dumps({'restaurants': restaurants}), status=200, mimetype='application/json')
        http_response.headers['Access-Control-Allow-Origin'] = '*'
        return http_response

    except Exception as e:
        return Response("{'error': '" + e + "'}", status=400, mimetype='application/json')

    return {'hello': 'world'}


def process(document):
    stopWords = nlp.Defaults.stop_words
    # Remove all the special characters, like parathesis
    document = re.sub(r'\W', ' ', document)
    # remove all single characters: like a, b, c, d
    document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
    # Remove single characters from the start
    document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)
    # Substituting multiple spaces with single space
    document = re.sub(r'\s+', ' ', document, flags=re.I)
    # Removing prefixed 'b'
    document = re.sub(r'^b\s+', '', document)
    # Lower case
    document = document.lower()
    # Lemmatization
    document = document.split()
    document = [stemmer.lemmatize(word) for word in document]
    # Remove stop words
    document = [word for word in document if word not in stopWords]
    print(document)
    # Remove words that aren't in the embedding dictionary
    word2vec = []
    for word in document:
        fetched = datastore_client.get(datastore_client.key('[default]', word))
        if fetched is not None:
            word2vec.append([float(n) for n in fetched['vec_string'].split(" ")])
    return word2vec

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]
