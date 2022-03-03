import streamlit as st
import logging
from collections import OrderedDict

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class App:
    def __init__(self):
        st.set_page_config(page_title="Azure A.I. Demo Gallery", page_icon="src/assets/img/logo.png", layout="wide", initial_sidebar_state="auto")

    def _get_source_code(self, script_name):
        file = open("src/assets/scripts/" + script_name + '.py', "r")
        content = file.read()
        return content

    def main(self):
        domain = OrderedDict([('de', 'Germany'),
                      ('sk', 'Slovakia'),
                      ('hu', 'Hungary'),
                      ('us', 'United States'),
                      ('no', 'Norway')])

        topic_demo = OrderedDict([
                            ('Language', OrderedDict([('Language Detection','lang_detect'),
                                                      ('Key Phrase Extraction','key_phrases'),
                                                      ('Entity Extraction','entity_extraction'),
                                                      ('Entity Linking','entity_linking'),
                                                      ('Sentiment Analysis','sentiment_analysis'),
                                                      ("Text Translation", "text_translation"),
                                                      ("Text to Speech", "text_to_speech"),
                                                      ("Speech to Text", "speech_to_text"),
                                                      ("Speech to Speech", "speech_to_speech")])),
                            ('Computer Vision', OrderedDict([('Image Analysis','image_analysis'),
                                                             ('Object Classification','object_classification'),
                                                             ('Object Detection','object_detection')]))
                      ])

        #topic_demo = OrderedDict([
        #    ("Language": OrderedDict([("Language Detection", "lang_detect"), 
        #                           ("Sentiment Analysis", "sentiment_analysis"),
        #                           ("Key Phrase Extraction", "key_phrases"),
        #                           ("Entity Extraction", "entity_extraction"),
        #                           ("Entity Linking", "entity_linking"),
        #                           ("Text Translation", "text_translation"),
        #                           ("Speech to Text", "speech_to_text"),
        #                           ("Text to Speech", "text_to_speech"),
        #                           ("Speech to Speech Translation", "speech_to_speech")])),
        #    ("Computer Vision": OrderedDict([("Object Classification", "object_classification"), 
        #                                  ("Object Detection", "object_detection")]))])

        with st.sidebar:
            st.title("Gallery")
            show_source_code = st.checkbox("Show Source Code", False)

            selected_topic = st.sidebar.selectbox(
                "Select Topic",
                options=topic_demo.keys()
            )
            
            demo = topic_demo[selected_topic]
            selected_demo = st.sidebar.selectbox(
                "Select Demo",
                options=demo
            )
            
            st.sidebar.title("About")
            st.sidebar.info(
                "This app demonstrates a variety of Azure A.I. services in the domains of language & vision.\n\n"
                "Developed by Jon-Paul Boyd. \n\n"
                "Check the code at https://github.com/corticalstack/azure-ai-demo-gallery"
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


if __name__ == "__main__":
    app = App()
    app.main()