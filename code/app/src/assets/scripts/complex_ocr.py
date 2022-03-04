import os
import time
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import streamlit as st
from st_clickable_images import clickable_images
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials



class App:
    def __init__(self):
        if "cog_endpoint" not in st.session_state:
            st.session_state.update({
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })
        credential = CognitiveServicesCredentials(st.session_state.cog_key) 
        self.cv_client = ComputerVisionClient(st.session_state.cog_endpoint, credential)

    def v_spacer(self, height, sb=False) -> None:
        for _ in range(height):
            if sb:
                st.sidebar.write('\n')
            else:
                st.write('\n')
    
    def main(self):
        st.write("Example demo of the OCR (Optical Character Recognition) Read API for images/pdfs containing lots of text")
        st.markdown("**CLICK** any image below to see if the Read API can detect text")

        images = [
                "https://csairesearchssst.blob.core.windows.net/samples/speccoll.jpg",
                "https://csairesearchssst.blob.core.windows.net/samples/bowers.jpg",
                "https://csairesearchssst.blob.core.windows.net/samples/robertson.jpg"
            ]
        clicked = clickable_images(
            images,
            titles=[f"Image #{str(i)}" for i in range(5)],
            div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
            img_style={"margin": "5px", "height": "450px"},
        )

        st.markdown(f"**You clicked image #{clicked}**" if clicked > -1 else "**No image clicked**")

        if clicked == -1:
            return      

        status_indicator = st.empty()
        results = st.empty()

        read_op = self.cv_client.read(images[clicked], raw=True)

        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        while True:
            status_indicator.info("Status: Processing...")
            read_results = self.cv_client.get_read_result(operation_id)
            if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)

        if read_results.status == OperationStatusCodes.succeeded:
            status_indicator.info("Status: Succeeded!")
            with results.container():
                st.markdown('**OCR Output**')
                for page in read_results.analyze_result.read_results:
                    for line in page.lines:
                            st.write(line.text)
        else:
            status_indicator.error("Status: Read API failed!")


if __name__ == "__main__":
    app = App()
    app.main()