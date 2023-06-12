import streamlit as st
from utils import elenco_bullet

st.set_page_config(
    page_title="Documentazione",
    page_icon="🗒"
)

st.image("utility/LogoUniRemakeWhite.png")

st.markdown("<h3 style='text-align: center;'>Documentazione del progetto<br>di Big Data Engineering</h3>", unsafe_allow_html=True)

st.markdown("<h6 style='text-align: center;'>Anno 2022/2023</h6>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Social Network Analysis<br>Summarization<br><br></h1>", unsafe_allow_html=True)

st.write("Orlando Gian Marco M63/001326")
st.write("Perillo Marco M63/001313")
st.write("Russo Diego M63/001335")

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("**Traccia**"):
    st.write("*Social media platforms play a significant role in shaping the modern digital "
             "information ecosystem by allowing users to contribute to discussions on a wide "
             "range of topics. However, the freedom of expression offered by these platforms "
             "can potentially threaten the integrity of these information ecosystems when "
             "harmful content (e.g., fake news, hateful speech) is shared and propagates across "
             "the digital population. "
             "To overcome this problem, mainstream social media platforms (e.g., Facebook "
             "and Twitter) deploy diverse moderation interventions to target both inappropriate "
             "content and the users responsible for spreading it. However, these "
             "moderation efforts are typically enacted in a siloed fashion, largely overlooking "
             "other platforms’ interventions on harmful content that has migrated to their "
             "spaces. This approach poses risks as any harmful content originating on "
             "a source platform can migrate to other target platforms, gaining traction with "
             "specific communities and reaching a wider audience. "
             "The aim of this challenge is to characterize users sharing (moderated) YouTube "
             "content on Twitter, hereafter (moderated) YouTube mobilizers, during US 2020 "
             "presidential election. In particular, we will provide a dataset containing all "
             "tweets posted by (moderated) Youtube mobilizers as well as all tweets, posted "
             "by the general Twitter audience, which engage with (moderated) Youtube mobilizers. "
             "The objective is to generate a comprehensive report that summarizes a user "
             "interest. The final report should characterize the user across several dimensions, "
             "including his interests, his (political) preference, the topics he engages with, and "
             "the sentiment and the emotions expressed through his tweets. Furthermore, the "
             "analyses should unveil the characteristics of the YouTube cross-posting behavior "
             " (e.g., whether the user supports the ideas promoted in the videos he shares, "
             "whether he is only an advertiser of those videos). Finally, investigations regarding "
             "the sharing of moderated vs non-moderated YouTube videos are welcome "
             "(e.g., what kind of users share moderated videos, can we understand whether a "
             "video will be moderated on YouTube based on its Twitter user base).*")

with st.expander("**Architettura del progetto e tecnologie utilizzate**"):
    st.write("""Al fine di poter realizzare le analitiche riportate in questa dashboard, abbiamo innanzitutto deciso di
                utilizzare un database a grafo per poter descrivere al meglio le relazioni che intercorrono tra i dati a
                nostra disposizione. Un database a grafo, infatti, risulta essere la soluzione ottimale proprio nel caso
                in cui il dominio che si sta trattando è quello del social networking. Nel nostro caso, infatti, il database
                a grafo ci ha permesso di individuare in modo piuttosto intuitivo (anche visivamente) le relazioni che
                intercorrono tra i tweet pubblicati dagli utenti, le relative risposte, ricondivisioni e così via. In
                particolare, il database a grafo da noi scelto è stato Neo4j e, per poter lavorare parallelamente al progetto,
                abbiamo deciso di utilizzare il servizio AuraDB messo a disposizione da Neo4j stesso. Tale tecnologia permette
                di avere a disposizione un server remoto su cui caricare il proprio database a grafo. In questo modo, dunque,
                il database è sempre accessibile ed è possibile accedervi e lavorarci direttamente dall'applicazione di
                Neo4j Desktop come se il database fosse disponibile in locale.
                Per quanto riguarda lo sviluppo del codice, invece, il linguaggio di programmazione utilizzato è stato Python.
                Abbiamo effettuato lo staging del codice su GitHub in modo da sfruttare tutti i vantaggi di un sistema di
                version control.
                Tra le librerie più importanti utilizzate per la realizzazione del progetto ricordiamo:
                """)
    elenco_bullet("OpenAI", "tale libreria, tramite l'utilizzo di apposite API, consente di avere accesso al chatbot ChatGPT;")
    elenco_bullet("Gensim", """tale libreria è stata utilizzata per poter addestrare l'algoritmo Latent Dirichlet Allocation
                            (LDA). Tale algoritmo è di tipo non supervisionato ed effettua topic detection. Abbiamo deciso
                            di utilizzare tale algoritmo e non un modello pre-addestrato in quanto un modello pre-addestrato
                            non avrebbe potuto ottenere prestazioni soddisfacenti con tweet molto specifici come quelli
                            a nostra disposizione;""")
    elenco_bullet("HuggingFace", """tale libreria è stata utilizzata per effettuare la sentiment analysis sui tweet condivisi"
                                 dagli utenti;""")
    elenco_bullet("Streamlit", "tale libreria ha semplificato la realizzazione della dashboard stessa.")
    st.write("""L'IDE utilizzato è PyCharm, il quale permette una semplice installazione e gestione di tutte le librerie
                utilizzate.
                """)
    st.image("utility/ImgDocumentazioneProgettoFinale.png")

with st.expander("**Presentazione del dataset e Pre-processing**"):
    st.write("""
           Il dataset su cui sono state realizzate le analitiche raccolgono una serie di tweet riguardanti le elezioni presidenziali americane del 2020. 
           Tale dataset è stato lavorato andando a rimuovere i campi che non fornivano alcun contributo informativo (colonne costituite da tutti valori uguali, colonne costituite da molti valori nulli e così via).
           Il dataset su cui abbiamo realizzato le analitiche risulta essere caratterizzato dai seguenti campi:
             """)
    elenco_bullet("tweetid", "ID del tweet;")
    elenco_bullet("userid", "ID dell'utente che ha pubblicato il tweet;")
    elenco_bullet("screen_name", "nickname dell'utente che ha pubblicato il tweet;")
    elenco_bullet("date", "data e ora in cui è stato pubblicato il tweet;")
    elenco_bullet("lang", "lingua del tweet;")
    elenco_bullet("description", "biografia dell'utente che ha pubblicato il tweet;")
    elenco_bullet("text", "testo del tweet;")
    elenco_bullet("reply_userid", "ID dell'utente del tweet a cui si sta rispondendo;")
    elenco_bullet("reply_screen_name", "nickname dell'utente del tweet a cui si sta rispondendo;")
    elenco_bullet("reply_statusid", "ID del tweet a cui si sta rispondendo;")
    elenco_bullet("tweet_type", "tipologia di tweet (ad esempio originale, retweet, citazione o risposta);")
    elenco_bullet("friends_count", "numero di utenti seguiti dall'utente;")
    elenco_bullet("followers_count", "numero di follower dell'utente;")
    elenco_bullet("favourites_count", "numero di like dell'utente;")
    elenco_bullet("statuses_count", "numero totale di tweet pubblicati dall'utente;")
    elenco_bullet("verified", "definisce se l'account dell'utente è verificato su Twitter;")
    elenco_bullet("hashtag", "hashtag presenti nel tweet;")
    elenco_bullet("urls_list", "URL presenti nel tweet;")
    elenco_bullet("display_name", "nome dell'utente;")
    elenco_bullet("rt_urls_list", "URL presenti nel messaggio che è stato ritwittato;")
    elenco_bullet("mentionid", "ID degli utenti menzionati nel tweet;")
    elenco_bullet("mentionsn", "nickname degli utenti menzionati nel tweet;")
    elenco_bullet("rt_screen", "nickname dell'utente del messaggio che è stato ritwittato;")
    elenco_bullet("rt_userid", "ID dell'utente del messaggio che è stato ritwittato;")
    elenco_bullet("rt_user_description", "biografia dell'utente del messaggio che è stato ritwittato;")
    elenco_bullet("rt_text", "testo del messaggio che è stato ritwittato;")
    elenco_bullet("rt_hashtag", "hashtag presenti nel messaggio che è stato ritwittato;")
    elenco_bullet("rt_qtd_count", "numero di volte in cui il messaggio ritwittato è stato citato;")
    elenco_bullet("rt_rt_count", "numero di volte in cui il messaggio ritwittato è stato ritwittato;")
    elenco_bullet("rt_reply_count", "numero di risposte ricevute dal messaggio che è stato ritwittato;")
    elenco_bullet("rt_fav_count", "numero di volte in cui il messaggio che è stato è stato aggiunto ai preferiti;")
    elenco_bullet("rt_tweetid", "ID del messaggio che è stato ritwittato;")
    elenco_bullet("qtd_screen", "nickname dell'utente del messaggio che è stato citato;")
    elenco_bullet("qtd_userid", "ID dell'utente del messaggio che è stato citato;")
    elenco_bullet("qtd_user_description", "biografia dell'utente del messaggio che è stato citato;")
    elenco_bullet("qtd_text", "testo del messaggio che è stato citato;")
    elenco_bullet("qtd_hashtag", "hashtag presenti nel messaggio che è stato citato;")
    elenco_bullet("qtd_qtd_count", "numero di volte in cui il messaggio citato è stato citato;")
    elenco_bullet("qtd_rt_count", "numero di volte in cui il messaggio citato è stata ritwittato;")
    elenco_bullet("qtd_reply_count", "numero di risposte ricevute dal messaggio citato;")
    elenco_bullet("qtd_fav_count", "numero di volte in cui il messaggio citato è stata aggiunto ai preferiti;")
    elenco_bullet("qtd_tweetid", "ID del tweet che è stato citato;")
    elenco_bullet("qtd_urls_list", "URL presenti nel messaggio citato;")
    elenco_bullet("media_urls", "URL multimediali presenti nel tweet;")
    elenco_bullet("rt_media_urls", "URL multimediali presenti nel messaggio ritwittato;")
    elenco_bullet("q_media_urls", "URL multimediali presenti nel messaggio citato;")
    elenco_bullet("cat", "definisce se l'utente ha condiviso su Twitter dei video che sono stati moderati da Youtube.")
