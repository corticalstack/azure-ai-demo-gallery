import os
import matplotlib.pyplot as plt
from io import BytesIO
import requests
from PIL import Image, ImageDraw
import streamlit as st
from st_clickable_images import clickable_images
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
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
        st.write("An example of using the Azure Computer Vision Image Analysis service to extract a wide variety of visual features from images")
        st.write("Includes object detection with location of labelled objects within bounding boxes")
        st.markdown("**CLICK** any image below to see its features with associated confidence level")

        features = [VisualFeatureTypes.description,
                    VisualFeatureTypes.tags,
                    VisualFeatureTypes.categories,
                    VisualFeatureTypes.brands,
                    VisualFeatureTypes.objects,
                    VisualFeatureTypes.adult]
        
        images = [
                "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=700",
                "https://images.unsplash.com/photo-1546436836-07a91091f160?w=700",
                "https://images.unsplash.com/photo-1614200179396-2bdb77ebf81b?w=700",
                "https://images.unsplash.com/photo-1534361960057-19889db9621e?w=700",
                "https://images.unsplash.com/photo-1612175790672-698305ab79c8?w=700",
                "https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?w=700",
                "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=700",
                "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=700",
                "https://images.unsplash.com/photo-1568736333610-eae6e0ab9206?w=700",
                "https://images.unsplash.com/photo-1532105956626-9569c03602f6?w=700",
                "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=700",
                "https://c.static-nike.com/a/images/w_1920,c_limit/bzl2wmsfh7kgdkufrrjq/image.jpg?w=700",
                "https://cdn.britannica.com/82/130482-050-87C2665C/Actor-Robin-Williams.jpg?w=700",
                "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=700",
                "https://images.unsplash.com/photo-1520716963369-9b24de965de4?w=700",
                "https://images.unsplash.com/photo-1532526338225-bc66ea49a9f2?w=700",
                "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=700",
                "https://images.unsplash.com/photo-1616325629936-99a9013c29c6?w=700",
                "https://images.unsplash.com/photo-1540778339538-067eae485e9f?w=700",
                "https://images.unsplash.com/photo-1545631757-8b75025a310e?w=700",
                "https://images.unsplash.com/photo-1615535248235-253d93813ca5?w=700",
                "https://m.media-amazon.com/images/I/818isgqqL3L._AC_SX466_.jpg?w=700",
                "https://images.unsplash.com/photo-1551120599-440aefce5263?w=700",
                "https://www.lydiamonks.com/wp-content/uploads/2014/06/sugarlump-and-unicorn_1.jpg?w=700"
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

        # Call image analysis service
        analysis = self.cv_client.analyze_image(images[clicked] , features)
        

        # Analysis - captions
        if (len(analysis.description.captions) > 0):
            self.v_spacer(height=2, sb=False)
            st.markdown("**Description**")
            for caption in analysis.description.captions:
                st.write("{} ({:.2f}%)".format(caption.text, caption.confidence * 100))

        # Analysis - tags
        if (len(analysis.tags) > 0):
            self.v_spacer(height=2, sb=False)
            st.markdown("**Tags**")
            for tag in analysis.tags:
                st.write("- {} ({:.2f}%)".format(tag.name, tag.confidence * 100))

        # Analysis - categories
        if (len(analysis.categories) > 0):
            self.v_spacer(height=2, sb=False)
            st.markdown("**Categories**")
            landmarks = []
            celebrities = []
            for category in analysis.categories:
                st.write("- {} ({:.2f}%)".format(category.name, category.score * 100))
                if category.detail:
                    if category.detail.landmarks:
                        for landmark in category.detail.landmarks:
                            if landmark not in landmarks:
                                landmarks.append(landmark)

                    if category.detail.celebrities:
                        for celebrity in category.detail.celebrities:
                            if celebrity not in celebrities:
                                celebrities.append(celebrity)

            # Analysis - landmarks
            if len(landmarks) > 0:
                self.v_spacer(height=2, sb=False)
                st.markdown("**Landmarks**")
                for landmark in landmarks:
                    st.write("- {} ({:.2f}%)".format(landmark.name, landmark.confidence * 100))

            # Analysis - celebrities
            if len(celebrities) > 0:
                self.v_spacer(height=2, sb=False)
                st.markdown("**Celebrities**")
                for celebrity in celebrities:
                    st.write("- {} ({:.2f}%)".format(celebrity.name, celebrity.confidence * 100))

        # Analysis - brands
        if (len(analysis.brands) > 0):
            self.v_spacer(height=2, sb=False)
            st.markdown("**Brands**")
            for brand in analysis.brands:
                st.write("- {} ({:.2f}%)".format(brand.name, brand.confidence * 100))


        # Save image for in prep for thumbnail and object detection
        response = requests.get(images[clicked])
        image = Image.open(BytesIO(response.content))
        image_analysis_file = "temp/image_analysis.jpg"
        image = image.save(image_analysis_file)


        # Generate a thumbnail
        self.v_spacer(height=2, sb=False)
        st.markdown("**Thumbnail Generation**")
        with open(image_analysis_file, mode="rb") as image_data:
            thumbnail_stream = self.cv_client.generate_thumbnail_in_stream(100, 100, image_data, True)

        image_analysis_thumbnail = 'temp/image_analysis_thumbnail.jpg'
        with open(image_analysis_thumbnail, "wb") as thumbnail_file:
            for chunk in thumbnail_stream:
                thumbnail_file.write(chunk)
        st.image(image_analysis_thumbnail)


        # Object detection with bounding boxes and labelling
        if len(analysis.objects) > 0:
            self.v_spacer(height=2, sb=False)
            st.markdown("**Object Detection**")

            fig = plt.figure(figsize=(8, 8))
            plt.tight_layout()
            plt.axis('off')
            
            image = Image.open(image_analysis_file)
            draw = ImageDraw.Draw(image)
            
            color = 'cyan'
            for detected_object in analysis.objects:
                st.markdown("- {} ({:.2f}%)".format(detected_object.object_property, detected_object.confidence * 100))
                
                r = detected_object.rectangle
                bounding_box = ((r.x, r.y), (r.x + r.w, r.y + r.h))
                draw.rectangle(bounding_box, outline=color, width=3)
                plt.annotate(detected_object.object_property,(r.x, r.y), backgroundcolor=color)
            
            plt.imshow(image)
            outputfile = 'temp/image_analysis_object_detection.jpg'
            fig.savefig(outputfile)
            st.image(outputfile)

        
if __name__ == "__main__":
    app = App()
    app.main()