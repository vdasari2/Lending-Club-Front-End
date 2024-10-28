from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import json
import random
import joblib
import numpy as np
import sklearn
from sklearn.tree import DecisionTreeClassifier
import shap
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
from sklearn.preprocessing import MinMaxScaler
import os 
from dotenv import load_dotenv

load_dotenv()

application = Flask(__name__)
app = application

password = os.getenv('MONGODB_PASSWORD')
connection_string = f"mongodb+srv://vishnupreethamreddy:{password}@cluster0.2hftm.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0"

# MongoDB connection
# client = MongoClient('mongodb://localhost:27017/')
client = MongoClient(connection_string)
db = client.LendingClub
collection = db.ATBReport

model = joblib.load('final_model_v1.pkl')
scaler = joblib.load('avg_cur_bal_scaler.pkl')
print(type(model))
@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        loanamount = int(request.form['loanamount'])
        loanpurpose = request.form['loanpurpose']
        ssn = int(request.form['ssn'])
        dob = request.form['dob']
        income = int(request.form['income'])
        inq_last_6mths = int(request.form['inq'])
        int_rate = float(request.form['intrate'])
        if request.form['homeownership'] == 'Yes':
            home_ownership = 0
        elif request.form['homeownership'] == 'No':
            home_ownership = 1

        if request.form['debtsetlement'] == 'Yes':
            debtsetlement = 1
        elif request.form['debtsetlement'] == 'No':
            debtsetlement = 0

        if request.form['Loandisbursal'] == 'CASH':
            Loandisbursal = 0
        elif request.form['Loandisbursal'] == 'DIRECT PAY':
            Loandisbursal = 1

        if request.form['term'] == '36 Months':
            term = 0
        elif request.form['term'] == '60 Months':
            term = 1

        # if request.form['liststatus'] == 'Whole':
        #     initial_list_status = 1
        # elif request.form['liststatus'] == 'Fractional':
        #     initial_list_status = 0

        if request.form['incomeverification'] == 'Not Verified':
            incomeverification = 0
        elif request.form['incomeverification'] == 'Source Verified':
            incomeverification = 1
        elif request.form['incomeverification'] == 'Source Verified':
            incomeverification = 2
        DTI = float(request.form['DTI'])
        lfico = int(request.form['lfico'])
        ofico = int(request.form['ofico'])
        numtrades = int(request.form['numtrades'])
        currbal = float(request.form['currbal'])
        grossrecovery = int(request.form['grossrecovery'])
        total_rec_late_fee = int(request.form['latefees'])
        recentaccount = int(request.form['recentaccount'])

        curr_bal_scaled_v1 = scaler.transform([[currbal]])[0,0]
        # curr_bal_scaled_v1 = curr_bal_scaled.reshape(1, -1)
        print(curr_bal_scaled_v1)
        features = np.array([
            term,                    
            int_rate,  
            home_ownership,               
            incomeverification,      
            DTI,                   
            lfico,                 
            inq_last_6mths,         
            total_rec_late_fee,       
            grossrecovery,            
            ofico,                   
            numtrades,              
            curr_bal_scaled_v1,              
            recentaccount,          
            Loandisbursal,           
            debtsetlement             
        ]).reshape(1, -1)
        print(features)
        prediction = model.predict(features)
        y_pred_prob = model.predict_proba(features)[:, 1]
        y_pred_prob_v1  = y_pred_prob[0]
        prediction_v1 = int(prediction[0])

        collection.insert_one({'First Name': firstname, 'Last Name': lastname, 'DOB':dob,'Income':income, 'SSN':ssn, 'Loan Amount': loanamount, 'Loan Purpose':loanpurpose,
        'Inquiries in last 6 Months':inq_last_6mths,'Home Ownership':home_ownership,'Interest Rate':int_rate,'Income Verification':incomeverification,
        'DTI':DTI,'fico_range_low':lfico,'Account Management FICO':ofico,'numtrades':numtrades,'currbal':curr_bal_scaled_v1,'disbursement_method':Loandisbursal,'debt_settlement_flag':debtsetlement,
        'Recoveries':grossrecovery,'Late Fees Received to Date':total_rec_late_fee,'recentaccount':recentaccount,'term':term,'PD Score':y_pred_prob_v1,'Prediction Result':prediction_v1})

        features_set = {
            1: ['Term', 0], 
            2: ['Interest_Rate', 0], 
            3: ['HomeOwnerShip', 0], 
            4: ['Income Verification', 0], 
            5: ['Debt To Income Ratio (DTI)', 0], 
            6: ['Latest FICO Score', 0], 
            7: ['Inquiries in Last 6 Months', 0], 
            8: ['Total Recovery Late Fee', 0], 
            9: ['Gross Recovery', 0], 
            10: ['Lowest FICO Ever Reported', 0], 
            11: ['Number of Trades Opened in Last 6 Months', 0], 
            12: ['Avg Current Balance on all Accounts', 0], 
            13: ['Months Since Most Recent Account Opened', 0], 
            14: ['Loan Disbursal Method', 0], 
            15: ['Debt Settlement Flag', 0]
        }
        
        print(features_set.keys)
        # explainer = shap.TreeExplainer(model)
        # shap_values = explainer.shap_values(features)
        # shap_html = shap.plots.force(explainer.expected_value[0], shap_values[..., 0], features)
        # shap.save_html("shap_force_plot.html", shap_html)
        explainer = shap.Explainer(model)
        shap_values = explainer(features)

        print(np.shape(shap_values.values))
        print(shap_values)
        shap_values_instance_class_1 = shap_values[0, :, 1]
        shap_values_instance_class_2 = shap_values_instance_class_1.values
        print(shap_values_instance_class_1.values)

        for i, shap_value in enumerate(shap_values_instance_class_2):
            features_set[i + 1][1] = shap_value 

        # Convert dictionary to DataFrame for better visualization
        features_df = pd.DataFrame.from_dict(features_set, orient='index', columns=['Feature Name', 'SHAP Value'])
        features_df_sorted = features_df.sort_values(by='SHAP Value',ascending=False).head(3)
        for row in features_df_sorted.head(1).values:
            value_1 = (" -> ".join(map(str, row)))
        print(features_df_sorted)


        print(prediction_v1)
        print(features)
        prediction_result = 'Rejected' if prediction[0] == 1 else 'Approved'

        return render_template('result.html', prediction=prediction_result, pd_score = y_pred_prob, SHAP_1 = value_1)

    return render_template('index.html')

@app.route('/delete', methods=['POST'])
def delete_records():
    if request.method == 'POST':
        collection.delete_many({})
        return 'All records are deleted from the database!'

@app.route('/search', methods=['POST'])
def search_records():
    if request.method == 'POST':
        ssn_v1 = int(request.form['ssn_v1'].strip())
        print(ssn_v1)
        record = collection.find_one({'SSN': ssn_v1})
        print(record)
        if record:
            record['_id'] = str(record['_id'])
            return jsonify(record)
        else:
            return jsonify({'message': 'No record found for the provided SSN.'}), 404

@app.route('/success')
def success():
    return 'Data submitted successfully!'

if __name__ == '__main__':
    app.run(debug=True)
