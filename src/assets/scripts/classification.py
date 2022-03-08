import os
import urllib.request
import json
import json
from io import BytesIO
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import streamlit as st


class App:
    def __init__(self):
        if "infer-endpoint-predict" not in st.session_state:
            st.session_state.update({
                "infer-endpoint-predict": os.environ["AZ_MLW_INFER_ENDPOINT_PREDICT_FRAMINGHAM_HEART"],
                "infer-endpoint-key-predict": os.environ["AZ_MLW_INFER_ENDPOINT_KEY_PREDICT_FRAMINGHAM_HEART"]
            })
        
        if "source_df" not in st.session_state:
            self.load_source()

    @staticmethod
    def v_spacer(height, sb=False) -> None:
        for _ in range(height):
            if sb:
                st.sidebar.write('\n')
            else:
                st.write('\n')

    @staticmethod
    def load_source():
        st.session_state['source_df'] = pd.read_csv("src/assets/data/Framingham.csv")
        st.session_state['source_df'].drop(['Death_age', 'Bpressure_status', 'Weight_status', 'Smoke_status', 'Chol_status'], axis=1, inplace=True)

    
    def main(self):
        st.write("A demo using the Azure Machine Learning designer to build and deploy a no-code supervised machine learning model to predict mortality by cardiovascular disease (C.V.D.) from a training sample of the [Framingham heart study](https://en.wikipedia.org/wiki/Framingham_Heart_Study) dataset.")
        st.markdown("**CLICK PREDICT** for a predicition of mortality based on main risk factors. Try adjusting features to see their effect")
        
        with st.form("featuresform"):
            f1, _ = st.columns([1, 1])
            with f1:
                st.selectbox('Sex', ('Female', 'Male'), key="Sex")
            
            f2, f3 = st.columns([1, 1])
            with f2:
                st.number_input("Height", key="Height", value=160, min_value=120, max_value=210, step=10, help='Input Height in cm, in the range 120-210')
            with f3:
                st.number_input("Weight", key="Weight", value=80, min_value=30, max_value=140, step=10, help='Input Weight in kg, in the range 30-140')

            f4, f5 = st.columns([1, 1])
            with f4:
                st.number_input("Diastolic", key="Diastolic", value=100, min_value=40, max_value=170, step=10, help='Input diastolic rate, in the range 40-170')
            with f5:
                st.number_input("Systolic", key="Systolic", value=140, min_value=70, max_value=310, step=10, help='Input systolic, in the range 70-310')
        
            
            f6, f7 = st.columns([1, 1])               
            with f6:
                st.number_input("Cholesterol", key="Cholesterol", value=240, min_value=80, max_value=600, step=20, help='Input cholesterol level, in the range 80-600')
            with f7:
                st.number_input("Smoking", key="Smoking", min_value=0, max_value=60, step=5, help='Input number of cigarettes consumed per day, in the range 0-60')
                
            f8, _ = st.columns([1, 1])
            with f8:
                predict = st.form_submit_button(label="Predict C.V.D. Risk", help='Click to execute model which uses input features to predict C.V.D. risk')

        status_indicator = st.empty()

        if predict:
            prediction = self.make_prediction()
            if prediction == "Alive":
                status_indicator.info("Prediction: Alive!")
            else:
                status_indicator.error("Prediction: Dead!")

        self.show_data_exploration()
        self.show_ml_modelling()

    def make_prediction(self):
        data = {
            "Inputs": {
                "WebServiceInput0":
                [
                    {
                        "Sex": st.session_state['Sex'],
                        "Height": int(st.session_state['Height']) / 2.54, # Convert cm to inches
                        "Weight": int(st.session_state['Weight']) * 2.205, # Convert kg to lbs
                        "Diastolic": int(st.session_state['Diastolic']),
                        "Systolic": int(st.session_state['Systolic']),
                        "Smoking": int(st.session_state['Smoking']),
                        "Cholesterol": int(st.session_state['Cholesterol'])
                    },
                ]
            },
            "GlobalParameters": {
            }
        }

        
        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ st.session_state['infer-endpoint-key-predict'])}
        req = urllib.request.Request(st.session_state['infer-endpoint-predict'], body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            json_result = json.loads(result)
            return (json_result["Results"]["WebServiceOutput0"][0]["Status"])
        except urllib.error.HTTPError as error:
            st.write("Model enpoint request failed with status code: " + str(error.code))
            st.write(error.info())
            st.write(json.loads(error.read().decode("utf8", 'ignore')))
            return('Failed inference!')

    def plot_disto(self, feature):
        fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(10, 4))
        
        female = st.session_state['source_df'][st.session_state['source_df']['Sex']=='Female']
        male = st.session_state['source_df'][st.session_state['source_df']['Sex']=='Male']
        
        # Female
        ax = sns.distplot(female[female['Status']=='Alive'][feature].dropna(), bins=20, label='Alive', ax=axes[0], kde=False)
        ax = sns.distplot(female[female['Status']=='Dead'][feature].dropna(), bins=20, label='Dead', ax=axes[0], kde=False)
        ax.legend()
        ax.set_title('Female')
        
        # Male
        ax = sns.distplot(male[male['Status']=='Alive'][feature].dropna(), bins=20, label='Alive', ax=axes[1], kde=False)
        ax = sns.distplot(male[male['Status']=='Dead'][feature].dropna(), bins=20, label='Dead', ax=axes[1], kde=False)
        ax.legend()
        _ = ax.set_title('Male')
        
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.image(buf)

    def show_data_exploration(self):
        self.v_spacer(height=2, sb=False)
        st.subheader("Data Exploration")
        
        st.markdown('**The Framingham Heart Study Dataset**')
        st.dataframe(st.session_state['source_df'])
        st.write("- From the table above, we can note a few things. All 5209 observations have 'Status', a categorical and nominally scaled variable, with two distinct nonmissing levels, and therefore binary.")
        st.write("- 'Status' identifies whether the anonymous study participant is alive or dead, with minority class 'Dead' representing 38.22% (1991 participants), and 'Alive' 61.78% (3218).")
        st.write("- Variable 'Diastolic' represents artery blood pressure at heart rest between beats")
        st.write("- Variable 'Systolic' represents artery blood pressure when the heart is beating")
        st.write("- Variable 'Height' is recorded in inches. Interval variable 'Weight' is measured in lbs.")
        st.write("- Variable 'Smoking' measures the number of cigarettes consumed per day.")
        st.write("- There are some null values ('N/A') that need to be dealt with.")
        st.write("- Furthermore, the features have widely different ranges, so there will need to be a conversion into the same scale so one feature doesn't dominate the others.")

        self.v_spacer(height=2, sb=False)
        st.markdown("**Dataset Feature Statistics**")
        st.write(st.session_state['source_df'].describe())
        st.write("- The min and max values can be used to define limits on feature values in the predict form.")

        self.v_spacer(height=2, sb=False)
        st.markdown("**Missing Data**")
        st.write(st.session_state['source_df'].isnull().sum())
        st.write("- Rows are present with missing values for the 'Height', 'Weight', 'Smoking', and 'Cholesterol' features. These rows can be dropped from the dataset.")
       
        self.v_spacer(height=2, sb=False)
        st.markdown("**Feature Correlation With Mortality**")      
        st.write("From the plots below you can see there is a higher probability of mortality due to cardiovascular disease when you smoke, especially for men. For women smokers, the survival chances are higher") 
        self.plot_disto('Smoking')
        
        self.v_spacer(height=2, sb=False)
        st.write("The plots below again indicate a particular problem for overweight men where the chances of survival are reduced the heavier they get.")
        self.plot_disto('Weight')
        
        self.v_spacer(height=2, sb=False)
        st.write("Higher cholesterol levels increase the risk of mortality.")
        self.plot_disto('Cholesterol')
        
        self.v_spacer(height=2, sb=False)
        st.write("From the systolic and diastolic plots below, a blood pressure rate below 130/85 (systolic/diastolic) diastolic is recommended to reduce Cardiovascular disease risk")
        self.plot_disto('Diastolic')
        self.plot_disto('Systolic')
        
        self.v_spacer(height=2, sb=False)
        st.write("Features 'Systolic' and 'Diastolic' have a moderate linear correlation and the strongest association with the target label 'Status' (Alive/Dead).")
        st.write("It is clear that risk of death due to C.V.D. becomes greater as systolic and diastolic rates increase.")
        fig = plt.figure(figsize=(7, 3))
        sns.scatterplot(x = "Diastolic", y = "Systolic", data =st.session_state['source_df'], hue="Status",)
        plt.tight_layout()
        st.pyplot(fig)

    def show_ml_modelling(self):
        self.v_spacer(height=2, sb=False)
        st.subheader("Machine Learning Modelling")
        st.write("The image below shows the pipeline developed to model the Framingham dataset for predicting risk of mortality due to cardiovascular disease. Some points of note:")
        st.markdown("- The first **Edit Metadata** node is used to transform 'Sex' into a categorical feature, which can then be split into seperate feature columns based on gender by node **Convert to Indicator Values**")
        st.markdown("- The **Clean Missing Data** node removes rows with null feature values.")
        st.markdown("- The **Group Data into Bins** node uses the number if cigarettes smoked per day to indicate a non-smoker, light smoker, moderate smoker, heavy smoker, or very heavy smoker. This helps to reduce noise in interval features")
        st.markdown("- The **Normalize Data** node transforms all numerical features to a common scale between 0 and 1 to prevent feature dominance where values are high.")
        st.markdown("- The **Split Data** node takes 70%s%% of observations for model training, setting aside the remaining 30%s%% for model evaluation.")
        st.write("The generated model is hosted on a VM to make it available for making a prediction based on new data (inference)")    
        st.image("src/assets/img/framingham-heart-train-pipeline.png")
    

if __name__ == "__main__":
    app = App()
    app.main()