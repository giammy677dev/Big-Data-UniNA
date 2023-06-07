from utils import st, pd, conn, WordCloud, plt, openai
import nltk
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
from math import floor
nltk.download('stopwords')

batch_size = 5000

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
custom_stopwords.update(['rt', '', '&amp;', '|', 'it\'s']) #Aggiungiamo stopwords personalizzate
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

# Aggiungiamo il box per la summarization dell'utente selezionato
# Selezioniamo i topic dell'utente e mergiamo i testi dei tweet relativi a quel topic
query = f"""MATCH (u:Utente)-[:ha_twittato]->(m:Messaggio)
            WHERE u.screen_name = '{selected_user}'
            WITH m, SPLIT(m.topic, ';') AS topics
            UNWIND topics AS topic
            WITH topic, COLLECT(m.text) AS texts
            WITH topic, [text IN texts | REDUCE(s = '', word IN SPLIT(text, ' ') | CASE WHEN NOT word CONTAINS 'http' THEN s + ' ' + word ELSE s END)] AS filteredTexts
            RETURN topic, REDUCE(mergedText = '', text IN filteredTexts | mergedText + ' ' + text) AS mergedText
        """
query_results = conn.query(query)
tweets_results = [(record['mergedText'], record['topic']) for record in query_results]

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


def chatGPT_request(text):
    prompt = f"""Dammi in output il riassunto in italiano in un unico testo della posizione dell'utente."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=2000,
        temperature=0.7,
        top_p=0.5,
        frequency_penalty=0.5,
        messages=[
            {
                "role": "user",
                "content": f"{prompt} Il testo da esaminare è il seguente: {text}",
            },
        ],
    )
    summary_response = response["choices"][0]["message"]["content"]
    return summary_response


@st.cache_data
def chatGPT_script(selected_topic):
    text = ''
    response_dict = {"Topic": [], "Response": []}
    for tweet, topic in tweets_results:
        if topic == selected_topic:
            text = tweet
            break
    batches = split_string_in_batches(text, batch_size)
    if len(batches) == 1:
        full_response = batches[0]
    elif len(batches) == 2:
        first_batch = batches[0]
        second_batch = batches[1]
        first_response = chatGPT_request(first_batch)
        second_response = chatGPT_request(second_batch)
        full_response = first_response + second_response
    else:
        first_batch = batches[0]
        central_batch = batches[floor(len(batches)/2)]
        last_batch = batches[len(batches)-1]
        first_response = chatGPT_request(first_batch)
        central_response = chatGPT_request(central_batch)
        last_response = chatGPT_request(last_batch)
        full_response = first_response + central_response + last_response
    response = chatGPT_request(full_response)
    response_dict["Topic"].append(selected_topic)
    response_dict["Response"].append(response)
    return response_dict


# Crea le checkbox per selezionare i topic
selected_topic = st.multiselect("Seleziona i topic", [topic[1] for topic in tweets_results])

if len(selected_topic) >= 1:
    chatGPT_response = chatGPT_script(selected_topic[len(selected_topic) - 1])
    st.write(chatGPT_response)
    """
    # Aggiungi righe alla lista per ogni topic selezionato
    for topic, value in chatGPT_response:
        topic = chatGPT_response["Topic"][0]  # Primo elemento della riga come topic
        value = chatGPT_response["Response"][0]  # Secondo elemento della riga come valore
        data.append({"Topic": topic, "Valore": value})
    # Crea un DataFrame a partire dalla lista di dati
    table = pd.DataFrame(data)

    # Mostra la tabella
    st.table(table)
    """
# Explicitly close the connection
conn.close()
