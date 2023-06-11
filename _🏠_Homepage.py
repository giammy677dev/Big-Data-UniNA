from utils import st, elenco_bullet

st.set_page_config(
    page_title="Homepage",
    page_icon="📊",
    layout='wide'
)

st.image("utility/copertinaHomePage.jpg")

st.title("Dashboard Analitiche Social Network")
st.header("Analitiche e summarization - Twitter")
st.write("""L'obiettivo di tale dashboard è quello di generare una serie di reportistiche che permettano di caratterizzare
            gli interessi ed il tipo di contenuto pubblicato da una serie di utenti su Twitter durante il periodo compreso
            tra giugno e dicembre del 2020.
  """)

st.write("""
      Le analitiche effettuate sono state raggruppate in tre sezioni. Di seguito ne riportiamo una breve presentazione:
      """)


# Esempio di utilizzo
elenco_bullet("Analitica 1 - Gli Utenti", """Tale sezione si focalizza sull'analisi del comportamento degli utenti e
                                            sulle interazioni effettuate all'interno della piattaforma. E' possibile
                                            selezionare uno specifico utente e, attraverso operazioni di summarization
                                            svolte sui dati estratti dai tweet pubblicati dall'utente selezionato, è
                                            possibile comprendere opinioni e sentiment dell'utente stesso rispetto ai
                                            topic di cui ha discusso su Twitter;""")
elenco_bullet("Analitica 2 - I Topic", """Tale sezione si focalizza sull'analisi dei topic di cui gli utenti hanno
                                        maggiormente discusso sulla piattaforma. Le analisi effettuate si focalizzano sui
                                        dati provenienti dai tweet relativi a specifici argomenti di interesse trattati,
                                        identificati considerando l'intera totalità di tweet. Inoltre, è possibile visualizzare
                                        un breve riassunto delle opinioni degli utenti rispetto ad un qualsiasi topic
                                        appositamente inserito tramite un box di testo;""")
elenco_bullet("Analitica 3 - Gli Opinion Leader", """Tale sezione si focalizza principalmente nell'identificazione dei
                                                    cosiddetti "Opinion Leader". Gli Opinion Leader sono coloro che -
                                                    tramite i proprio contenuti sulla piattaforma - hanno ottenuto molte
                                                    interazioni da parte di altri utenti. Lo scopo delle nostre analitiche,
                                                    allora, è stato quello di cercare di identificare in che modo i loro
                                                    contenuti sono stati in grado di influenzare l'opinione pubblica ed
                                                    analizzare il tipo di sentiment che sono stati in grado di suscitare
                                                    negli utenti.""")
