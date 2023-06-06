from utils import conn
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=12)

query = f"""MATCH (u:Utente)-[:ha_twittato]->(m:Messaggio)
            WHERE m.topic <> ''
            RETURN m.text, m.tweetid
        """
query_results = conn.query(query)
tweets_results = [{"text": record["m.text"], "tweetid": record["m.tweetid"]} for record in query_results]

i=0
for tweet in tweets_results:
    i += 1
    print(i)
    # Tokenizzazione del testo
    inputs = tokenizer(tweet["text"], return_tensors='pt')

    # Esecuzione del modello
    outputs = model(**inputs)

    # Estrazione delle probabilità dei topic
    probs = torch.softmax(outputs.logits, dim=-1)

    # Individuazione del topic con la probabilità più alta
    topic_idx = torch.argmax(probs).item()

    # Mappatura degli indici dei topic ai nomi dei topic (da personalizzare in base ai topic desiderati)
    topic_mapping = {
        0: 'Politics',
        1: 'Justice',
        2: 'Pandemy',
        3: 'Actuality',
        4: 'Society',
        5: 'Technology',
        6: 'Music',
        7: 'Education',
        8: 'Environment',
        9: 'Social Media',
        10: 'Economy',
        11: 'Health'
    }

    topic = topic_mapping[topic_idx]

    query = f"""MATCH (m:Messaggio)
                WHERE m.tweetid = '{tweet["tweetid"]}'
                SET m.topic = '{topic}'
            """
    query_results = conn.query(query)
