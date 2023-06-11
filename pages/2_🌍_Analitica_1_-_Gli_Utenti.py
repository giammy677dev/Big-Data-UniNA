from utils import st, conn, WordCloud, plt, openai
from utils import floor, time, batch_size, stop_words, custom_stopwords, ranges
from utils import split_string_in_batches, perform_sentiment_analysis
import nltk
import plotly.graph_objects as go
nltk.download('stopwords')

st.set_page_config(
    page_title="Analitica 1 - Gli Utenti",
    page_icon="🌍",
)

st.title('🌍 Analitica 1 - Gli Utenti')

st.write('''In questa sezione è possibile effettuare diverse analitiche sugli utenti. Viene prima riportata una breve
            bio dell'utente. Successivamente, è possibile visualizzare una tag cloud che rappresenta le parole più
            utilizzate dall'utente selezionato nei propri tweet.''')

# Aggiungiamo il filtro per selezionare l'utente da visualizzare
query = "MATCH (u:Utente) RETURN u.screen_name ORDER BY u.screen_name"
query_results = conn.query(query)
string_results = [record['u.screen_name'] for record in query_results]
selected_user = st.selectbox('Seleziona l\'utente:', string_results, index=11)

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

    with st.expander("Info Box dell'utente", expanded=True):
        if verified_results[0] == 'True':
            col11, col12 = st.columns([1, 15])
            with col11:
                st.image('utility/twitterVerifiedBadge.png', width=25)
            with col12:
                st.write("L'utente è verificato!")
        st.write(
            '''
                {}
                {}
                {}
                {}
            '''.format(
                f'<p style="color: white;">⚠️ L\'utente {selected_user} non ha una descrizione</p>' if
                description_results[
                    0] == '' else f'<p style="color: white;"><b style="color: #00acee;">Descrizione:</b> {description_results[0]}</p>',
                f'<p style="color: white;"><b style="color: #00acee;">Followers:</b> {followers_results[0]}</p>',
                f'<p style="color: white;"><b style="color: #00acee;">Following:</b> {friends_results[0]}</p>',
                f'<p style="color: white;"><b style="color: #00acee;">Numero di tweet:</b> {statuses_results[0]}</p>'
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
            f'<div style="display: flex; flex-direction: column; align-items: center;">'
            f'<span style="font-size: 30px;">⚠️</span>'
            f'<p style="color: white; text-align: center;">L\'utente {selected_user} ha condiviso video che sono stati moderati su YouTube.</p>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background-color: #00acee; padding: 15px; border-radius: 5px;">'
            f'<p style="color: white; text-align: center;">L\'utente {selected_user} non ha condiviso video che sono stati moderati su YouTube.</p>'  # INDICARE INDICE
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("\n\n")

# Aggiungiamo la tag cloud per l'utente selezionato

query = f"""MATCH (u:Utente)-[:ha_twittato]->(m:Messaggio)
            WHERE u.screen_name = '{selected_user}'
            WITH m.text AS testo
            WITH testo, SPLIT(toLower(testo), ' ') AS parole
            UNWIND parole AS parola
            WITH REPLACE(REPLACE(REPLACE(parola, ':', ''), ',', ''), '.', '') AS word_without_punckt, 
                COUNT(DISTINCT testo) AS frequenza
            WHERE frequenza > 1 AND NOT word_without_punckt IN {stop_words} 
                AND NOT word_without_punckt IN {custom_stopwords}
            RETURN word_without_punckt AS parola, frequenza
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

st.write("---------------------------------")

st.header("Summarization per topic scelti")

st.write("""In questa sezione è possibile scegliere uno dei topic trattati dall'utente per ottenere un breve riassunto
            estratto dai tweet da lui pubblicati. Tale riassunto esprime la posizione dell'utente per il topic selezionato.""")


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
def chatGPT_script(selected_topic, user):
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


# Crea il multiselect per selezionare i topic
selected_topic = st.multiselect("Seleziona i topic:", [topic[1] for topic in tweets_results])


# Effetto di scrittura chatGPT-style
@st.cache_data(show_spinner=False)
def type_string_GPT_style(string):
    text_placeholder = st.empty()
    for i in range(1, len(string) + 1):
        typed_text = string[:i]
        text_placeholder.markdown(typed_text)
        time.sleep(0.02)


sentiment_values = []
selected_topics = []

# Facciamo la summarization dei tweet e la sentiment analysis
for topic in selected_topic:
    with st.expander(topic):
        chatGPT_response = chatGPT_script(topic, selected_user)
        response_string = chatGPT_response["Response"][0]
        type_string_GPT_style(response_string)

    for tweet, selected_topic in tweets_results:
        if topic == selected_topic:
            text = tweet
            sentiment = perform_sentiment_analysis(text)
            sentiment = round(sentiment, 2)
            sentiment_values.append(sentiment)
            selected_topics.append(topic)

# Creazione dell'istogramma solo se sono presenti valori di sentiment
if sentiment_values:
    fig = go.Figure(data=[go.Bar(x=selected_topics, y=sentiment_values, width=0.3)])

    color_values = []

    for sentiment in sentiment_values:
        for i, range_ in enumerate(ranges):
            if range_[0] <= sentiment < range_[1]:
                color_values.append(range_[3])
                break

    # Assegnazione del colore alle barre in base al valore
    color_scale = 'RdYlGn'  # Scala di colore da rosso a verde

    fig.update_traces(marker=dict(color=color_values, colorscale=color_scale))

    fig.update_layout(
        title = 'Grafico del Sentiment per Topic',
        xaxis_title='Topic',
        yaxis_title='Sentiment',
        yaxis_range=[-1, 1]
    )

    st.write("-------------------------------------------")
    st.header("Sentiment Analysis dei topic scelti")
    st.write("""Di seguito viene riportato un grafico a barre verticali che rappresenta il sentiment dell'utente selezionato
                rispetto al topic scelto. Il valore del sentiment è compreso tra -1 (estremo negativo) e 1 (estremo positivo).
            """)
    # Visualizzazione del grafico
    st.plotly_chart(fig)

# Explicitly close the connection
conn.close()
