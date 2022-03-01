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
        st.write("Mine text to see what people are thinking based on their hotel reviews from Booking.com")

        credential = AzureKeyCredential(st.session_state.cog_key)
        cog_client = TextAnalyticsClient(endpoint=st.session_state.cog_endpoint, credential=credential)
                
        selected_sample = st.selectbox('Select sample text',
                ('surprisingly no covid certificate check upon arrival. extremely slow room service. staff at both bars unfriendly. (evening and morning) low quality bathroom products, in particular the body lotion, gave a skin rash.', 
                 'Super room overlooking the lake. First night we dined at the inhouse Italian restaurant which was fabulous. Overall we really liked this hotel and would definitely return again. Good location right on the lake waterfront. Nice and quiet room with good amenities and friendly staff', 
                 'Light fittings in room were unsafe.. ended up burning my hand badly on the bedside lamp and spending a night with my hand wrapped in ice, getting little sleep as a result. The hotel reaction was pretty mediocre.. someone bought me ice but there was no apology or checking if I was ok.',
                 'The different locations were not obvious to me when I booked'))

        st.markdown('**Analysis**')
        sentimentAnalysis = cog_client.analyze_sentiment(documents=[selected_sample])[0]
        st.write("Highest sentiment: ", sentimentAnalysis.sentiment)
        st.write("Confidence scores: ", sentimentAnalysis.confidence_scores)
    

if __name__ == "__main__":
    app = App()
    app.main()