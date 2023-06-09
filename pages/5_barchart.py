import pandas as pd
from utils import st, conn

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
df['date'] = pd.to_datetime(df['date']).dt.date

# Conteggio delle occorrenze per ogni data e categoria di topic
count_by_date_topic = df.groupby(['date', 'topic']).size().unstack(fill_value=0)

# Calcolo della somma cumulativa dei valori per ogni data
cumulative_count = count_by_date_topic.cumsum()

# Salvataggio del dataframe in un file CSV senza l'indice
cumulative_count.to_csv('C:/Users/ogiam/Desktop/df.csv')

# Percorso del video all'interno del progetto
video_path = "bcr.mp4"

# Apertura del video come oggetto binario
with open(video_path, "rb") as video_file:
    video_bytes = video_file.read()

# Embedding del video all'interno di un box
st.video(video_bytes)
