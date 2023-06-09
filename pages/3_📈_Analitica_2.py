from utils import st, conn, pd, WordCloud, plt, openai, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from scipy.special import softmax
import plotly.express as px
from math import floor

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title('Analitiche sui Topic')

st.write('''In questa sezione si fanno analitiche sui topic''')

# Layout a due colonne
col1, col2 = st.columns([1, 2])
with col1:
    # Aggiungiamo il filtro per selezionare i topic da visualizzare
    query = """MATCH (m:Messaggio)
               WITH m, SPLIT(m.topic, ';') AS topics
               UNWIND topics AS topic
               RETURN DISTINCT topic"""
    query_results = conn.query(query)
    string_results = [record['topic'] for record in query_results]
    selected_topic = st.selectbox('Seleziona il topic:', string_results)

with col2:
    # Andiamo a selezionare i il filtro per selezionare i topic da visualizzare
    query = """MATCH (m:Messaggio)
               WITH m, SPLIT(m.topic, ';') AS topics
               UNWIND topics AS topic
               RETURN topic, m.date
               ORDER BY m.date;"""
    query_results = conn.query(query)
    topic_results = [(record['topic'], record['m.date']) for record in query_results]

    # Creazione del DataFrame pandas con i dati
    df = pd.DataFrame(topic_results, columns=['topic', 'date'])

    # Conversione del campo "date" in formato datetime
    df['date'] = pd.to_datetime(df['date'])

    # Conteggio delle occorrenze per ogni data e categoria di topic
    count_by_date_topic = df.groupby([df['date'].dt.date, 'topic']).size().unstack(fill_value=0)

    # Calcolo della somma cumulativa dei valori per ogni data
    cumulative_count = count_by_date_topic.cumsum()
    st.write(cumulative_count)

    # Creazione del grafico di tipo "bar chart race" con bar_chart_race
    #fig = bcr.bar_chart_race(cumulative_count)

    # Rendering del grafico in Streamlit
    #st.pyplot(fig)

    # Visualizzazione del conteggio per ogni data e categoria di topic
    #st.write(count_by_date_topic)

# Andiamo a prendere i testi che contengono il topic selezionato nel campo topic
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

# Sentiment analysis
# Carichiamo il tokenizer ed il modello pre-addestrato di sentiment analysis
MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


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


sentiment_values = []
month_list = list(monthly_texts.keys())

for month in month_list:
    text_month = monthly_texts[month]
    sentiment = perform_sentiment_analysis(text_month)
    sentiment_values.append(sentiment)

fig = px.line(x=month_list, y=sentiment_values, markers = False)

#PARTE NUOVA
col1, col2 = st.columns([3, 1])
with col1:
    fig.update_layout(
        title='Sentiment Mensile',
        xaxis_title='Mesi',
        yaxis_title='Sentiment',
        yaxis_range=[-1, 1]
    )

    # Visualizzazione del grafico
    st.plotly_chart(fig)
with col2:
    #Andiamo a selezionare per ogni utente i testi inerenti al topic selezionato
    query = f"""MATCH (u:Utente)-[a:ha_twittato]->(m:Messaggio)
                WHERE m.topic = '{selected_topic}'
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

    labels = ['Positivi', 'Neutrali', 'Negativi']
    values = [len(positive), len(neutral), len(negative)]

    fig = px.pie(values=values, names=labels)

    st.plotly_chart(fig)
    #FINE PARTE NUOVA


batch_size = 5000
#Se il testo supera il limite di token previsto da chatGPT, dividilo in batch
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
    st.write(batches)
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
@st.cache_data
def type_string_GPT_style(string):
    text_placeholder = st.empty()
    for i in range(1, len(string) + 1):
        typed_text = string[:i]
        text_placeholder.markdown(typed_text)
        time.sleep(0.02)


# Creazione del box di testo
user_text = st.text_area("Inserisci il testo qui", value="", height=10)
user_text = user_text.lower()
# Bottone per salvare il testo
if st.button("Ricerca"):
    # Aggiungiamo il filtro per selezionare i topic da visualizzare
    query = f"""MATCH (m:Messaggio) WHERE toLower(m.text) CONTAINS '{user_text}'
                RETURN REDUCE(s = '', x IN COLLECT(m.text) | s + ' ' + x) AS combined_text"""
    query_results = conn.query(query)
    text_results = [record['combined_text'] for record in query_results]
    response_text = chatGPT_script_for_text(text_results)
    type_string_GPT_style(response_text)






