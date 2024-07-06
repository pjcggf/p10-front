"""Page de présentation des résultats"""
import re
import streamlit as st
import requests

st.set_page_config(page_title="P10-Développer un POC", page_icon="🤖")

API_GET_EXAMPLES_URL = 'https://us-central1-p10-developper-poc.cloudfunctions.net/get_examples'
API_GET_PREDICTION_URL = 'https://us-central1-p10-developper-poc.cloudfunctions.net/get_prediction'

st.markdown("""# Développer un POC
## POC : Détection de bad buzz et classification automatisée de sentiment via LLM.""")


@st.cache_data
def get_prediction(text_to_predict, with_answer):
    """Récupère la prediction de classification"""

    json_data = {}
    try:
        result = requests.get(API_GET_PREDICTION_URL,
                              params={
                                  'text_to_predict': text_to_predict,
                                  'with_answer': with_answer
                              },
                              timeout=300).json()
        if result['candidates'][0]['finish_reason'] == 'SAFETY':
            json_data['SAFETY'] = {}
            for reason in result['candidates'][0]['safety_ratings']:
                if reason['probability'] != 'NEGLIGIBLE':
                    json_data['SAFETY'][reason['category']] = {
                        'probability': reason['probability'],
                        'severity_score': reason['severity_score'],
                    }
        elif result['candidates'][0]['finish_reason'] == 'STOP' and with_answer:
            text = result['candidates'][0]['content']['parts'][0]['text']
            regex_text = r"(?<='answer_proposition': ')(.*)(?='}])"
            regex_classif = r"(?<='pred_label': )(\d)(?=, )|(?<='pred_label': ')(\d)(?=', )"
            res = re.findall(regex_classif, text)[0]
            classif = ''
            for _ in res:
                if _:
                    classif = int(_)

            json_data['VALID_RESPONSE'] = {
                'classification': classif,
                'reponse': re.findall(regex_text, text)[0]
            }
        elif result['candidates'][0]['finish_reason'] == 'STOP':
            text = result['candidates'][0]['content']['parts'][0]['text']
            regex_classif = r"(?<='pred_label': )(\d)(?=}])|(?<='pred_label': ')(\d)(?='}])"
            res = re.findall(regex_classif, text)[0]
            classif = ''
            for _ in res:
                if _:
                    classif = int(_)

            json_data['VALID_RESPONSE'] = {
                'classification': classif
            }

    except Exception as e:
        json_data['unexpected_error'] = e

    return json_data

langues = {
    'Anglais': 'en',
    'Français': 'fr',
    'Suédois': 'sw',
    'Turc': 'tk',
    'Hébreu': 'hb'
}

@st.cache_data
def get_examples(lang = 'en', nb_examples = 10):
    '''Fonction pour mettre en cache des exemples'''
    liste_examples = requests.get(
        url = API_GET_EXAMPLES_URL,
        params = {
            'nb' : nb_examples,
            'lang' : lang
        },
        timeout=100).json()

    return liste_examples

st.divider()
choix_exemple = st.radio('**Voulez-vous utiliser un exemple ou rentrer votre propre texte ?**',
         ['Exemple', 'Texte à remplir'], index=None, horizontal=True
         )

choix_reponse = st.radio('**Voulez-vous utiliser obtenir une proposition de réponse ?**',
                         ['Oui', 'Non'], index=1, horizontal=True
                         )
if choix_exemple == 'Exemple':
    st.divider()

    nb_ex = st.slider("Combien d'exemples souhaitez-vous afficher ?",
        min_value=10, max_value=100, step=5)
    langue = st.radio('Dans quelle langue souhaitez-vous avoir vos exemples ?',
            options=langues.keys())

    example_selected = st.selectbox(
        'Pour quel exemples souhaitez-vous une classification ?',
        get_examples(nb_examples=nb_ex, lang=langues[langue]))

elif choix_exemple == 'Texte à remplir':
    st.divider()
    example_selected = st.text_area('Texte à évaluer.')

try:
    st.subheader("Exemple choisi :")
    st.write(example_selected)

except NameError:
    pass

with st.form('get_prediction'):

    submit_prediction = st.form_submit_button('Obtenir une prédiction')
    if submit_prediction:
        choix_reponse = True if choix_reponse == 'Oui' else False
        prediction = get_prediction(text_to_predict=example_selected,with_answer=choix_reponse)

        try:
            if prediction['VALID_RESPONSE']['classification'] == 1:
                st.success('Commentaire positif')
            elif prediction['VALID_RESPONSE']['classification'] == 0:
                st.warning('Commentaire négatif')

            try:
                assert prediction['VALID_RESPONSE']['reponse']
                st.write('Proposition de réponse :')
                st.markdown(
                        f">{prediction['VALID_RESPONSE']['reponse']}")
            except KeyError:
                st.write('Pas de réponse demandée.')

        except KeyError:
            try:
                assert prediction['SAFETY']
                st.error("Traitement impossible, le contenu du commentaire est considéré comme offensant.")
                for i, v in prediction['SAFETY'].items():
                    st.error(f"""Catégorie: {i},
                             probabilité: {v['probability']},
                             sévérité: {round(v['severity_score'], 3)}""")
            except KeyError:
                st.error("Une erreur inconnue est survenue durant la prédiction.")
                st.error(f"Erreur renvoyée: {prediction['unexpected_error']}")
