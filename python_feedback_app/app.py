from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail


app = Flask(__name__)

ENV = 'dev' # setting a value dev for environment

if ENV == 'prod':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sqlpost@localhost/lexus'

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dmesamxfsujkqk:19f6c0777ced87a2b423c6d1d7885d1baacfb0c9774cc8bac121863537a954f5@ec2-18-215-96-22.compute-1.amazonaws.com:5432/d7mbmh4tl8it92'

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        database_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        # print(customer, dealer, rating, comments)
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')
        # creating a query and filter by customer    
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data) # adding the data
            db.session.commit()
            send_mail(customer, dealer, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='already submiited')
        


if __name__ == '__main__':
    app.run()