from utils import st, conn, pd, openai, floor, np
from utils import time, batch_size, ranges
from utils import split_string_in_batches, perform_sentiment_analysis
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Analitica 2 - I Topic",
    page_icon="📈",
)

st.title('📈 Analitica 2 - I Topic')

st.write("""In questa sezione è possibile visualizzare diverse analitiche sui topic. Oltre ad un bar chart race che riporta
            l'andamento dei topic più discussi nel tempo, è possibile selezionare un topic specifico al fine di visualizzare
            appositi grafici che riportano il sentiment generale degli utenti rispetto a quel topic. Infine, viene messo
            a disposizione un box in cui è possibile inserire del testo tramite il quale è possibile ricevere un breve
            riassunto delle opinioni degli utenti rispetto alle parole inserite nel box stesso.
        """)

# Aggiungiamo il filtro per selezionare i topic da visualizzare
query = """MATCH (m:Messaggio)
           WITH m, SPLIT(m.topic, ';') AS topics
           UNWIND topics AS topic
           RETURN DISTINCT topic"""
query_results = conn.query(query)
string_results = [record['topic'] for record in query_results]
selected_topic = st.selectbox('Seleziona il topic:', string_results)


# Sentiment analysis
@st.cache_data(show_spinner=False)
def draw_pie_chart(topic):
    # Andiamo a selezionare per ogni utente i testi inerenti al topic selezionato
    query = f"""MATCH (u:Utente)-[a:ha_twittato]->(m:Messaggio)
                WHERE m.topic CONTAINS '{topic}'
                RETURN u.screen_name, 
                REDUCE(output = "", msg IN COLLECT(m.text) | output + " " + msg) AS combined_text
                """
    query_results = conn.query(query)
    user_text_results = [(record['u.screen_name'], record['combined_text']) for record in query_results]

    sentiment_topic_values = []

    for user, tweet in user_text_results:
        sentiment = perform_sentiment_analysis(tweet)
        sentiment_topic_values.append(sentiment)

    positive = [val for val in sentiment_topic_values if val > 0.3]
    neutral = [val for val in sentiment_topic_values if -0.3 <= val <= 0.3]
    negative = [val for val in sentiment_topic_values if val < -0.3]

    labels = ['Sentiment Positivo', 'Sentiment Neutrale', 'Sentiment Negativo']
    values = [len(positive), len(neutral), len(negative)]

    # Definizione dei colori per areogramma
    colors = ['green', 'lightgray', 'red']

    # Creazione dell'areogramma
    fig = px.pie(values=values, names=labels, color_discrete_sequence=colors)

    # Personalizzazione del layout
    fig.update_layout(showlegend=False, width=300, height=300)

    # Modifica le etichette di hover del mouse
    fig.update_traces(hovertemplate='Categoria: %{label}')

    # Visualizzazione dell'areogramma
    st.plotly_chart(fig)


st.write("-------------------------------------------------------------------------------")
st.write("**Bar Chart Race dei Topic ed Areogramma del sentiment**")
st.write("""La Bar Chart Race riportata di seguito permette di visualizzare come, nel tempo, l'attenzione degli utenti
            si è spostata da un topic all'altro. Inoltre, viene riportato un areogramma che mostra la distribuzione percentuale
            del sentiment rispetto al topic selezionato. Questo permette di comprendere l'opinione generale degli utenti
            rispetto ad un determinato topic.
         """)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("<br>", unsafe_allow_html=True)
    # Percorso del video del bar chart race
    video_path = "utility/bcr.mp4"

    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()

    # Embedding del video all'interno di un box
    st.video(video_bytes)
with col2:
    draw_pie_chart(selected_topic)


@st.cache_data(show_spinner=False)
def draw_histogram(topic):
    # Prendiamo i testi che contengono il topic selezionato nel campo topic
    # Aggiungiamo il filtro per selezionare i topic da visualizzare
    query = f"""MATCH (m:Messaggio)
                WHERE m.topic CONTAINS '{selected_topic}'
                RETURN m.text, LEFT(m.date, 10) AS data
                ORDER BY data
            """
    query_results = conn.query(query)
    selected_topic_results = [(record['m.text'], record['data']) for record in query_results]

    # Creazione del DataFrame pandas con i dati
    df = pd.DataFrame(selected_topic_results, columns=['text', 'data'])

    # Conversione del campo "date" in formato datetime
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

    # Raggruppamento dei testi per mese di quell'anno
    grouped_texts = df.groupby(df['data'].dt.to_period('M'))['text'].apply(list)

    # Creazione del dizionario
    month_dict = {str(month): texts for month, texts in grouped_texts.items()}

    monthly_texts = {}

    for month, texts in month_dict.items():
        combined_text = ' '.join(texts)
        monthly_texts[month] = combined_text

    sentiment_values = []
    month_list = list(monthly_texts.keys())

    for month in month_list:
        text_month = monthly_texts[month]
        sentiment = perform_sentiment_analysis(text_month)
        sentiment_values.append(sentiment)

    fig = px.line(x=month_list, y=sentiment_values, markers=False)

    fig.update_layout(
        title='Sentiment Mensile',
        xaxis_title='Mesi',
        yaxis_title='Sentiment',
        yaxis_range=[-1, 1],
        height=400  # Altezza del grafico
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.write("**Grafico temporale dell'andamento del sentiment**")

    st.write("Il seguente grafico temporale permette di visualizzare come cambia il sentiment degli utenti nel corso del tempo rispetto al topic selezionato.")

    # Visualizzazione del grafico
    st.plotly_chart(fig)


draw_histogram(selected_topic)

st.write("-------------------------------")
st.header("Summarization per keyword")
st.write("""Inserendo una o più parole chiave nel box sottostante, verrà generato accanto un riassunto che esprime la
            posizione degli utenti che hanno utilizzato tali parole chiave nei propri tweet.""")


def chatGPT_request(text):
    prompt = f"""Dammi in output il riassunto in italiano in un unico testo della posizione degli utenti."""
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
def chatGPT_script_for_text(text):
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
    return response

# Effetto di scrittura chatGPT-style
@st.cache_data(show_spinner=False)
def type_string_GPT_style(string):
    text_placeholder = st.empty()
    for i in range(1, len(string) + 1):
        typed_text = string[:i]
        text_placeholder.markdown(typed_text)
        time.sleep(0.02)


sentiment_result = []

col3, col4 = st.columns(2)

with col3:
    # Creazione del box di testo
    user_text = st.text_area("Inserisci il testo qui:", value="", height=10)
    user_text = user_text.lower()

    # Bottone per salvare il testo
    if st.button("Ricerca"):
        # Aggiungiamo il filtro per selezionare i topic da visualizzare
        query = f"""MATCH (m:Messaggio)
                    WHERE toLower(m.text) CONTAINS '{user_text}'
                    RETURN REDUCE(s = '', x IN COLLECT(m.text) | s + ' ' + x) AS combined_text
                """
        query_results = conn.query(query)
        text_results = [record['combined_text'] for record in query_results]

        query = f"""MATCH (m:Messaggio)
                    WHERE toLower(m.text) CONTAINS '{user_text}'
                    RETURN m.text
                """
        query_results = conn.query(query)
        sentiment_result = [record['m.text'] for record in query_results]
    else:
        text_results = "NULL"
    user_text = ''

with col4:
    st.write("Summarization:")
    if text_results[0] == "":
        response_text = "Gli utenti non hanno discusso di questo argomento."
    elif len(text_results) > 0 and text_results != "NULL":
        response_text = chatGPT_script_for_text(text_results[0])
    elif text_results == "NULL":
        response_text = ''

    type_string_GPT_style(response_text)

if len(text_results) > 0 and text_results != "NULL":
    st.write("------------------------------------------------------")
    st.write("**Areogramma del sentiment generato dei tweet sull'argomento ricercato**")
    st.write(f"""Di seguito viene riportato un areogramma che mostra, in percentuale, il sentiment generato dai tweet
                sull'argomento ricercato.
            """)
    # Recupero i testi dei tweet che hanno risposto o citato (senza retweet) questo tweet per una sentiment analysis 'media'
    sentiment_list = []

    for text in sentiment_result:
        sentiment_values = perform_sentiment_analysis(text)
        sentiment_list.append(sentiment_values)

    # Calcolo delle percentuali dei sentiment
    sentiment_counts = np.zeros(len(ranges))
    for sentiment in sentiment_list:
        for i, range_ in enumerate(ranges):
            if range_[0] <= sentiment < range_[1]:
                sentiment_counts[i] += 1
                break
    total_tweets = len(sentiment_list)
    sentiment_percentages = sentiment_counts / total_tweets

    # Areogramma delle percentuali dei sentiment
    labels = [range_[2] for range_ in ranges]
    colors = [range_[3] for range_ in ranges]
    explode = [0.1] + [0] * (len(ranges) - 1)  # Esplosione della prima fetta

    fig_sentiment_percentages = []
    fig_labels = []
    fig_colors = []

    for i in range(len(sentiment_percentages)):
        if sentiment_percentages[i] != 0:
            fig_sentiment_percentages.append(sentiment_percentages[i])
            fig_labels.append(labels[i])
            fig_colors.append(colors[i])

    fig = go.Figure(data=[go.Pie(labels=fig_labels, values=fig_sentiment_percentages, marker=dict(colors=fig_colors),
                                 hoverinfo='label+percent', textinfo='percent', hole=0.4)])

    # Visualizzazione del grafico su Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Explicitly close the connection
    conn.close()
