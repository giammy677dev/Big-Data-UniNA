from utils import st, pd, conn, WordCloud, plt
import nltk
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
import plotly.graph_objects as go
import streamlit as st


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

# Creazione del grafico temporale
fig = go.Figure(data=go.Scatter(x=date_results, y=followers_results, mode='lines'))

# Personalizzazione del grafico
fig.update_layout(
    title='Andamento dei followers nel tempo',
    xaxis_title='Data',
    yaxis_title='Followers'
)

# Visualizzazione del grafico su Streamlit
st.plotly_chart(fig)

st.write("aaa")

# Explicitly close the connection
conn.close()