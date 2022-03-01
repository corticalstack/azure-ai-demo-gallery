import os
from io import BytesIO
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import WebRtcMode, webrtc_streamer, WebRtcStreamerContext
import streamlit as st
import azure.cognitiveservices.speech as speech_sdk

MEDIA_STREAM_CONSTRAINTS = {
    "video": False,
    "audio": {
        "echoCancellation": False,
        "noiseSuppression": True,
        "autoGainControl": True,
    },
}

VOICE_PACK = {
    "fr": "fr-FR-HenriNeural",
    "es": "es-ES-ElviraNeural",
    "de": "de-DE-KatjaNeural"
}
class App:
    def __init__(self):
        if "cog_key" not in st.session_state:
            st.session_state.update({
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })
        
        if "recording_status" not in st.session_state:
            st.session_state["recording_status"] = None

        self.webrtc_ctx = None

    def v_spacer(self, height, sb=False) -> None:
        for _ in range(height):
            if sb:
                st.sidebar.write('\n')
            else:
                st.write('\n')

    def webrtc_audio_recorder(self, wavpath):
        def recorder_factory():
            return MediaRecorder(wavpath)

        self.webrtc_ctx: WebRtcStreamerContext = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDRECV,
            in_recorder_factory=recorder_factory,
            media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
        )

    def main(self):
        st.write("Example of real-time quick and accurate audio transcription to text, which could then be used for search, analytics and inititating events.")
        st.write("Press START to record from your selected audio input device")
        st.write("For example, you could say 'Switch off the bedside lamps' or 'Play Blue Moon by Frank Sinatra'")
        st.write("Once translation completes, press play to hear the results in the locale language voice")
       
        selected_target_lang = st.selectbox('Target Language',
                ('fr', 'es', 'de'))

        source_wavpath = "temp/speech_to_text_audio.wav"
        target_wavpath = "temp/speech_to_speech_audio.wav"
        self.webrtc_audio_recorder(source_wavpath)
  
        status_indicator = st.empty()
        if self.webrtc_ctx.state.playing:
            status_indicator.info("Recording...")
            st.session_state['recording_status'] = 'recording'
            return

        if st.session_state['recording_status'] == 'recording':
            st.session_state['recording_status'] = None
            if Path(source_wavpath).exists():
                speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
                audio_config = speech_sdk.AudioConfig(filename=source_wavpath)
                speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
                speech = speech_recognizer.recognize_once_async().get()
                audio_transcription = speech.text
                
                self.v_spacer(height=2, sb=False)
                st.markdown('**Source Audio To Text Transcription**')
                st.write(audio_transcription)

                translation_config = speech_sdk.translation.SpeechTranslationConfig(st.session_state.cog_key, st.session_state.cog_region)
                translation_config.speech_recognition_language = 'en-GB'
                translation_config.add_target_language(selected_target_lang)

                self.v_spacer(height=2, sb=False)
                st.markdown('**Target Text Transcription**')
                audio_config = speech_sdk.AudioConfig(filename=source_wavpath)
                translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config)
                result = translator.recognize_once_async().get()
                translation = result.translations[selected_target_lang]
                st.write(translation)

                self.v_spacer(height=2, sb=False)
                st.markdown('**Target Audio Synthesis**')
                file_config = speech_sdk.audio.AudioOutputConfig(filename=target_wavpath)
                speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
                speech_config.speech_synthesis_voice_name = VOICE_PACK[selected_target_lang]
                speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config, audio_config=file_config)
                speak = speech_synthesizer.speak_text_async(translation).get()
               
                audio_file = open(target_wavpath, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/ogg')   

    
if __name__ == "__main__":
    app = App()
    app.main()