"""Page de dashboard"""
from io import BytesIO
import streamlit as st
from google.cloud import storage

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="P10-Dashboard", page_icon="🤖")

PROJECT = 'p10-developper-poc'
client_gcs = storage.Client(project=PROJECT)
bucket = client_gcs.get_bucket('p10-dev-poc')

langues = {
    'Anglais': 'english',
    'Français': 'french',
    'Suédois': 'swedish',
    'Turc': 'turkish'
}


@st.cache_data
def get_data(lang):
    '''Fonction pour récupérer le dataset à utiliser dans l'analyse'''
    lang = langues[lang]
    data_file = BytesIO(bucket.get_blob(
    f'{lang}/data.parquet').download_as_bytes())

    return data_file


st.session_state.activated = st.toggle("Version accessible", value=False)
with st.form('get_dashboard'):
    langue = st.radio('Pour quelle langue souhaitez-vous afficher le dashboard ?',
                    options=langues.keys(), index=None)
    if langue:
        st.divider()
        data = pd.read_parquet(get_data(lang=langue))
        st.text(f"Nombres d'exemples disponibles : {data.shape[0]}")
        st.divider()
        fig_label, ax_lab = plt.subplots()
        ax_lab = data.label.plot(kind='hist')
        ax_lab.set_ylabel('Nb cumulé')
        ax_lab.set_xticks(ticks=[0, 1], labels=["0-Négatif", "1-Positif"])
        ax_lab.set_title('Répartition des labels')
        st.pyplot(fig_label)
        if st.session_state.activated:
            st.text(f"Histogramme représentant la répartition des labels positifs et négatifs\ndans le dataset en {langue}")
            st.text(f"Nombres de labels positifs : {data.label.value_counts()[1]}")
            st.text(f"Nombres de labels négatifs : {data.label.value_counts()[0]}")
        st.divider()
        fig_long, ax_long = plt.subplots()
        ax_long.hist(data['long'])
        ax_long.set_title("Nombre de mots par phrases.")
        st.pyplot(fig_long)
        if st.session_state.activated:
            st.text(f"Histogramme représentant la répartition du nombre de mots par phrase\npour le dataset en {langue}")
            st.text(f"Nombre de mots moyen par phrase : {round(data.long.mean(),2)}")
            st.text(
                f"Ecart-type du nombre de mots par phrase : {round(data.long.std(),2)}")
            st.text(
                f"Longueur de phrase maximale : {data.long.max()}")
    submit_prediction = st.form_submit_button('Afficher le dashboard')
with st.form('get_wordcloud'):
    nb_mots = st.slider('Nombres de mots à afficher',10,100,50)
    if nb_mots and langue:
        data_sample = data.sample(data.shape[0]//8)
        text = " ".join(i for i in data_sample.cleaned_text)
        if st.session_state.activated:
            wordcloud = WordCloud(
                background_color="white",
                max_words=nb_mots,
                colormap='tab20_r',
                min_word_length=3).generate(text)
            fig, ax = plt.subplots()
        else:
            wordcloud = WordCloud(
                background_color="beige",
                max_words=nb_mots,
                min_word_length=3).generate(text)
            fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")

        st.pyplot(fig)
        if st.session_state.activated:
            st.text(f"Nuage de mots représentant les mots les plus présents dans un extrait\ndu dataset en {langue}.")
            st.text(
                f"""Taille du dataset réduite pour permettre l'affichage du nuage de mots.\nNombre d'exemples dans le dataset utilisé : {data_sample.shape[0]}""")
            st.text(f"{nb_mots} mots les plus présents dans le corpus:")
            s = ''
            for i in list(wordcloud.words_.keys())[:nb_mots]:
                s += "- "+i+"\n"
            st.markdown(s)
    st.form_submit_button('Actualiser le nuage de mots')

if st.session_state.activated:
    submit_prediction
