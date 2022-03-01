import os
import streamlit as st
import http.client
import json


class App:
    def __init__(self):
        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "cog_endpoint": os.environ["AZ_COG_ENDPOINT"],
                "cog_key": os.environ["AZ_COG_KEY"],
                "cog_region": os.environ["AZ_COG_REGION"]
            })

    def main(self):
        # Demo example using the REST api rather than the Python SDK
        input_text = st.text_input('Input Text', 'Hello')
        if input_text:
            lang_name, _ = self.get_language(input_text)
            if lang_name:
                st.write("Language detected:", lang_name)

    def get_language(self, text):
        api_endpoint = "/text/analytics/v3.1/languages?"
        lang_name = None
        lang_iso6391Name = None

        try:
            jsonBody = {
                "documents":[
                    {"id": 1,
                     "text": text}
                ]
            }

            uri = st.session_state.cog_endpoint.rstrip("/").replace("https://", "")
            conn = http.client.HTTPSConnection(uri)

            headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": st.session_state.cog_key
            }

            conn.request("POST", api_endpoint, str(jsonBody).encode("utf-8"), headers)
            response = conn.getresponse()
            data = response.read().decode("UTF-8")

            if response.status == 200:
                results = json.loads(data)
                for document in results["documents"]:
                    print(document)
                    lang_name = document["detectedLanguage"]["name"]
                    lang_iso6391Name = document["detectedLanguage"]["iso6391Name"]

            conn.close()

        except Exception as ex:
            st.write(ex)
        
        return lang_name, lang_iso6391Name


if __name__ == "__main__":
    app = App()
    app.main()