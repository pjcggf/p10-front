"""Page de dashboard"""
from io import BytesIO
import re
import streamlit as st
from google.cloud import storage

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PIL import Image
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


langue = st.radio('Pour quelle langue souhaitez-vous afficher le dashboard ?',
                  options=langues.keys())

with st.form('get_dashboard'):
    if langue:
        data = pd.read_parquet(get_data(lang=langue))
        st.text(f"Nombres d'exemples disponibles : {data.shape[0]}")
        plot_label = data.label.plot(kind='hist')
        plot_label.set_xticks(ticks=[0, 1], labels=["0-Négatif", "1-Positif"])
        plot_label.set_title('Répartition des labels')
        st.pyplot(plot_label)
    submit_prediction = st.form_submit_button('Afficher le dashboard')
