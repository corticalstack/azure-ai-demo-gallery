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

        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "http_headers": self._get_session_http_headers(),
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    def _get_source_code(self):
        import urllib.request
        url = 'https://raw.githubusercontent.com/corticalstack/azure-ai-demo-gallery/master/code/app/main.py'
        try:
            data = urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as exception:  # type: ignore
            pass

        return data.decode("utf-8")

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

        # Demo example using the REST api rather than the Python SDK
       

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


if __name__ == "__main__":
    app = App()
    app.main()