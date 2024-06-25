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
        loanamount = request.form['loanamount']
        loanpurpose = request.form['loanpurpose']
        ssn = request.form['ssn']
        FICO = random.randint(600, 850)
        inq_last_6mths = random.randint(0,6)
        revol_bal = random.randint(0,100)
        home_ownership = random.randint(0,1)
        # Insert data into MongoDB
    
        collection.insert_one({'First Name': firstname, 'Last Name': lastname, 'SSN':ssn, 'Loan Amount': loanamount, 'Loan Purpose':loanpurpose, 'FICO':FICO,
        'Inquiries in last 6 Months':inq_last_6mths,'Revolving Utilization':revol_bal,'Home Ownership':home_ownership})
        
        # return redirect(url_for('success'))
        return 'Success!'
    return render_template('index.html')

@app.route('/delete', methods=['POST'])
def delete_records():
    if request.method == 'POST':
        # Delete all records from the database
        collection.delete_many({})
        return 'All records are deleted from the database!'

@app.route('/search', methods=['POST'])
def search_records():
    if request.method == 'POST':
        ssn_v1 = request.form['ssn_v1'].strip()
        print(type(ssn_v1))
        record = collection.find_one({'SSN': ssn_v1})
        print(type(record))
        print(record)
        if record:
            # Convert ObjectId to string
            record['_id'] = str(record['_id'])
            # Return the record as JSON response
            return jsonify(record)
        else:
            # If no matching record was found, return an appropriate response
            return jsonify({'message': 'No record found for the provided SSN.'}), 404

@app.route('/success')
def success():
    return 'Data submitted successfully!'

if __name__ == '__main__':
    app.run(debug=True)
