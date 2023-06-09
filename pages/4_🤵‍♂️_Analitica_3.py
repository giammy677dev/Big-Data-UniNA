from utils import st, pd, conn, WordCloud, plt, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
import nltk
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
import plotly.graph_objects as go
import streamlit as st
import seaborn as sns
import calendar
from scipy.special import softmax
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Analitica 3 - Gli Opinion Leader",
    page_icon="👨‍💼",
)

st.title("Analitiche sugli Opinion Leader")

minNumFollower = 50000

st.write(f'''In questa sezione si fanno analitiche sugli Opinion Leader. Per Opinion Leader consideriamo tutti gli 
utenti che presentano un numero di follower pari almeno a {minNumFollower}.''')

#Query per considerare il numero totale di utenti analizzati
query = f"""MATCH (u:Utente)
RETURN count(u)"""
query_results = conn.query(query)
numeroTotaleUtenti = (query_results[0][0])

#Query per considerare il numero totale di utenti analizzati
query = f"""MATCH (m:Messaggio)-[r]-(u:Utente)
WITH u, MAX(m.followers_count) AS valoreMassimo
WHERE toInteger(valoreMassimo)> {minNumFollower}
RETURN count(u)"""
query_results = conn.query(query)
numeroOpinionLeader = (query_results[0][0])

numero_non_opinionLeader = (numeroTotaleUtenti - numeroOpinionLeader)

# Definisci i colori personalizzati
colors = ['#00acee', '#ADD8E6']

# Creazione del grafico ad aerogramma
labels = ['Opinion Leader', 'Non Opinion Leader']
values = [numeroOpinionLeader, numero_non_opinionLeader]

fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])

st.header("Percentuale Opinion Leader")
st.write(f"""Per le analisi effettuate, stiamo considerando un totale di {numeroTotaleUtenti}. Per questi utenti abbiamo un numero di Opinion Leader pari a {numeroOpinionLeader}""")

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig, use_container_width=True)

st.header("Analitiche sull'Opinion Leader scelto")
# Aggiungiamo il filtro per selezionare l'utente da visualizzare
query = f"""MATCH (m:Messaggio)-[r]-(u:Utente)
WITH u, MAX(m.followers_count) AS valoreMassimo
WHERE toInteger(valoreMassimo)> {minNumFollower}
RETURN u.screen_name ORDER BY u.screen_name"""
query_results = conn.query(query)
string_results = [record['u.screen_name'] for record in query_results]
selected_user = st.selectbox('Seleziona l\'Opinion Leader:', string_results)

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
                st.image('twitterVerifiedBadge.png', width=25)
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
                description_results[0] == '' else f'<p style="color: white;"><b style="color: #00acee;">Descrizione:</b> {description_results[0]}</p>',
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

st.write("--------------------")

# GRAFICI TEMPORALI
st.write("**Grafici Temporali**")
# Prendiamo i dati utili (tempo e valore) per i grafici
query = f"""MATCH (u:Utente)-[r]-(m:Messaggio)
            WHERE u.screen_name= "{selected_user}" AND toInteger(m.followers_count) > {int(followers_results[0]) * 0.01}
            RETURN m.date, m.followers_count, m.favourites_count
            ORDER BY m.date
        """
query_results = conn.query(query)
date_results = [datetime.strptime(record['m.date'], '%Y-%m-%d %H:%M:%S+00:00') for record in query_results]
followers_results = [int(record['m.followers_count']) for record in query_results]
favourites_results = [int(record['m.favourites_count']) for record in query_results]

# Selezione data inizio e data fine su due colonne
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('Seleziona la data di inizio:', value=date_results[0].date())
with col2:
    end_date = st.date_input('Seleziona la data di fine:', value=date_results[-1].date())

# Filtra i dati in base al range di date selezionato
filtered_date_results = []
filtered_followers_results = []
filtered_favourites_results = []

for date, followers, favourites in zip(date_results, followers_results, favourites_results):
    if start_date <= date.date() <= end_date:
        filtered_date_results.append(date)
        filtered_followers_results.append(followers)
        filtered_favourites_results.append(favourites)


# Creazione del grafico temporale 1
fig1 = go.Figure(data=go.Scatter(x=filtered_date_results, y=filtered_followers_results, mode='lines'))

# Personalizzazione del grafico 1
fig1.update_layout(
    title='Andamento dei followers nel tempo',
    xaxis_title='Data',
    yaxis_title='Followers'
)

# Creazione del grafico temporale 2
fig2 = go.Figure(data=go.Scatter(x=filtered_date_results, y=filtered_favourites_results, mode='lines'))

# Personalizzazione del grafico 2
fig2.update_layout(
    title='Andamento dei likes nel tempo',
    xaxis_title='Data',
    yaxis_title='Likes'
)

st.plotly_chart(fig1)

st.plotly_chart(fig2)

st.write("--------------------")

#GRAFICO ISTOGRAMMA ATTIVITA' MENSILE
st.write("**Attività mensile dell'utente**")
# Prendiamo i dati utili (tempo e valore) per l'istogramma a barre verticali
query = f"""MATCH (u:Utente)-[r]-(m:Messaggio)
WHERE u.screen_name = "{selected_user}"
WITH m, substring(m.date, 5, 2) AS month, substring(m.date, 0, 4) AS year
RETURN year, month, count(m) AS messageCount
ORDER BY year, month"""

query_results = conn.query(query)
month_results = [f"{record['year']}-{record['month']}" for record in query_results]
count_result = [record['messageCount'] for record in query_results]

# Ottenere i nomi dei mesi e degli anni corrispondenti ai numeri
month_names = [f"{calendar.month_name[int(month.split('-')[1])]} {month.split('-')[0]}" for month in month_results]

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

# Converti i nomi completi dei mesi nelle forme abbreviate
month_names = [month_abbreviations.get(month.split(' ')[0], month.split(' ')[0]) + ' ' + month.split(' ')[1] for month in month_names]

# Imposta lo stile di seaborn senza griglia
sns.set_style("dark", {"axes.facecolor": "none", "axes.grid": False})

# Creazione dell'istogramma
fig, ax = plt.subplots(facecolor='none')
bars = ax.bar(month_names, count_result, width=0.6)

# Imposta il colore del testo delle etichette delle barre come bianco
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), bar.get_height(), ha='center', va='bottom', color='white')

# Imposta il colore del testo delle etichette degli assi e riduci la dimensione del carattere
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.xaxis.label.set_fontsize(8)
ax.yaxis.label.set_fontsize(8)

# Imposta il colore delle linee degli assi come bianco
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')

# Nascondi le linee degli assi
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Nascondi i ticks degli assi
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')

# Imposta la dimensione del carattere per i valori vicino agli assi
ax.xaxis.set_tick_params(labelsize=7)
ax.yaxis.set_tick_params(labelsize=7)

# Aggiungi etichette sull'asse x e sull'asse y
ax.set_xlabel('Mese e Anno', color='white')
ax.set_ylabel('Conteggio attività', color='white')

# Mostra il grafico su Streamlit
st.pyplot(fig)

st.header(f"Analitiche sui Tweet di '{selected_user}'")

#RANKING TWEET
st.write(f"**Ranking dei Tweet rilevanti**")
st.write("Per identificare i tweet più rilevanti per questo ranking, si fa riferimento ai tweet col maggior numero di interazioni, considerando numero di retweet, numero di quoted tweet e numero di risposte associati, per ogni tweet.")

# Inserisci il numero di tweet da considerare per il ranking
n_ranking = st.slider("Seleziona il numero di tweet per il ranking", 1, 10, 3)

# Prendiamo i dati utili per il ranking
query = f"""MATCH (u:Utente)-[r1]-(m:Messaggio)<-[r2]-(m1:Messaggio)
            WHERE u.screen_name = "{selected_user}"
            RETURN m.tweetid, m.text, m.topic, count(m) as conteggio
            ORDER BY count(m) DESC
            LIMIT {n_ranking}"""

query_results = conn.query(query)
ranking_data = [(i+1, record['m.tweetid'], record['m.text'], record['m.topic'], record['conteggio']) for i, record in enumerate(query_results)]

# Creiamo un DataFrame pandas con i dati
df = pd.DataFrame(ranking_data, columns=['Posizione', 'ID', 'Testo del tweet', 'Topic trattato', 'Conteggio interazioni'])

# Rimuoviamo la colonna degli indici
df.set_index('Posizione', inplace=True)

# Nascondiamo la colonna dell'ID nella tabella
df_display = df.drop(columns=['ID'])

# Mostra la tabella
st.header(f"Top {n_ranking} tweets")
st.table(df_display)

st.header("Sentiment Analysis")

# Seleziona un tweet dal ranking
selected_text = st.selectbox(f"**Seleziona uno dei tweet della top {n_ranking}:**", df['Testo del tweet'])
# Ottieni l'ID del tweet selezionato
selected_tweet = df[df['Testo del tweet'] == selected_text]['ID'].values[0]


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


sentiment = perform_sentiment_analysis(selected_text)

# Definizione dei range di valore e dei corrispondenti testi e colori
ranges = [(-1, -0.7, 'Estremamente negativo', '#D10000'),
          (-0.7, -0.4, 'Negativo', '#FF0000'),
          (-0.4, -0.2, 'Leggermente Negativo', '#FF4242'),
          (-0.2, 0.2, 'Neutro', 'lightgray'),
          (0.2, 0.4, 'Leggermente Positivo', 'lightgreen'),
          (0.4, 0.7, 'Positivo', 'mediumseagreen'),
          (0.7, 1, 'Estremamente positivo', 'green')]

# Trova il testo e il colore corrispondenti al valore del sentiment
text = ''
color = ''
for range_ in ranges:
    if range_[0] <= sentiment < range_[1]:
        text = range_[2]
        color = range_[3]
        break

st.write("----------------------------------------")
st.write("**Sentiment Analysis sul tweet selezionato**")

# Creazione del layout a tre colonne
col1, col2, col3 = st.columns([5, 1, 1])

# Colonna 1: Testo descrittivo
with col1:
    st.write(f"Il sentiment rilevato per questo tweet è: {text}")

# Colonna 2: Valore numerico con colore
with col2:
    rounded_sentiment = round(sentiment, 3)
    st.write(rounded_sentiment)

# Colonna 3: Grafico
with col3:
    fig, ax = plt.subplots(figsize=(4, 1))
    ax.barh(0, sentiment, color=color, height=0.5)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    ax.axvline(x=0, color='white', linestyle='-')
    fig.patch.set_facecolor('None')
    ax.set_facecolor('None')
    plt.box(False)
    st.pyplot(fig)

st.write("--------------------------------------------------------")
st.write("**Sentiment Analysis e analitiche dei tweet che interagiscono col tweet selezionato**")
# Recupero i testi dei tweet che hanno risposto o citato (senza retweet) questo tweet per una sentiment analysis 'media'
sentiment_list = []
query = f"""MATCH (u:Utente)-[r1]-(m1:Messaggio)<-[r2:ha_citato|ha_risposto]-(m2:Messaggio)
            WHERE u.screen_name = "{selected_user}" AND m1.tweetid = "{selected_tweet}"
            RETURN m2.text
            """
query_results = conn.query(query)
text_result = [record['m2.text'] for record in query_results]

for text in text_result:
    sentiment_values = perform_sentiment_analysis(text)
    sentiment_list.append(sentiment_values)

# Creazione del layout a tre colonne
col1, col2, col3 = st.columns([5, 1, 1])
i=1
# Iterazione attraverso la lista dei valori sentiment
for sentiment in sentiment_list:
    # Trova il testo e il colore corrispondenti al valore del sentiment
    text = ''
    color = ''
    for range_ in ranges:
        if range_[0] <= sentiment < range_[1]:
            text = range_[2]
            color = range_[3]
            break

    # Colonna 1: Testo descrittivo
    with col1:
        st.write(f"Il sentiment rilevato per il tweet {i} è: {text}")

    # Colonna 2: Valore numerico con colore
    with col2:
        rounded_sentiment = round(sentiment, 3)
        st.write(rounded_sentiment)

    # Colonna 3: Grafico
    with col3:
        fig, ax = plt.subplots(figsize=(4, 1))
        ax.barh(0, sentiment, color=color, height=0.5)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')
        ax.axvline(x=0, color='white', linestyle='-')
        fig.patch.set_facecolor('None')
        ax.set_facecolor('None')
        plt.box(False)
        st.pyplot(fig)
    i += 1

st.write("------------------------------------------------------")
# Selettore del tweet nella sidebar
selected_tweet_index = st.selectbox("Seleziona un tweet per visualizzarne il testo:", range(1, len(text_result) + 1),
                                            format_func=lambda i: f'Tweet {i}')
st.write(text_result[selected_tweet_index - 1])

st.write("------------------------------------------------------")
# Calcolo delle percentuali dei sentiment
sentiment_counts = np.zeros(len(ranges))
for sentiment in sentiment_list:
    for i, range_ in enumerate(ranges):
        if range_[0] <= sentiment < range_[1]:
            sentiment_counts[i] += 1
            break
total_tweets = len(sentiment_list)
sentiment_percentages = sentiment_counts / total_tweets

# Aerogramma delle percentuali dei sentiment
labels = [range_[2] for range_ in ranges]
colors = [range_[3] for range_ in ranges]
explode = [0.1] + [0] * (len(ranges) - 1)  # Esplosione della prima fetta

fig = go.Figure(data=[go.Pie(labels=labels, values=sentiment_percentages, marker=dict(colors=colors),
                             hoverinfo='label+percent', textinfo='percent', hole=0.4)])

st.write("**Percentuale Opinion Leader**")
st.write(f"""Le percentuali sono calcolate in riferimento al numero totale pari a {len(sentiment_list)}.""")

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig, use_container_width=True)

# Explicitly close the connection
conn.close()
