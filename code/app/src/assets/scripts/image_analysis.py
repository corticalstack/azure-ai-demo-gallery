import os
import streamlit as st
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

    
    def main(self):
        st.write("Blaa")

        features = [VisualFeatureTypes.description,
                    VisualFeatureTypes.tags,
                    VisualFeatureTypes.categories,
                    VisualFeatureTypes.brands,
                    VisualFeatureTypes.objects,
                    VisualFeatureTypes.adult]
        
        #with open('samples/img/new-york-city.jpg', mode="rb") as image_data:
        #   analysis = self.cv_client.analyze_image_in_stream(image_data , features)
           

        
    
        from st_clickable_images import clickable_images

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
                "https://m.media-amazon.com/images/I/818isgqqL3L._AC_SX466_.jpg?w=700"
            ]
        clicked = clickable_images(
            images,
            titles=[f"Image #{str(i)}" for i in range(5)],
            div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
            img_style={"margin": "5px", "height": "200px"},
        )

        st.markdown(f"Image #{images[clicked]} clicked" if clicked > -1 else "No image clicked")
        st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")

        analysis = self.cv_client.analyze_image(images[clicked] , features)
        # Get image description
        for caption in analysis.description.captions:
            st.write("Description: '{}' (confidence: {:.2f}%)".format(caption.text, caption.confidence * 100))

        if (len(analysis.tags) > 0):
            st.write("Tags: ")
            for tag in analysis.tags:
                st.write(" -'{}' (confidence: {:.2f}%)".format(tag.name, tag.confidence * 100))


        # Get image categories (including celebrities and landmarks)
        if (len(analysis.categories) > 0):
            print("Categories:")
            landmarks = []
            celebrities = []
            for category in analysis.categories:
                # Print the category
                st.write(" -'{}' (confidence: {:.2f}%)".format(category.name, category.score * 100))
                if category.detail:
                    # Get landmarks in this category
                    if category.detail.landmarks:
                        for landmark in category.detail.landmarks:
                            if landmark not in landmarks:
                                landmarks.append(landmark)

                    # Get celebrities in this category
                    if category.detail.celebrities:
                        for celebrity in category.detail.celebrities:
                            if celebrity not in celebrities:
                                celebrities.append(celebrity)

            # If there were landmarks, list them
            if len(landmarks) > 0:
                st.write("Landmarks:")
                for landmark in landmarks:
                    st.write(" -'{}' (confidence: {:.2f}%)".format(landmark.name, landmark.confidence * 100))

            # If there were celebrities, list them
            if len(celebrities) > 0:
                st.write("Celebrities:")
                for celebrity in celebrities:
                    st.write(" -'{}' (confidence: {:.2f}%)".format(celebrity.name, celebrity.confidence * 100))

        # Get brands in the image
        if (len(analysis.brands) > 0):
            st.write("Brands: ")
            for brand in analysis.brands:
                st.write(" -'{}' (confidence: {:.2f}%)".format(brand.name, brand.confidence * 100))


if __name__ == "__main__":
    app = App()
    app.main()