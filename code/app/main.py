import os
import streamlit as st
from streamlit.server.server import Server
from streamlit.script_run_context import add_script_run_ctx
import pandas as pd
import http.client
#from urllib import request, parse, error
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import requests
import json
import azure.cognitiveservices.speech as speech_sdk

from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer, WebRtcStreamerContext

from aiortc.contrib.media import MediaRecorder

import queue

import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

import queue
from pathlib import Path
import time
import pydub


TMP_DIR = Path('temp')
if not TMP_DIR.exists():
    TMP_DIR.mkdir(exist_ok=True, parents=True)

MEDIA_STREAM_CONSTRAINTS = {
    "video": False,
    "audio": {
        # these setting doesn't work
        # "sampleRate": 48000,
        # "sampleSize": 16,
        # "channelCount": 1,
        "echoCancellation": False,  # don't turn on else it would reduce wav quality
        "noiseSuppression": True,
        "autoGainControl": True,
    },
}

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

        if "audio_buffer" not in st.session_state:
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        topic_demo = {"Language": {"Language Detection": "lang_detect", 
                                   "Sentiment Analysis": "sentiment_analysis",
                                   "Key Phrases": "key_phrases",
                                   "Entity Extraction": "entity_extraction",
                                   "Entity Linking": "entity_linking",
                                   "Text Translation": "text_translation",
                                   "Speech to Text": "speech_to_text"},
                      "Computer Vision": {"Object Classification": "object_classification", 
                                          "Object Detection": "object_detection" }}

        with st.sidebar:
            st.title("Gallery")
            selected_topic = st.sidebar.selectbox(
                "Select Topic",
                options=sorted(topic_demo.keys())
            )
            
            demo = topic_demo[selected_topic]
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

    def aiortc_audio_recorder(self, wavpath):
        def recorder_factory():
            return MediaRecorder(wavpath)

        webrtc_ctx: WebRtcStreamerContext = webrtc_streamer(
            key="sendonly-audio",
            # mode=WebRtcMode.SENDONLY,
            mode=WebRtcMode.SENDRECV,
            in_recorder_factory=recorder_factory,
            media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
        )


        def save_frames_from_audio_receiver(wavpath):
            webrtc_ctx = webrtc_streamer(
                key="sendonly-audio",
                mode=WebRtcMode.SENDONLY,
                media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
            )

            if "audio_buffer" not in st.session_state:
                st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

            status_indicator = st.empty()
            lottie = False
            while True:
                if webrtc_ctx.audio_receiver:
                    try:
                        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                    except queue.Empty:
                        status_indicator.info("No frame arrived.")
                        continue

                    for i, audio_frame in enumerate(audio_frames):
                        sound = pydub.AudioSegment(
                            data=audio_frame.to_ndarray().tobytes(),
                            sample_width=audio_frame.format.bytes,
                            frame_rate=audio_frame.sample_rate,
                            channels=len(audio_frame.layout.channels),
                        )
                        st.session_state["audio_buffer"] += sound
                else:
                    lottie = True
                    break

            audio_buffer = st.session_state["audio_buffer"]

            if not webrtc_ctx.state.playing and len(audio_buffer) > 0:
                audio_buffer.export(wavpath, format="wav")
                st.session_state["audio_buffer"] = pydub.AudioSegment.empty()


    def display_wavfile(self, wavpath):
        audio_bytes = open(wavpath, 'rb').read()
        file_type = Path(wavpath).suffix
        st.audio(audio_bytes, format=f'audio/{file_type}', start_time=0)


    def plot_wav(self, wavpath):
        audio, sr = sf.read(str(wavpath))
        fig = plt.figure()
        plt.plot(audio)
        plt.xticks(
            np.arange(0, audio.shape[0], sr / 2), np.arange(0, audio.shape[0] / sr, 0.5)
        )
        plt.xlabel('time')
        st.pyplot(fig)

   

    def speech_to_text(self, demo):
        print("Speech to text")
        st.markdown('# recorder')
    
        if "wavpath" not in st.session_state:
            cur_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
            tmp_wavpath = TMP_DIR / f'{cur_time}.wav'
            st.session_state["wavpath"] = str(tmp_wavpath)

        wavpath = st.session_state["wavpath"]

        self.aiortc_audio_recorder(wavpath)  # first way
        # save_frames_from_audio_receiver(wavpath)  # second way

        if Path(wavpath).exists():
           
        
            speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
            print('Ready to use speech service in:', speech_config.region)
            audio_config = speech_sdk.AudioConfig(filename=wavpath)
            speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
            speech = speech_recognizer.recognize_once_async().get()
            command = speech.text
            print(command)
            st.write(command)
            st.markdown(wavpath)
            self.display_wavfile(wavpath)
            self.plot_wav(wavpath)

if __name__ == "__main__":
    app = App()
    app.main()