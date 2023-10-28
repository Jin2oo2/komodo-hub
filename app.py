from flask import Flask, request, render_template, url_for, redirect, abort
import sqlite3 as sql
from models import create_feedback_table
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

import os
from werkzeug.security import generate_password_hash, check_password_hash

db_path = 'C:\\Users\\owapip install big-ois\\Desktop\\Yggdrasill\\KS\\komodo-hub\\ABC.db'
create_feedback_table()

db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///komodoDB.db'
app.secret_key = os.urandom(24)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def hello():
    registerURL = url_for('register')
    loginURL = url_for('login')
    return render_template('home.html', registerURL=registerURL, loginURL=loginURL)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']
        userType = request.form['usertype']

        user = User(username=username, password=generate_password_hash(password, method='sha256'), userType=userType)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return do_the_login(request.form['username'], request.form['password'])
    
def do_the_login(username, password):
    if username == 'John' and password == '123':
        return '<h1>Success</h1>'
    else:
        abort(403)


@app.route('/feedback' , methods = ['GET','POST'], endpoint='feedback')
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
 
    if request.method == 'POST':
        suggestion = request.form['suggestion']
        
        
        conn = sql.connect('ABC.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO feedback (submission_date, suggestion) VALUES (CURRENT_TIMESTAMP, ?)", (suggestion,))

        conn.commit()
        conn.close()
        
        return redirect(url_for('feedback'))
    return render_template('feedback.html')  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    userType = db.Column(db.String, nullable=False)