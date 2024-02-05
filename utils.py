from neo4j import GraphDatabase
import openai
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import nltk
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from scipy.special import softmax
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
from math import floor
import time
nltk.download('stopwords')

batch_size = 5000

openai.api_key = "sk-API-KEY"

# Stopwords
stop_words = stopwords.words('english') #Stopwords di nltk
custom_stopwords = set(STOPWORDS) #Stopwords di gensim
custom_stopwords.update(['rt', '', '&amp;', '|', 'it\'s']) #Aggiungiamo stopwords personalizzate
custom_stopwords = list(custom_stopwords)

# Carichiamo il tokenizer ed il modello pre-addestrato di sentiment analysis
MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Definizione dei range di valore e dei corrispondenti testi e colori
ranges = [(-1, -0.7, 'Estremamente negativo', '#D10000'),
          (-0.7, -0.4, 'Negativo', '#FF0000'),
          (-0.4, -0.2, 'Leggermente Negativo', '#FF4242'),
          (-0.2, 0.2, 'Neutro', 'lightgray'),
          (0.2, 0.4, 'Leggermente Positivo', 'lightgreen'),
          (0.4, 0.7, 'Positivo', 'mediumseagreen'),
          (0.7, 1, 'Estremamente positivo', 'green')]

# Dizionario per la mappatura dei nomi completi dei mesi alle forme abbreviate
month_abbreviations = {
    'January': 'Jan',
    'February': 'Feb',
    'March': 'Mar',
    'April': 'Apr',
    'May': 'May',
    'June': 'Jun',
    'July': 'Jul',
    'August': 'Aug',
    'September': 'Sep',
    'October': 'Oct',
    'November': 'Nov',
    'December': 'Dec'
}


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


conn = Neo4jConnection(uri="neo4j+s://021210b0.databases.neo4j.io", user="neo4j", pwd="jOYU-cr88yKi0CFddGaPETtuWSqYzE53sS1dH5zPB94")


# Elenco con bullet list e link ai collegamenti delle sezioni
def elenco_bullet(testo_grassetto, testo_normale):
    st.markdown(f"- <span style='color:#00acee'><b>{testo_grassetto}</b></span>: {testo_normale}",
                unsafe_allow_html=True)


# Se il testo supera il limite di token previsto da chatGPT, dividilo in batch
def split_string_in_batches(stringa, batch_size):
    batches = []
    length = len(stringa)
    start_index = 0
    end_index = batch_size

    while start_index < length:
        if end_index >= length:
            end_index = length

        batch = stringa[start_index:end_index]
        batches.append(batch)

        start_index = end_index
        end_index += batch_size
    return batches


def perform_sentiment_analysis(_text):
    # Tokenizzazione del testo di input
    input = tokenizer(_text, padding=True, truncation=True, max_length=512, return_tensors="pt")

    # Inferenza del modello
    output = model(**input)

    # Ottieni le predizioni del modello
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    positive_score = float(scores[config.label2id["positive"]])
    neutral_score = float(scores[config.label2id["neutral"]])
    negative_score = float(scores[config.label2id["negative"]])

    sentiment_value = (positive_score + (neutral_score / 2)) - negative_score
    return sentiment_value
