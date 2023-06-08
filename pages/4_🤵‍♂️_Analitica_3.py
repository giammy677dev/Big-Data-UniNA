from utils import st, pd, conn, WordCloud, plt
import nltk
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
import plotly.graph_objects as go
import streamlit as st
import seaborn as sns
import calendar

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title("Analitiche sugli 'influencer'")

minNumFollower = 50000

st.write(f'''In questa sezione si fanno analitiche sugli influencer. Per 'influencer' consideriamo tutti gli 
utenti che presentano un numero di follower pari almeno a {minNumFollower}''')

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
numeroInfluencer = (query_results[0][0])

numero_non_influencer = (numeroTotaleUtenti - numeroInfluencer)

# Definisci i colori personalizzati
colors = ['#00acee', '#ADD8E6']

# Creazione del grafico ad aerogramma
labels = ['Influencer', 'Non Influencer']
values = [numeroInfluencer, numero_non_influencer]

fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])

st.header("Percentuale Influencer")
st.write(f"""Per le analisi effettuate, stiamo considerando un totale di {numeroTotaleUtenti}. Per questi utenti abbiamo un numero di Influencer pari a {numeroInfluencer} e un numero di non Influencer pari a {numero_non_influencer}""")

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig, use_container_width=True)

st.header("Analitiche sull'Influencer scelto")
# Aggiungiamo il filtro per selezionare l'utente da visualizzare
query = f"""MATCH (m:Messaggio)-[r]-(u:Utente)
WITH u, MAX(m.followers_count) AS valoreMassimo
WHERE toInteger(valoreMassimo)> {minNumFollower}
RETURN u.screen_name ORDER BY u.screen_name"""
query_results = conn.query(query)
string_results = [record['u.screen_name'] for record in query_results]
selected_user = st.selectbox('Seleziona l\'influencer:', string_results)

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

#GRAFICI TEMPORALI

# Prendiamo i dati utili (tempo e valore) per i grafici
query = f"""MATCH (u:Utente)-[r]-(m:Messaggio)
WHERE u.screen_name= "{selected_user}"
RETURN m.date, m.followers_count, m.favourites_count
ORDER BY m.date"""

query_results = conn.query(query)
date_results = [record['m.date'] for record in query_results]
followers_results = [int(record['m.followers_count']) for record in query_results]
favourites_results = [int(record['m.favourites_count']) for record in query_results]

# Creazione del grafico temporale 1
fig = go.Figure(data=go.Scatter(x=date_results, y=followers_results, mode='lines'))

# Personalizzazione del grafico
fig.update_layout(
    title='Andamento dei followers nel tempo',
    xaxis_title='Data',
    yaxis_title='Followers'
)

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig)

# Creazione del grafico temporale 2
fig = go.Figure(data=go.Scatter(x=date_results, y=favourites_results, mode='lines'))

# Personalizzazione del grafico
fig.update_layout(
    title='Andamento dei likes nel tempo',
    xaxis_title='Data',
    yaxis_title='Likes'
)

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig)


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
            RETURN m.tweetid, m.text, count(m)
            ORDER BY count(m) DESC
            LIMIT {n_ranking}"""

query_results = conn.query(query)
ranking_data = [(i+1, record['m.tweetid'], record['m.text'], record['count(m)']) for i, record in enumerate(query_results)]

# Creiamo un DataFrame pandas con i dati
df = pd.DataFrame(ranking_data, columns=['Posizione', 'ID', 'Testo', 'Conteggio'])

# Rimuoviamo la colonna degli indici
df.set_index('Posizione', inplace=True)

# Nascondiamo la colonna dell'ID nella tabella
df_display = df.drop(columns=['ID'])

# Mostra la tabella
st.header(f"Top {n_ranking} tweets")
st.table(df_display)

# Seleziona un tweet dal ranking
selected_text = st.selectbox("**Seleziona un tweet**", df['Testo'])
# Ottieni l'ID del tweet selezionato
selected_tweet = df[df['Testo'] == selected_text]['ID'].values[0]

#SPAZIO PER SENTIMENT ANALYSIS


#Recupero i testi dei tweet che hanno risposto o citato (senza retweet) questo tweet per una sentiment analysis 'media'
query = f"""MATCH (u:Utente)-[r1]-(m1:Messaggio)<-[r2:ha_citato|ha_risposto]-(m2:Messaggio)
            WHERE u.screen_name = "{selected_user}" AND m1.tweetid = "{selected_tweet}"
            RETURN m2.text
            """

# Explicitly close the connection
conn.close()