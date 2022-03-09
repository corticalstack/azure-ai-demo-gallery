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
        st.write("Entity linking identifies and disambiguates the identity of entities found in text, returning a list of recognized entities with links to associated wikipedia pages.")

        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
                
        selected_sample = st.selectbox('Select sample text',
                ('SpaceX is an aerospace manufacturer and space transport services company headquartered in California. It was founded in 2002 by entrepreneur and investor Elon Musk with the goal of reducing space transportation costs and enabling the colonization of Mars.', 
                 'The National Aeronautics and Space Administration (NASA) is an independent agency of the U.S. federal government responsible for the civilian space program, as well as aeronautics and space research.', 
                 'The Empire State Building is a 102-story Art Deco skyscraper in Midtown Manhattan in New York City, United States. It was designed by Shreve, Lamb & Harmon and built from 1930 to 1931. Its name is derived from "Empire State", the nickname of the state of New York. The building has a roof height of 1,250 feet (380 m) and stands a total of 1,454 feet (443.2 m) tall, including its antenna.'))

        
        entities = cog_client.recognize_linked_entities(documents=[selected_sample])[0].entities
        if len(entities) > 0:
            st.write("\n\n")
            st.markdown('**Links**')
            for link in entities[:10]:
                  st.write('\t{} ({})'.format(link.name, link.url))
        
    
if __name__ == "__main__":
    app = App()
    app.main()