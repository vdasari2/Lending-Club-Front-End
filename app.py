from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import json
import random

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client.LendingClub
collection = db.ATBReport

@app.route('/', methods=['GET', 'POST'])
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
            debtsetlement = 1

        if request.form['Loandisbursal'] == 'CASH':
            Loandisbursal = 0
        elif request.form['Loandisbursal'] == 'DIRECT PAY':
            Loandisbursal = 1

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
        currbal = int(request.form['currbal'])

        collection.insert_one({'First Name': firstname, 'Last Name': lastname, 'DOB':dob,'Income':income, 'SSN':ssn, 'Loan Amount': loanamount, 'Loan Purpose':loanpurpose,
        'Inquiries in last 6 Months':inq_last_6mths,'Home Ownership':home_ownership,'Interest Rate':int_rate,'Income Verification':incomeverification,
        'DTI':DTI,'fico_range_low':lfico,'Account Management FICO':ofico,'numtrades':numtrades,'currbal':currbal,'disbursement_method':Loandisbursal,'debt_settlement_flag':debtsetlement})
        
        return 'Success!'
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
