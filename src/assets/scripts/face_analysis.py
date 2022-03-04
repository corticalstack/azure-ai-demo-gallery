import os
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import streamlit as st
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import FaceAttributeType


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
        self.face_client = FaceClient(st.session_state.cog_endpoint, credential)

    def v_spacer(self, height, sb=False) -> None:
        for _ in range(height):
            if sb:
                st.sidebar.write('\n')
            else:
                st.write('\n')
    
    def main(self):
        st.write("An example of embedding facial recognition using the Azure Face API for out-of-the-box face detection and facial features extraction")
        st.markdown("**Click Take Photo** for your face feature extraction including age estimate - sorry if this insults!")

        # Face detection
        features = [VisualFeatureTypes.faces]
        col1, _ = st.columns(2)
        with col1:
            img_data = st.camera_input("Say Cheese!")
        
        if img_data is None:
            return

        image = Image.open(img_data)
        face_analysis_file = "temp/face_analysis.jpg"
        image = image.save(face_analysis_file)

        with open(face_analysis_file, mode="rb") as img_data:
            analysis = self.cv_client.analyze_image_in_stream(img_data , features)

            if analysis.faces:
                self.v_spacer(height=2, sb=False)
                st.markdown("**Face Detection**")

                fig = plt.figure(figsize=(8, 6))
                plt.axis('off')
                plt.tight_layout()
                image = Image.open(img_data)
                draw = ImageDraw.Draw(image)
                color = 'lightgreen'

                for face in analysis.faces:
                    r = face.face_rectangle
                    bounding_box = ((r.left, r.top), (r.left + r.width, r.top + r.height))
                    draw = ImageDraw.Draw(image)
                    draw.rectangle(bounding_box, outline=color, width=5)
                    annotation = 'Person aged approximately {}'.format(face.age)
                    plt.annotate(annotation,(r.left, r.top), backgroundcolor=color)


                plt.imshow(image)
                outputfile = 'temp/detected_faces.jpg'
                fig.savefig(outputfile)
                st.image(outputfile)

        with open(face_analysis_file, mode="rb") as img_data:
            # Face analysis
            features = [FaceAttributeType.age,
                        FaceAttributeType.emotion,
                        FaceAttributeType.glasses]

            
            detected_faces = self.face_client.face.detect_with_stream(image=img_data,
                                                                    return_face_attributes=features)

            if len(detected_faces) > 0:
                st.markdown("**Face Analysis**")
                st.write(len(detected_faces), 'face(s) detected.')

                for face in detected_faces:
                    detected_attributes = face.face_attributes.as_dict()
                    age = 'age unknown' if 'age' not in detected_attributes.keys() else int(detected_attributes['age'])
                    st.markdown('**Age: ** {}'.format(age))

                    if 'emotion' in detected_attributes:
                        st.markdown("**Emotions**")
                        for emotion_name in detected_attributes['emotion']:
                            st.write('- {}: {}'.format(emotion_name, detected_attributes['emotion'][emotion_name]))
                    
                    if 'glasses' in detected_attributes:
                        st.markdown('**Glasses:** {}'.format(detected_attributes['glasses']))           


if __name__ == "__main__":
    app = App()
    app.main()