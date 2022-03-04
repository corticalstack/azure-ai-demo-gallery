import os
import time
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
        st.write("OCR (Optical Character Recognition) example using the Azure OCR API for detecting small amounts of printed text in images")
        st.markdown("**CLICK** any image below to see if OCR can detect text")

        images = [
                "https://images.unsplash.com/photo-1520716963369-9b24de965de4?w=700",
                "https://images.unsplash.com/photo-1561931153-1c178973c0eb?w=700",
                "https://images.unsplash.com/photo-1494331789569-f98601f1934f?w=700",
                "https://images.unsplash.com/photo-1580938435284-3a2d3a3603d2?w=700",
                "https://images.unsplash.com/photo-1527474362609-8c66156e7c33?w=700",
                "https://images.unsplash.com/photo-1516916759473-600c07bc12d4?w=700",
                "https://images.unsplash.com/photo-1627135775457-9c001a0537bf?w=700",
                "https://images.unsplash.com/photo-1572844980501-10a1fcb2587f?w=700",
                "https://images.unsplash.com/photo-1513107132060-48f411aff83c?w=700",
                "https://images.unsplash.com/photo-1548722038-fbe52045aa57?w=700",
                "https://images.unsplash.com/photo-1579705379005-1cdcdc76f793?w=700",
                "https://images.unsplash.com/photo-1583225214464-9296029427aa?w=700"

            ]
        clicked = clickable_images(
            images,
            titles=[f"Image #{str(i)}" for i in range(5)],
            div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
            img_style={"margin": "5px", "height": "200px"},
        )

        st.markdown(f"**You clicked image #{clicked}**" if clicked > -1 else "**No image clicked**")

        if clicked == -1:
            return      

        read_op = self.cv_client.read(images[clicked], raw=True)

        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        while True:
            read_results = self.cv_client.get_read_result(operation_id)
            if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)

        if read_results.status == OperationStatusCodes.succeeded:
            if len(read_results.analyze_result.read_results) > 0:
                st.markdown("**Text detected**")
                for page in read_results.analyze_result.read_results:
                    for line in page.lines:
                        st.write('- {}'.format(line.text))
            else:
                st.markdown("**No text detected**")


if __name__ == "__main__":
    app = App()
    app.main()