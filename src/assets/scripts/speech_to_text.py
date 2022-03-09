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
        plt.ylabel('Amplitude')
        plt.tight_layout()
      
        # Workaround to resize array-based plot
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.image(buf)

    def webrtc_audio_recorder(self, wavpath):
        def recorder_factory():
            return MediaRecorder(wavpath)

        self.webrtc_ctx: WebRtcStreamerContext = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDONLY,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            in_recorder_factory=recorder_factory,
            media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
        )

    def main(self):
        st.write("Example of real-time quick and accurate audio transcription to text, which could then be used for search, analytics and inititating events")
        st.markdown("Press **START** to record from your selected audio input device")
        st.markdown("For example, you could say **Switch off the bedside lamps** or **Book flights for New York**")
        st.markdown("Note currently **the initialisation of the audio recorder is slow** - after pressing **START** please wait up to 30s for the Status Indicator to change from **Not Recording** to **Recording**")

        wavpath = "temp/speech_to_text_audio.wav"
        self.webrtc_audio_recorder(wavpath)
        
        status_indicator = st.empty()
        if self.webrtc_ctx.state.playing:
            status_indicator.error("Status: Recording...now say something")
            st.session_state['recording_status'] = 'recording'
            return

        status_indicator.info("Status: Not Recording")
        
        if st.session_state['recording_status'] == 'recording':
            st.session_state['recording_status'] = None
            if Path(wavpath).exists():
                speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
                audio_config = speech_sdk.AudioConfig(filename=wavpath)
                speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
                speech = speech_recognizer.recognize_once_async().get()
                audio_transcription = speech.text
                
                self.v_spacer(height=2, sb=False)
                st.markdown('**Audio To Text Transcription**')
                st.write(audio_transcription)
                
                self.v_spacer(height=2, sb=False)
                st.markdown('**Recorded Audio Player**')
                self.wav_file_player(wavpath)
                
                self.v_spacer(height=2, sb=False)
                st.markdown('**Spectrogram**')
                self.plot_wav(wavpath)
        
    
if __name__ == "__main__":
    app = App()
    app.main()