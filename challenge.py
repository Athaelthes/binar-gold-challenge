import re
import sqlite3
import numpy as np
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from flask import Flask, jsonify


from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)

app.json = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Challenge: Membuat API untuk Cleansing Data dan Laporan Analisis Data'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/Teks via Form', methods=['POST'])
def text_processing():
    
    text_input = request.form.get('text')
    text_output = clean_tweet(text_input)

    json_response = {
        'input' : text_input,
        'output' : text_output,
    }  

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/file_processing.yml", methods=['POST'])
@app.route('/Upload File CSV', methods=['POST'])
def file_processing():
    
    file = request.files('file')
    df_csv = pd.read_csv(file, encoding="latin-1")
    df_csv = df_csv['Tweet Hate and Abuse Speech']
    df_csv = df_csv.drop_duplicates()

    df_csv = df_csv.values.tolist()
    i = 0
    data = {}
    for text in df_csv:
        data[i] = {}
        data[i]['tweet'] = text
        data[i]['cleansing_tweet'] = clean_tweet(text)
        i = i + 1

    return data

sastrawi_stopwords = StopWordRemoverFactory().get_stop_words()
stemmer = StemmerFactory().create_stemmer()

def symbol(tweet):
    if type(tweet) == np.float:
        return ""
    temp = tweet.lower()
    temp = re.sub("'", "", temp) 
    temp = re.sub("@[A-Za-z0-9_]+","", temp)
    temp = re.sub("#[A-Za-z0-9_]+","", temp)
    temp = re.sub(r'http\S+', '', temp)
    temp = re.sub('[()!?]', ' ', temp)
    temp = re.sub('\[.*?\]',' ', temp)
    temp = re.sub("[^a-z0-9]"," ", temp)
    temp = temp.split()
    temp = [w for w in temp if not w in sastrawi_stopwords]
    temp = " ".join(word for word in temp)
    return temp

database = sqlite3.connect('/Users/macupicho/Downloads/Challenge Gold/datachallenge/tugas_challenge.db', check_same_thread = False)

x = 'SELECT * FROM kamusalay'
xq = pd.read_sql_query(x, database)
dict_alay = dict(zip(xq['alay'], xq['normal']))
def baku(dari_alay):
    for word in dict_alay:
        return ' '.join([dict_alay[word] if word in dict_alay else word for word in dari_alay.split(' ')])
    
y = 'SELECT * FROM abusive'
read_y = pd.read_sql_query(y, database)
def normalize(dari_abusive):
    list_word = dari_abusive.split()
    return ' '.join([s for dari_abusive in list_word if dari_abusive not in read_y])

def clean_tweet(clean):
    clean = clean.lower()
    clean = symbol(clean)
    clean = baku(clean)
    clean = normalize(clean)
    return clean

if __name__ == '__main__':
    app.run()