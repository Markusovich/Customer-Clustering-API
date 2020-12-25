# Imports
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from joblib import load
from sklearn.preprocessing import MinMaxScaler


# Calling flask constructor
app = Flask(__name__)
# Setting the connection to the database we will use
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
# Setting the database var
db = SQLAlchemy(app)

# Constructor for the customer posts
class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerName = db.Column(db.String(100), nullable=False)
    purchaseFreq = db.Column(db.Integer, nullable=False)
    daysFromLast = db.Column(db.Integer, nullable=False)
    daysFromFirst = db.Column(db.Integer, nullable=False)
    totalRev = db.Column(db.Float, nullable=False)
    clusterCategory = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Importing our database
#from app import db
#from app import Customers
db.create_all()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/customers', methods=['GET', 'POST'])
def customers():

    if request.method == 'POST':
        customer_name = request.form['name']
        purchase_freq = request.form['freq']
        days_last = request.form['last']
        days_first = request.form['first']
        total_rev = request.form['revenue']

        pipelineClustering = load('pipelineClusteringPickle.joblib')
        clusterDict = {1: 'The new customer cluster. Most likely show signs of low spending.',
                        2: 'The non-frequent buyer cluster. Do not have a long record of shopping.',
                        0: 'The loyal buyer cluster. May have a long record of purchases.',
                        3: 'The highest spender cluster. The category of the highest spenders. '
                        'May have a large record, and shop frequently.'}
        cluster = clusterDict[pipelineClustering.predict([[purchase_freq, days_last, days_first, total_rev]])[0]]

        new_customer = Customers(customerName=customer_name, purchaseFreq=purchase_freq, daysFromLast=days_last, 
        daysFromFirst=days_first, totalRev=total_rev, clusterCategory=cluster)

        db.session.add(new_customer)
        db.session.commit()
        return redirect('/customers')
    else:
        all_customers = Customers.query.order_by(Customers.date_posted).all()
        return render_template('customers.html', customers=all_customers)

@app.route('/customers/delete/<int:id>')
def delete(id):
    customer = Customers.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect('/customers')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    customer = Customers.query.get_or_404(id)

    if request.method == 'POST':
        customer.customerName = request.form['name']
        customer.purchaseFreq = request.form['freq']
        customer.daysFromLast = request.form['last']
        customer.daysFromFirst = request.form['first']
        customer.totalRev = request.form['revenue']

        pipelineClustering = load('pipelineClusteringPickle.joblib')
        clusterDict = {1: 'The new customer cluster. Most likely show signs of low spending.',
                        2: 'The non-frequent buyer cluster. Do not have a long record of shopping.',
                        0: 'The loyal buyer cluster. May have a long record of purchases.',
                        3: 'The highest spender cluster. The category of the highest spenders. '
                        'May have a large record, and shop frequently.'}
        customer.clusterCategory = clusterDict[pipelineClustering.predict([[customer.purchaseFreq, customer.daysFromLast,
                                                                             customer.daysFromFirst, customer.totalRev]])[0]]

        db.session.commit()
        return redirect('/customers')
    else:
        return render_template('edit.html', customer=customer)

@app.route('/customers/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        customer_name = request.form['name']
        purchase_freq = request.form['freq']
        days_last = request.form['last']
        days_first = request.form['first']
        total_rev = request.form['revenue']

        pipelineClustering = load('pipelineClusteringPickle.joblib')
        clusterDict = {1: 'The new customer cluster. Most likely show signs of low spending.',
                        2: 'The non-frequent buyer cluster. Do not have a long record of shopping.',
                        0: 'The loyal buyer cluster. May have a long record of purchases.',
                        3: 'The highest spender cluster. The category of the highest spenders. '
                        'May have a large record, and shop frequently.'}
        cluster = clusterDict[pipelineClustering.predict([[purchase_freq, days_last, days_first, total_rev]])[0]]

        new_customer = Customers(customerName=customer_name, purchaseFreq=purchase_freq, daysFromLast=days_last, 
        daysFromFirst=days_first, totalRev=total_rev, clusterCategory=cluster)
        db.session.add(new_customer)
        db.session.commit()
        return redirect('/customers')
    else:
        return render_template('new_customer.html')

if __name__ == "__main__":
    app.run(debug=True)
