from utils import st, conn, pd
#DA METTERE SE FUNZIONA
import bar_chart_race as bcr
from itertools import groupby

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
query = f"MATCH (m:Messaggio) WHERE m.topic CONTAINS '{selected_topic}' RETURN m.text, LEFT(m.date, 10) AS data ORDER BY data"
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

# SERVE QUI LA SENTIMENT ED IL GRAFICO

col1, col2 = st.columns([1, 1])
with col1:
    # Creazione del box di testo
    text = st.text_area("Inserisci il testo qui", value="", height=10)
    text = text.lower()
    # Bottone per salvare il testo
    if st.button("Ricerca"):
        # Aggiungiamo il filtro per selezionare i topic da visualizzare
        query = f"MATCH (m:Messaggio) WHERE toLower(m.text) CONTAINS '{text}' RETURN REDUCE(s = '', x IN COLLECT(m.text) | s + ' ' + x) AS combined_text"
        query_results = conn.query(query)
        text_results = [record['combined_text'] for record in query_results]
        st.write(text_results)



