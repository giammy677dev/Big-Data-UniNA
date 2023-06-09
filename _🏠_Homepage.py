from utils import st

st.set_page_config(
    page_title="TwitterAnalytics",
    page_icon="📊",
)

st.image("copertinaHomePage.jpg")

st.title("Dashboard Analitiche Social Network")
st.header("Analitiche e summarization - Twitter")
st.write("""
  Inserire piccola presentazione della dashboard
  """)

st.write("""
      Le analitiche effettuate che ritroviamo in questa dashboard sono le seguenti:
      """)


# Elenco con bullet list e link ai collegamenti delle sezioni
def elenco_bullet(testo_grassetto, testo_normale):
    st.markdown(f"- <span style='color:#00acee'><b>{testo_grassetto}</b></span>: {testo_normale}",
                unsafe_allow_html=True)


# Esempio di utilizzo
elenco_bullet("Prima sezione di Analitiche", "Questo settore delle analitiche è user-oriented in quanto si concentra sull'analisi del comportamento di uno specifico utente selezionabile e sulle interazioni effettuate all'interno della piattaforma. Attraverso operazioni di summarization e di svolte sui dati estratti dai tweet, l'obiettivo principale è comprendere le opinioni e i sentiment degli utenti.")
elenco_bullet("Seconda sezione di Analitiche", "Questo settore delle analitiche è topic-oriented, infatti, le analisi si concentrano sui dati provenienti dai tweet relativi a specifici argomenti di interesse trattati, identificati considerando l'intera totalità di tweet.")
elenco_bullet("Terza sezione di Analitiche", "Questo settore si concentra principalmente nell'identificazione dei cosiddetti influencer, e tutte le analisi fanno riferimento all'infuencer selezionato.")

