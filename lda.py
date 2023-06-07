from utils import conn
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS

query = """MATCH (m:Messaggio)
            RETURN m.text, m.tweetid
        """

# Esecuzione della query Cypher
query_results = conn.query(query)

# Estrazione dei dati dalla query
text_results = [record['m.text'].lower() for record in query_results]
data = [(record["m.text"].lower(), record["m.tweetid"]) for record in query_results]

custom_stopwords = set(STOPWORDS) #Stopwords di gensim
custom_stopwords.update(['rt', '', '&amp;', '|', 'it\'s']) #Aggiungiamo stopwords personalizzate
custom_stopwords = list(custom_stopwords)

# Rimozione delle stop word dai token
nltk_stop_words = list(stopwords.words('english'))

full_stop_words = custom_stopwords + nltk_stop_words

tweet_tokens = [[token for token in tweet.split() if token not in full_stop_words] for tweet in text_results]

# Creazione del dizionario dei token
dictionary = Dictionary(tweet_tokens)

# Rimozione dei token meno frequenti e più comuni
dictionary.filter_extremes(no_below=3, no_above=0.5)

# Esclusione dei token composti da un solo carattere
single_char_tokens = [token for token in dictionary.token2id.keys() if len(token) == 1]
dictionary.filter_tokens(bad_ids=[dictionary.token2id[token] for token in single_char_tokens])

# Creazione del corpus
corpus = [dictionary.doc2bow(tokens) for tokens in tweet_tokens]

# Definizione del numero di topic desiderati
num_topics = 5

# Addestramento del modello LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)

# Inferenza dei topic per ogni tweet
topics = lda_model.get_document_topics(corpus)

for topic_id in range(num_topics):
    print(f"Topic {topic_id}:")
    words = lda_model.show_topic(topic_id, topn=10)  # Modifica il valore di 'topn' se desideri più o meno parole chiave per ogni topic
    topic_words = [word for word, _ in words]
    print(topic_words)
    print()

# Memorizzazione dei topic e delle probabilità che soddisfano le condizioni richieste
for i, tweet_topics in enumerate(topics):
    print(i)
    # Ordinamento dei topic in base alla probabilità
    sorted_topics = sorted(tweet_topics, key=lambda x: x[1], reverse=True)
    if sorted_topics[0][1] > 0.7:
        topic_dict = {
            "Topic": sorted_topics[0][0],
            "Probability": sorted_topics[0][1],
            "TweetID": data[i][1]
        }
        query = f"""MATCH (m:Messaggio)
                    WHERE m.tweetid = '{topic_dict["TweetID"]}'
                    SET m.topic = '{topic_dict["Topic"]}'
                """
    else:
        first_topic_dict = {
            "Topic": sorted_topics[0][0],
            "Probability": sorted_topics[0][1],
            "TweetID": data[i][1]
        }
        second_topic_dict = {
            "Topic": sorted_topics[1][0],
            "Probability": sorted_topics[1][1],
            "TweetID": data[i][1]
        }
        query = f"""MATCH (m:Messaggio)
                    WHERE m.tweetid = '{first_topic_dict["TweetID"]}'
                    SET m.topic = '{first_topic_dict["Topic"]};{second_topic_dict["Topic"]}'
                """
    query_results = conn.query(query)

# Chiusura della connessione al database Neo4j
conn.close()
