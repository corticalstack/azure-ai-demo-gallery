import os
import streamlit as st
import azure.cognitiveservices.speech as speech_sdk


class App:
    def __init__(self):
        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    def main(self):
        st.write("Transform text to naturally sounding speech")
        
        input_text = st.text_input('Enter input text', 'Sugarlump was a rocking horse, he belonged to a girl and boy. To and fro, to and fro, they rode on their favourite toy')
        selected_voice = st.selectbox('Select voice',
                ('en-US-AnaNeural',
                 'en-GB-LibbyNeural', 
                 'en-GB-RyanNeural',
                 'en-US-SaraNeural'))

        file_name = "temp/text_to_speech_output_audio.wav"
        file_config = speech_sdk.audio.AudioOutputConfig(filename=file_name)
        speech_config = speech_sdk.SpeechConfig(st.session_state.cog_key, st.session_state.cog_region)
        speech_config.speech_synthesis_voice_name = selected_voice
        speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config, audio_config=file_config)
        
        speak = speech_synthesizer.speak_text_async(input_text).get()
        audio_file = open(file_name, 'rb')
        audio_bytes = audio_file.read()

        st.markdown('**Synthesized Speech From Text**')
        st.audio(audio_bytes, format='audio/ogg')


if __name__ == "__main__":
    app = App()
    app.main()