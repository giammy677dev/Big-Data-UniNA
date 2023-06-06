from neo4j import GraphDatabase
import openai
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

openai.api_key = "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"


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

# Esempio d'uso di Neo4j
'''
result = "MATCH (p:Partenza) RETURN p.Citta_Partenza"
dtf_data = DataFrame([dict(_) for _ in conn.query(result)])

print(dtf_data)

# Explicitly close the connection
conn.close()
'''

# Esempio d'uso di ChatGPT
'''
input= "Inserisci testo qui"
prompt = """Inserisci testo qui"""

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=500,
    temperature=0.7,
    top_p=0.5,
    frequency_penalty=0.5,
    messages=[
        {
          "role" : "user",
          "content": f"Sulla base di questo: {prompt} rispondi alla seguente domanda: {input}",
        },
    ],
)

print(response["choices"][0]["message"]["content"])
'''