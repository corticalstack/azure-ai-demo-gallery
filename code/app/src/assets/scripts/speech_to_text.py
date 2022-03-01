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

class App:
    def __init__(self):
        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    def wav_file_player(self, wav_file):
        audio_bytes = open(wav_file, 'rb').read()
        file_type = Path(wav_file).suffix
        st.audio(audio_bytes, format=f'audio/{file_type}', start_time=0)

    def plot_wav(self, wav_file):
        audio, sr = sf.read(str(wav_file))
        fig = plt.figure(figsize= (8, 4), dpi=300)
     
        plt.plot(audio, color="red")
        plt.xticks(np.arange(0, audio.shape[0], sr / 2), np.arange(0, audio.shape[0] / sr, 0.5))
        plt.xlabel('Time')
      
        # Workaround to resize array-based plot
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.image(buf)

    def aiortc_audio_recorder(self, wavpath):
        def recorder_factory():
            return MediaRecorder(wavpath)

        webrtc_ctx: WebRtcStreamerContext = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDRECV,
            in_recorder_factory=recorder_factory,
            media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
        )


    def main(self):
        st.write("Example of real-time quick and accurate audio transcription to text, which could then be used for search, analytics and inititating events.")
        st.write("Press START to record from your selected audio input device")

        if "wav_file" not in st.session_state:
            st.session_state["wav_file"] = "temp/speech_to_text_audio.wav"
            try:
                os.remove(st.session_state["wav_file"])
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))
       

        self.aiortc_audio_recorder(st.session_state["wav_file"])

        if Path(st.session_state["wav_file"]).exists():
            speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
            audio_config = speech_sdk.AudioConfig(filename=st.session_state["wav_file"])
            speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
            speech = speech_recognizer.recognize_once_async().get()
            audio_transcription = speech.text
            
            st.markdown('**Transcription**')
            st.write(audio_transcription)
            self.wav_file_player(st.session_state["wav_file"])
            self.plot_wav(st.session_state["wav_file"])
        
    
if __name__ == "__main__":
    app = App()
    app.main()