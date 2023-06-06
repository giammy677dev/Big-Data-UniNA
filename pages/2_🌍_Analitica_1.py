from utils import st, pd, conn, OPENAI_KEY, WordCloud, plt
import nltk
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
nltk.download('stopwords')

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title('Analitiche sugli utenti')

st.write('''In questa sezione si fanno analitiche sugli utenti''')

# Aggiungiamo il filtro per selezionare l'utente da visualizzare
query = "MATCH (u:Utente) RETURN u.screen_name ORDER BY u.screen_name"
query_results = conn.query(query)
string_results = [record['u.screen_name'] for record in query_results]
selected_user = st.selectbox('Seleziona l\'utente:', string_results)

# Layout a due colonne
col1, col2 = st.columns([3, 1])

with col1:
    # Salviamo la description dell'utente selezionato
    query = f"MATCH (u:Utente) WHERE u.screen_name = '{selected_user}' RETURN u.description, u.verified"
    query_results = conn.query(query)
    description_results = [record['u.description'] for record in query_results]
    verified_results = [record['u.verified'] for record in query_results]

    query = f"""MATCH (u:Utente)-[:ha_twittato]-(m:Messaggio)
                WHERE u.screen_name = '{selected_user}'
                RETURN m.followers_count, m.friends_count, m.statuses_count
                ORDER BY m.date
                DESC LIMIT 1"""
    query_results = conn.query(query)
    followers_results = [record['m.followers_count'] for record in query_results]
    friends_results = [record['m.friends_count'] for record in query_results]
    statuses_results = [record['m.statuses_count'] for record in query_results]

    st.write(
        '''
        <div style="background-color: #454545; padding: 15px; border-radius: 5px;">
            {}
            {}
            {}
            {}
            {}
        </div>
        '''.format(
            f'<p style="color: white;">⚠️ L\'utente {selected_user} non ha una descrizione</p>' if
            description_results[0] == '' else f'<p style="color: white;"><b style="color: #00acee;">Descrizione:</b> {description_results[0]}</p>',
            f'<p style="color: white;"><b style="color: #00acee;">Followers:</b> {followers_results[0]}</p>',
            f'<p style="color: white;"><b style="color: #00acee;">Following:</b> {friends_results[0]}</p>',
            f'<p style="color: white;"><b style="color: #00acee;">Numero di tweet:</b> {statuses_results[0]}</p>',
            f'<p style="color: white;">✔️</p>' if verified_results[0] == 'True' else ''
        ),
        unsafe_allow_html=True
    )

# Aggiungiamo l'info box con le informazioni dell'utente selezionato
with col2:
    query = f"MATCH (u:Utente) WHERE u.screen_name = '{selected_user}' RETURN u.cat"
    query_results = conn.query(query)
    string_results = [record['u.cat'] for record in query_results]
    if string_results[0] == 'MYT':
        st.markdown(
            f'<div style="background-color: #00acee; padding: 15px; border-radius: 5px;">'
            f'<p style="color: white;">:warning: L\'utente {selected_user} è stato moderato su YouTube. Giudicando i suoi contenuti su Twitter, l\'indice di pericolosità è tot</p>' # INDICARE INDICE
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background-color: #00acee; padding: 15px; border-radius: 5px;">'
            f'<p style="color: white;"> L\'utente {selected_user} non è stato moderato su YouTube. Giudicando i suoi contenuti su Twitter, l\'indice di pericolosità è tot</p>'  # INDICARE INDICE
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("\n\n")

# Aggiungiamo la tag cloud per l'utente selezionato
stop_words = stopwords.words('english') #Stopwords di nltk
custom_stopwords = set(STOPWORDS) #Stopwords di gensim
custom_stopwords.update(['rt', '', '&amp;', '|']) #Aggiungiamo stopwords personalizzate
custom_stopwords = list(custom_stopwords)

query = f"""MATCH (u:Utente)-[:ha_twittato]->(m:Messaggio) WHERE u.screen_name = '{selected_user}'
WITH m.text AS testo
WITH testo, SPLIT(toLower(testo), ' ') AS parole
UNWIND parole AS parola
WITH parola, COUNT(DISTINCT testo) AS frequenza
WHERE frequenza > 1 AND NOT parola IN {stop_words} AND NOT parola IN {custom_stopwords}
RETURN parola, frequenza
ORDER BY frequenza DESC
"""
query_results = conn.query(query)
frequency_results = [(record['parola'], record['frequenza']) for record in query_results]
frequency_results = [elemento for elemento in frequency_results if len(elemento) > 1]
frequency_dictionary = {str(tupla[0]): int(tupla[1]) for tupla in frequency_results}
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(frequency_dictionary)

# Visualizza il tag cloud in Streamlit
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Explicitly close the connection
conn.close()


import openai
import streamlit as st
import pandas as pd

# Topic dell'utente
topics = ["Politica","Economia","Social Media"]

openai.api_key = "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"

prompt= f"""Per i seguenti argomenti: {topics} restituiscimi un piccolo riassunto dicendo l'utente cosa pensa, nel caso in cui non dice nulla in riferimento a quell'argomento dammi come output "nessuna opinione espressa". Restituiscimi il messaggio di output in questa precisa forma senza scrivere nient altro:
"nome Argomento 1; riassunto su Argomento 1;nome Argomento 2;riassunto Argomento 2;" e così via per tutti gli argomenti sopra elencati."""

testoUtente = "Inserisci testo qui"

"""
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=500,
    temperature=0.7,
    top_p=0.5,
    frequency_penalty=0.5,
    messages=[
        {
          "role" : "user",
          "content": f"{prompt} Il testo da esaminare è il seguente: {testoUtente}",
        },
    ],
)

print(response["choices"][0]["message"]["content"])
"""
#PARTE 2: estrazione e preparazione dati per la tabella
input_string = """Politica; L'utente esprime preoccupazione per il presunto scandalo politico legato a Biden, Obama e Hillary Clinton. Sentimento: Negativo.;Economia; Nessuna opinione espressa.;Social Media; Nessuna opinione espressa."""

#codice reale
#splitted_strings = response["choices"][0]["message"]["content"].split(";")

#da rimpiazzare con quello reale
splitted_strings = input_string.split(";")  # Divisione in base al punto e virgola per ogni stringa

#PARTE 3: TABELLA SUMMARIZATION
# Crea le checkbox per selezionare i topic
selected_topics = st.multiselect("Seleziona i topic", topics)

# Crea una lista vuota per i dati
data = []

# Aggiungi righe alla lista per ogni topic selezionato
for i in range(0, len(splitted_strings), 2):
    topic = splitted_strings[i].strip()  # Primo elemento della riga come topic
    if topic in selected_topics:
        value = splitted_strings[i + 1].strip()  # Secondo elemento della riga come valore
        data.append({"Topic": topic, "Valore": value})

# Crea un DataFrame a partire dalla lista di dati
table = pd.DataFrame(data)

# Mostra la tabella
st.table(table)