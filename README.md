# 🚀 Azure AI Demo Gallery

A comprehensive showcase of Azure AI services and capabilities through interactive demos.

## 📋 Description

This repository contains a Streamlit-based web application that demonstrates various Azure AI services in the domains of language, vision, and machine learning. It provides interactive examples of how to use Azure's cognitive services for tasks such as image analysis, face detection, OCR, sentiment analysis, language detection, speech services, and more.

The application is designed to be educational, allowing users to interact with Azure AI services through a user-friendly interface while also providing access to the source code for each demo.

## ✨ Features

- **Language Services**
  - [Language Detection](src/assets/scripts/lang_detect.py) - Detect the language of input text
  - [Key Phrase Extraction](src/assets/scripts/key_phrases.py) - Extract key phrases from text
  - [Entity Extraction](src/assets/scripts/entity_extraction.py) - Identify and extract entities from text
  - [Entity Linking](src/assets/scripts/entity_linking.py) - Link entities to known references
  - [Sentiment Analysis](src/assets/scripts/sentiment_analysis.py) - Analyze sentiment in text
  - [Text Translation](src/assets/scripts/text_translation.py) - Translate text between languages
  - [Text to Speech](src/assets/scripts/text_to_speech.py) - Convert text to spoken audio
  - [Speech to Text](src/assets/scripts/speech_to_text.py) - Convert spoken audio to text
  - [Speech to Speech](src/assets/scripts/speech_to_speech.py) - Translate spoken audio to another language

- **Computer Vision Services**
  - [Image Analysis](src/assets/scripts/image_analysis.py) - Analyze images for content, tags, objects, and more
  - [Face Analysis](src/assets/scripts/face_analysis.py) - Detect and analyze faces in images
  - [Simple OCR](src/assets/scripts/simple_ocr.py) - Extract text from images
  - [Complex OCR](src/assets/scripts/complex_ocr.py) - Advanced text extraction from complex images

- **Machine Learning Services**
  - [Classification](src/assets/scripts/classification.py) - Predict cardiovascular disease risk using the Framingham Heart Study dataset

## 🔧 Prerequisites

To run this application, you'll need:

1. An Azure account with the following services enabled:
   - Azure Cognitive Services (for language and vision services)
   - Azure Machine Learning (for prediction services)

2. The following environment variables set with your Azure service credentials:
   - `AZ_COG_ENDPOINT` - Cognitive Services endpoint
   - `AZ_COG_KEY` - Cognitive Services API key
   - `AZ_COG_REGION` - Cognitive Services region
   - `AZ_MLW_INFER_ENDPOINT_PREDICT_FRAMINGHAM_HEART` - Machine Learning endpoint for heart disease prediction
   - `AZ_MLW_INFER_ENDPOINT_KEY_PREDICT_FRAMINGHAM_HEART` - Machine Learning API key for heart disease prediction

## 🛠️ Setup Guide

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/corticalstack/azure-ai-demo-gallery.git
   cd azure-ai-demo-gallery
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables with your Azure credentials.

4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

### Docker Deployment

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

   This will build the Docker image with your Azure credentials and start the application.

## 📚 Resources

- [Azure Cognitive Services Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/)
- [Azure Machine Learning Documentation](https://docs.microsoft.com/en-us/azure/machine-learning/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## ❓ FAQ

**Q: Why does the app get downscaled in the evening?**  
A: As mentioned in the app's about section, the application consumes compute resources from a personal Azure subscription, so it is downscaled each evening to reduce costs.

**Q: How can I add my own demo to the gallery?**  
A: Create a new Python script in the `src/assets/scripts/` directory following the pattern of the existing demos. Then add your demo to the `topic_demo` OrderedDict in `app.py`.

**Q: Do I need to have all the Azure services set up to run the application?**  
A: Yes, the application expects all the environment variables to be set. However, you could modify the code to make certain services optional if you only want to run specific demos.

