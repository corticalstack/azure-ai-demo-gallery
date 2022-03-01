import os
import streamlit as st
import logging
# Get an instance of a logger

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

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

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
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    def _get_source_code(self, script_name):
        file = open("src/assets/scripts/" + script_name + '.py', "r")
        content = file.read()
        return content

    def main(self):
       
        #st.title("test")

        if "audio_buffer" not in st.session_state:
            st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

        topic_demo = {"Language": {"Language Detection": "lang_detect", 
                                   "Sentiment Analysis": "sentiment_analysis",
                                   "Key Phrase Extraction": "key_phrases",
                                   "Entity Extraction": "entity_extraction",
                                   "Entity Linking": "entity_linking",
                                   "Text Translation": "text_translation",
                                   "Speech to Text": "speech_to_text",
                                   "Text to Speech": "text_to_speech",
                                   "Speech to Speech Translation": "speech_to_speech"},
                      "Computer Vision": {"Object Classification": "object_classification", 
                                          "Object Detection": "object_detection" }}

        with st.sidebar:
            st.title("Gallery")
            show_source_code = st.checkbox("Show Source Code", False)

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
                "This app demonstrates a variety of Azure A.I. services in the domains of language & vision.\n\n"
                "Developed by Jon-Paul Boyd. \n\n"
                "Check the code at https://github.com/corticalstackai/azure-ai-demo-gallery"
            )

        python_code = self._get_source_code(demo[selected_demo])
        if python_code is not None:
            st.header(selected_demo)
            try:
                with st.spinner(f"Loading {selected_demo} ..."):
                    exec(python_code, globals()) 
            except Exception as exception: 
                st.write("Error occurred when executing [{0}]".format(selected_demo))
                st.error(str(exception))
                logging.error(exception)
            if show_source_code:
                st.write("\n")
                st.subheader("Source code")
                st.code(python_code)

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

    
    def speech_to_speech(self, demo):
        st.write(demo)

        st.markdown('# recorder')
    
        if "wavpath" not in st.session_state:
            cur_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
            tmp_wavpath = TMP_DIR / f'{cur_time}.wav'
            st.session_state["wavpath"] = str(tmp_wavpath)

        if "wavpath2" not in st.session_state:
            cur_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
            tmp_wavpath = TMP_DIR / f'{cur_time}.wav'
            st.session_state["wavpath2"] = str(tmp_wavpath)

        wavpath = st.session_state["wavpath"]
        wavpath2 = st.session_state["wavpath2"]

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
            #self.plot_wav(wavpath)
            # Configure translation
        
            translation_config = speech_sdk.translation.SpeechTranslationConfig(st.session_state.cog_key, st.session_state.cog_region)
            translation_config.speech_recognition_language = 'en-GB'
            translation_config.add_target_language('fr')
            print('Ready to translate from',translation_config.speech_recognition_language)
            
            audio_config = speech_sdk.AudioConfig(filename=wavpath2)
            translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config)
            print("Getting speech from file...")
            result = translator.recognize_once_async().get()
            print('Translating "{}"'.format(result.text))
            translation = result.translations['fr']
            print(translation)

            file_config = speech_sdk.audio.AudioOutputConfig(filename=wavpath2)
            speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config, audio_config=file_config)
            speak = speech_synthesizer.speak_text_async(translation).get()
       
            audio_file = open(wavpath2, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/ogg')
    




if __name__ == "__main__":
    app = App()
    app.main()