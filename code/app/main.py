import os
import streamlit as st
from streamlit.server.server import Server
from streamlit.script_run_context import add_script_run_ctx
import pandas as pd
import re
import http.client, base64, json, urllib
from urllib import request, parse, error
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import requests, json


class App:
    def __init__(self):
        st.set_page_config(page_title="Azure A.I. Demo Gallery", page_icon="src/assets/img/logo.png", layout="wide", initial_sidebar_state="auto")

        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "http_headers": self._get_session_http_headers(),
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })


    def _get_session_http_headers(self):
        headers = {
            "site_host": "",
            "logged_in_user_name": "",
            "site_deployment_id": ""
        }

        session_id = add_script_run_ctx().streamlit_script_run_ctx.session_id
        session_info = Server.get_current()._get_session_info(session_id)

        # Note case of headers differs from shown in xxx.scm.azurewebsites.net/env
        try:
            if "Host" in session_info.ws.request.headers._dict:
                headers["site_host"] = session_info.ws.request.headers._dict["Host"]

            if "X-Ms-Client-Principal-Name" in session_info.ws.request.headers._dict:
                headers["logged_in_user_name"] = session_info.ws.request.headers._dict["X-Ms-Client-Principal-Name"]

            if "X-Site-Deployment-Id" in session_info.ws.request.headers._dict:
                headers["site_deployment_id"] = session_info.ws.request.headers._dict["X-Site-Deployment-Id"]
        except Exception as ex:
            pass
        return headers

    def main(self):
        if not st.session_state.http_headers["site_host"]:
            st.session_state.http_headers = self._get_session_http_headers()
        #st.title("test")

        topic_demo = {"Language": {"Language Detection": "lang_detect", 
                                   "Sentiment Analysis": "sentiment_analysis",
                                   "Key Phrases": "key_phrases",
                                   "Entity Extraction": "entity_extraction",
                                   "Entity Linking": "entity_linking",
                                   "Text Translation": "text_translation"},
                      "Computer Vision": {"Object Classification": "object_classification", 
                                          "Object Detection": "object_detection" }}

        with st.sidebar:
            st.title("Gallery")
            selected_topic = st.sidebar.selectbox(
                "Select Topic",
                options=sorted(topic_demo.keys())
            )
            
            demo = topic_demo[selected_topic]
            print(demo)
            selected_demo = st.sidebar.selectbox(
                "Select Demo",
                options=sorted(demo)
            )
            st.sidebar.title("About")
            st.sidebar.info(
                "This app demonstrates key Azure A.I. service features.\n\n"
                "Check the code at https://github.com/corticalstackai/azure-ai-demo-gallery"
            )

        method_to_call = getattr(self, demo[selected_demo])
        method_to_call(selected_demo)

    
    def lang_detect(self, demo):
        # Demo example using the REST api rather than the Python SDK
       
        st.title(demo)

        input_text = st.text_input('Input Text', 'Hello')
        if input_text:
            lang_name, _ = self.get_language(input_text)
            if lang_name:
                st.write("Language detected:", lang_name)

    def get_language(self, text):
        api_endpoint = "/text/analytics/v3.1/languages?"
        lang_name = None
        lang_iso6391Name = None

        try:
            jsonBody = {
                "documents":[
                    {"id": 1,
                     "text": text}
                ]
            }

            uri = st.session_state.cog_endpoint.rstrip("/").replace("https://", "")
            conn = http.client.HTTPSConnection(uri)

            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": st.session_state.cog_key
            }

            conn.request("POST", api_endpoint, str(jsonBody).encode("utf-8"), headers)
            response = conn.getresponse()
            data = response.read().decode("UTF-8")

            if response.status == 200:
                results = json.loads(data)
                for document in results["documents"]:
                    print(document)
                    lang_name = document["detectedLanguage"]["name"]
                    lang_iso6391Name = document["detectedLanguage"]["iso6391Name"]

            conn.close()

        except Exception as ex:
            st.write(ex)
        
        return lang_name, lang_iso6391Name

    def sentiment_analysis(self, demo):
        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
        input_text = st.text_input('Input Text', 'surprisingly no covid certificate check upon arrival. extremely slow room service. staff at both bars unfriendly. (evening and morning) low quality bathroom products, in particular the body lotion, gave a skin rash.')
    
        sentimentAnalysis = cog_client.analyze_sentiment(documents=[input_text])[0]
        st.write("Sentiment: {}".format(sentimentAnalysis.sentiment))

    def key_phrases(self, demo):
        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
        input_text = st.text_input('Input Text', "Clean your hands before you put your mask on, as well as before and after you take it off, and after you touch it at any time. Make sure it covers both your nose, mouth and chin.  When you take off a mask, store it in a clean plastic bag, and every day either wash it if it’s a fabric mask, or dispose of a medical mask in a trash bin. Don’t use masks with valves.")
    
        phrases = cog_client.extract_key_phrases(documents=[input_text])[0].key_phrases
        if len(phrases) > 0:
            st.write("\nKey Phrases:")
            for phrase in phrases:
                st.write('\t{}'.format(phrase))

    def entity_extraction(self, demo):
        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
        input_text = st.text_input('Input Text', 'SpaceX is an aerospace manufacturer and space transport services company headquartered in California. It was founded in 2002 by entrepreneur and investor Elon Musk with the goal of reducing space transportation costs and enabling the colonization of Mars.')

        entities = cog_client.recognize_entities(documents=[input_text])[0].entities
        if len(entities) > 0:
            st.write("\nEntities")
            for entity in entities:
                st.write('\t{} ({})'.format(entity.text, entity.category))

    def entity_linking(self, demo):
        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
        input_text = st.text_input('Input Text', 'SpaceX is an aerospace manufacturer and space transport services company headquartered in California. It was founded in 2002 by entrepreneur and investor Elon Musk with the goal of reducing space transportation costs and enabling the colonization of Mars.')

        entities = cog_client.recognize_linked_entities(documents=[input_text])[0].entities
        if len(entities) > 0:
            st.write("\nLinks")
            for linked_entity in entities:
                st.write('\t{} ({})'.format(linked_entity.name, linked_entity.url))


    def text_translation(self, demo):
        translator_endpoint = 'https://api.cognitive.microsofttranslator.com/translate'
        input_text = st.text_input('Input Text', 'SpaceX is an aerospace manufacturer and space transport services company headquartered in California. It was founded in 2002 by entrepreneur and investor Elon Musk with the goal of reducing space transportation costs and enabling the colonization of Mars.')
        if not input_text:
            return
        
        source_lang_name, source_lang_iso6391Name = self.get_language(input_text)
        print(source_lang_name, source_lang_iso6391Name)
        # Build the request
        params = {
            'api-version': '3.0',
            'from': source_lang_iso6391Name,
            'to': ['fr']
        }

        headers = {
            'Ocp-Apim-Subscription-Key': st.session_state.cog_key,
            'Ocp-Apim-Subscription-Region': st.session_state.cog_region,
            'Content-type': 'application/json'
        }

        body = [{
            'text': input_text
        }]

        request = requests.post(translator_endpoint, params=params, headers=headers, json=body)
        response = request.json()
        print(response)
        translation = response[0]["translations"][0]["text"]
        st.write(translation)
       



if __name__ == "__main__":
    app = App()
    app.main()