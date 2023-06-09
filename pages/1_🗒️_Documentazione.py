import streamlit as st

st.image("LogoUniRemakeWhite.png")

st.markdown("<h3 style='text-align: center;'>Documentazione del progetto<br>di Big Data Engineering</h3>", unsafe_allow_html=True)

st.markdown("<h6 style='text-align: center;'>Anno 2022/2023</h6>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Social Network Analysis<br>Summarization<br><br></h1>", unsafe_allow_html=True)

st.write("Orlando Gian Marco M63/001326")
st.write("Perillo Marco M63/001313")
st.write("Russo Diego M63/001335")

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("Traccia"):
    st.write("Contenuto della Traccia")

with st.expander("Categoria 1"):
    st.write("Contenuto della Categoria 1")

with st.expander("Categoria 2"):
    st.write("Contenuto della Categoria 2")

with st.expander("Categoria 3"):
    st.write("Contenuto della Categoria 3")