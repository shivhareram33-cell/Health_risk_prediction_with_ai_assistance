import numpy as np 
import pandas as pd
import joblib
from flask import Flask , render_template , request , redirect, url_for, session
from openai import OpenAI
from dotenv import load_dotenv
import os


app = Flask(__name__)


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

app.secret_key = "super_secret_key_123"

patient_model = joblib.load('patient_model.pkl')
doctor_model = joblib.load('doctor_model.pkl')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/user", methods=['GET', 'POST'])
def user():

    reasons = []
    
    if request.method == 'POST':

        reasons = []
        
        Age = float(request.form['Age'])
        Gender = int(request.form['Gender'])
        Execise = int(request.form['Exercise Habits'])
        Smoking = int(request.form['Smoking'])
        family_heart = int(request.form['Family heart Disease'])
        Diabetes = float(request.form['Diabetes'])
        Hbp = float(request.form['High Blood Pressure'])
        Alcohol = int(request.form['Alcohol Consumption'])
        Stress = int(request.form['Stress Level'])
        Suger = int(request.form['Sugar Consumption'])

        input_data = np.array([[Age, Gender, Execise, Smoking,
                                family_heart, Diabetes, Hbp,
                                Alcohol, Stress, Suger]])


        pred = patient_model.predict(input_data)[0]


        if Hbp == 1:
            reasons.append("High Blood Pressure")

        if Diabetes == 1:
            reasons.append("Diabetes")

        if Smoking == 1:
            reasons.append("Smoking habit")

        if Alcohol == 2:
            reasons.append("High alcohol consumption")

        if Stress == 2:
            reasons.append("High stress level")

        if Suger == 2:
            reasons.append("High sugar intake")

        if Execise == 0:
            reasons.append("Lack of physical activity")

        if family_heart == 1:
            reasons.append("Family history of heart disease")

        if Age > 50:
            reasons.append("Higher age risk factor")

        # If no strong reason found
        if len(reasons) == 0:
            reasons.append("No major risk factors detected")

        #  Suggestion Logic
        if pred == 1:
            suggestion = "Consult a healthcare professional and improve lifestyle."
        elif pred == 0:
            suggestion = "Maintain your healthy lifestyle."
        else:
            suggestion = "Monitor health regularly and improve habits."
    
        return render_template(
            'user.html',
            prediction=pred,
            reasons=reasons,
            suggestion=suggestion
            # ai_suggestion= ai_suggestion  
        )

    return render_template("user.html" , reasons = reasons)
   


@app.route("/doctor" , methods=['GET' , 'POST'])
def docto():

    if request.method == 'POST' :


        Age = float(request.form['Age'])
        Gender = int(request.form['Gender'])
        Execise = int(request.form['Exercise Habits'])
        Smoking = int(request.form['Smoking'])
        Alcohol = int(request.form['Alcohol Consumption'])
        Stress = int(request.form['Stress Level'])
        Suger = int(request.form['Sugar Consumption'])
        family_heart = int(request.form['Family heart Disease'])
        Diabetes = float(request.form['Diabetes'])
        Hbp = float(request.form['High Blood Pressure'])
        ldl  = int(request.form["High LDL Cholesterol"])
        sleep = float(request.form['Sleep Hours'])
        weight = float(request.form['weight in Kg'])
        Height = float(request.form['Height in cm'])/100 # convert cm to m

        bmi = (weight / (Height*Height))

        lifestyle_score = Execise + sleep +Smoking - Alcohol - Stress
        age_bmi = Age + bmi

        input_data = np.array([[Gender , family_heart , Diabetes , Hbp , ldl , Suger , lifestyle_score , age_bmi]])

        pred = doctor_model.predict(input_data)[0]

        # reason 

        reasons = []

        if family_heart == 1:
            reasons.append('family history about heart disease')

        if Diabetes == 1:
            reasons.append("Diabetes problem")

        if Hbp == 1:
            reasons.append("High blood presure")
    
        if ldl == 1:
            reasons.append("High cholesterol level")
    
        if Suger == 2:
            reasons.append("High suger consumption")
    
        if Smoking == 1:
            reasons.append("Smoking habit")

        if Alcohol == 2:
            reasons.append("High alcohol consumption")

        if Stress == 2:
            reasons.append("High stress level")

        if Execise == 0:
            reasons.append("Lack of physical activity")

        if Age > 50:
            reasons.append("Higher age risk factor")

        # If no strong reason found
        if len(reasons) == 0:
            reasons.append("No major risk factors detected")

        #  Suggestion Logic
        if pred == 1:
            suggestion = "Consult a healthcare professional and improve lifestyle."
        elif pred == 0:
            suggestion = "Maintain your healthy lifestyle."
        else:
            suggestion = "Monitor health regularly and improve habits."

        session['pred'] = int(pred)
        session['reasons'] = reasons
        session['age'] = Age
        session['bmi'] = bmi
        session['type'] = "doctor"

        return render_template(
            'doctor.html',
            prediction=pred,
            reasons=reasons,
            suggestion=suggestion

        )

    return render_template("doctor.html")


@app.route("/ai")
def ai_suggestion():

    pred = session.get('pred')
    Age = session.get('Age')
    Smoking = session.get('Smoking')
    Stress = session.get('Stress')
    Suger = session.get('Suger')
    reasons = session.get('reasons', [])

    # prompt
    prompt = f"""
    Patient details:
    reasons : {reasons}
    Age: {Age}
    Smoking: {Smoking}
    Stress: {Stress}
    Sugar: {Suger}

    Prediction: {pred}

    you a doctor given that information give the suggetion to patient.
    this is display window of my app so without writing any another thing only give suggetion outoff this. 
    if you do not have inufe info outoff model prediction 0 - low , 1- medium , 2-high , give suggetion and suggetion should be like you are a doctor 
    as a doctor suggest furit name/vegitable/any product to reduce it.

    """
    
# Give short health advice in bullet points
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_suggestion = response.choices[0].message.content

    except Exception as e:
        if pred == 1:
            ai_suggestion = "High risk: Exercise daily, reduce stress, avoid smoking."
        else:
            ai_suggestion = "Low risk: Maintain healthy lifestyle."

    return render_template(
        "user.html",
        ai_suggestion=ai_suggestion,
        prediction=pred
    )

if __name__ ==  "__main__":
    app.run(debug=True)