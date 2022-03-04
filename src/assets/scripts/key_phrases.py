import os
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


class App:
    def __init__(self):
        if "cog_endpoint" not in st.session_state:
            st.session_state.update({
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    
    def main(self):
        # Demo example using the Python SDK
        st.write("Key phrase extraction can be used to quickly identify the main concepts in text.")

        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
                
        selected_sample = st.selectbox('Select sample text',
                ('Clean your hands before you put your mask on, as well as before and after you take it off, and after you touch it at any time. Make sure it covers both your nose, mouth and chin.  When you take off a mask, store it in a clean plastic bag, and every day either wash it if it’s a fabric mask, or dispose of a medical mask in a trash bin. Don’t use masks with valves.', 
                 'The National Aeronautics and Space Administration (NASA) is an independent agency of the U.S. federal government responsible for the civilian space program, as well as aeronautics and space research.', 
                 'The Empire State Building is a 102-story Art Deco skyscraper in Midtown Manhattan in New York City, United States. It was designed by Shreve, Lamb & Harmon and built from 1930 to 1931. Its name is derived from "Empire State", the nickname of the state of New York. The building has a roof height of 1,250 feet (380 m) and stands a total of 1,454 feet (443.2 m) tall, including its antenna.'))

        phrases = cog_client.extract_key_phrases(documents=[selected_sample])[0].key_phrases
        if len(phrases) > 0:
            st.write("\n\n")
            st.markdown('**Key Phrases**')
            for phrase in phrases[:5]:
                st.write(phrase)

if __name__ == "__main__":
    app = App()
    app.main()