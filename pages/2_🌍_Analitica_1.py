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
col1, col2 = st.columns(2)

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
        <div style="background-color: #FFA559; padding: 15px; border-radius: 5px; width: 60%;">
            <br><br><br><br>
            {}
            {}
            {}
            {}
            {}
        </div>
        '''.format(
            f'<p style="color: white;">⚠️ L\'utente {selected_user} non ha una descrizione</p>' if
            description_results[0] == '' else f'<p style="color: white;"> {description_results[0]}</p>',
            f'<p style="color: white;">Followers: {followers_results[0]}</p>',
            f'<p style="color: white;">Following: {friends_results[0]}</p>',
            f'<p style="color: white;">Numero di tweet: {statuses_results[0]}</p>',
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
            f'<br><br><br><br><div style="background-color: #FFA559; padding: 15px; border-radius: 5px;width: 60%;">'
            f'<p style="color: white;">:warning: L\'utente {selected_user} è stato moderato su YouTube. Giudicando i suoi contenuti su Twitter, l\'indice di pericolosità è tot</p>' # INDICARE INDICE
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<br><br><br><br><div style="background-color: #FFA559; padding: 15px; border-radius: 5px;width: 60%;">'
            f'<p style="color: white;"> L\'utente {selected_user} non è stato moderato su YouTube. Giudicando i suoi contenuti su Twitter, l\'indice di pericolosità è tot</p>'  # INDICARE INDICE
            f'</div>',
            unsafe_allow_html=True
        )

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
