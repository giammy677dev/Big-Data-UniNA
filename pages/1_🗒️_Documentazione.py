import streamlit as st

st.image("LogoUniRemakeWhite.png")

st.markdown("<h3 style='text-align: center;'>Documentazione del progetto<br>di Big Data Engineering</h3>", unsafe_allow_html=True)

st.markdown("<h6 style='text-align: center;'>Anno 2022/2023</h6>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Social Network Analysis<br>Summarization<br><br></h1>", unsafe_allow_html=True)

st.write("Orlando Gian Marco M63/001326")
st.write("Perillo Marco M63/001313")
st.write("Russo Diego M63/001335")

st.markdown("<br>", unsafe_allow_html=True)


def elenco_bullet(testo_grassetto, testo_normale):
    st.markdown(f"- <span style='color:#FFA559'><b>{testo_grassetto}</b></span>: {testo_normale}",
                unsafe_allow_html=True)


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

with st.expander("**Tecnologie Utilizzate**"):
    st.write("Contenuto della Categoria 1")

with st.expander("**Presentazione del dataset e Preprocessing**"):
    st.write("""
           Il dataset su cui vengono realizzate le analitiche raccoglie una serie di tweet riguardanti le elezioni presidenziali americane del 2020. Tale dataset è stato lavorato andando a rimuovere i campi che non fornivano alcun contributo informativo (colonne costituite da tutti valori uguali, colonne costituite da molti valori nulli e così via).
           Il dataset su cui abbiamo realizzato le analitiche risulta essere caratterizzato dai seguenti campi:
             """)
    elenco_bullet("tweetid", "ID del tweet")
    elenco_bullet("userid", "ID dell'utente che ha pubblicato il tweet")
    elenco_bullet("screen_name", "nickname dell'utente ha pubblicato il tweet")
    elenco_bullet("date", "data e ora in cui è stato pubblicato il tweet")
    elenco_bullet("lang", "lingua del tweet")
    elenco_bullet("description", "biografia dell'utente che ha pubblicato il tweet")
    elenco_bullet("text", "testo del tweet")
    elenco_bullet("reply_userid", "ID dell'utente a cui si sta rispondendo")
    elenco_bullet("reply_screen_name", "nickname dell'utente a cui si sta rispondendo")
    elenco_bullet("reply_statusid", "ID del tweet a cui si sta rispondendo")
    elenco_bullet("tweet_type", "tipologia di tweet (ad esempio originale, retweet, citazione, risposta)")
    elenco_bullet("friends_count", "numero di utenti seguiti dall'utente")
    elenco_bullet("followers_count", "numero di follower dell'utente")
    elenco_bullet("favourites_count", "numero di tweet che l'utente ha aggiunto ai preferiti")
    elenco_bullet("statuses_count", "numero totale di tweet pubblicati dall'utente")
    elenco_bullet("verified", "definisce se l'account dell'utente è verificato o meno")
    elenco_bullet("hashtag", "hashtag presenti nel tweet")
    elenco_bullet("urls_list", "URL presenti nel tweet")
    elenco_bullet("display_name", "nome dell'utente")
    elenco_bullet("rt_urls_list", "URL presenti nel retweet")
    elenco_bullet("mentionid", "ID degli utenti menzionati nel tweet")
    elenco_bullet("mentionsn", "nickname degli utenti menzionati nel tweet")
    elenco_bullet("rt_screen", "nickname dell'utente del messaggio ritwittato")
    elenco_bullet("rt_userid", "ID dell'utente del messaggio ritwittato")
    elenco_bullet("rt_user_description", "biografia dell'utente del messaggio ritwittato")
    elenco_bullet("rt_text", "testo del messaggio ritwittato.")
    elenco_bullet("rt_hashtag", "hashtag presenti nel messaggio ritwittato")
    elenco_bullet("rt_qtd_count", "numero di volte in cui il messaggio ritwittato è stato citato")
    elenco_bullet("rt_rt_count", "numero di volte in cui il messaggio ritwittato è stato ritwittato")
    elenco_bullet("rt_reply_count", "numero di risposte ricevute dal messaggio ritwittato")
    elenco_bullet("rt_fav_count", "numero di volte in cui il messaggio retweet è stato aggiunto ai preferiti")
    elenco_bullet("rt_tweetid", "ID del messaggio ritwittato")
    elenco_bullet("qtd_screen", "nickname dell'utente che ha citato il tweet originale.")
    elenco_bullet("qtd_userid", "ID univoco dell'utente che ha citato il tweet originale.")
    elenco_bullet("qtd_user_description", "La descrizione o la biografia dell'utente che ha citato il tweet originale.")
    elenco_bullet("qtd_text", "Il testo della citazione.")
    elenco_bullet("qtd_hashtag", "Gli hashtag utilizzati nella citazione.")
    elenco_bullet("qtd_qtd_count", "Il numero di volte in cui il tweet è stato citato.")
    elenco_bullet("qtd_rt_count", "Il numero di volte in cui la citazione è stata retwittata.")
    elenco_bullet("qtd_reply_count", "Il numero di risposte ricevute dalla citazione.")
    elenco_bullet("qtd_fav_count", "Il numero di volte in cui la citazione è stata aggiunta ai preferiti.")
    elenco_bullet("qtd_tweetid", "L'ID del tweet originale citato.")
    elenco_bullet("qtd_urls_list", "Elenco di URL inclusi nella citazione.")
    elenco_bullet("media_urls", "Elenco di URL dei media allegati al tweet originale.")
    elenco_bullet("rt_media_urls", "Elenco di URL dei media allegati al retweet.")
    elenco_bullet("q_media_urls", "Elenco di URL dei media allegati alla citazione.")
    elenco_bullet("cat", "Una possibile colonna aggiuntiva per assegnare una categoria o un'etichetta al tweet.")

    st.write("""
           Notiamo, inoltre, che per quanto riguarda i dati relativi alle temperature (in particolare, i campi *Temperature*, *Feels_Like*, *Temp_Min*, *Temp_Max*) è stata necessaria effettuare un'iniziale conversione da Kelvin a Gradi Celsius.
           Infine, per quanto riguarda tutti i campi che presentavano informazioni relative a data ed ora (*Datetime*, *Sunrise* e *Sunset*) il formato impostato nella API di *Openweather* è il datetime UNIX. Per questo motivo, è stata necessaria, anche in questo caso, una conversione che ha portato alla realizzazione di due nuove colonne specifiche relative a data ed ora.      
           """)
