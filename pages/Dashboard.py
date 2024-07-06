"""Page de dashboard"""
from io import BytesIO
import re
import streamlit as st
from google.cloud import storage
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
    data = BytesIO(bucket.get_blob(
    f'{lang}/data.parquet').download_as_bytes())

    return data


langue = st.radio('Pour quelle langue souhaitez-vous afficher les données ?',
                  options=langues.keys())

with st.form('get_dashboard'):
    if langue:
        st.dataframe(get_data(lang=langue))

    submit_prediction = st.form_submit_button('Afficher le dashboard')
