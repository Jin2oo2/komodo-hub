from flask import Flask, request, render_template, url_for, redirect, abort
import sqlite3 as sql
from models import create_feedback_table
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import random
import string

import os
from werkzeug.security import generate_password_hash, check_password_hash

db_path = 'DBTest1.db'
create_feedback_table()

db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///komodoDB.db'
app.secret_key = os.urandom(24)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Password recovery form
class PasswordRecoveryForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Recover Password')

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id)

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

        user = User(username=username, password=generate_password_hash(password, method='scrypt:32768:8:1'), userType=userType)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        print('username: ' + str(username) + ', password: ' + str(password))

        user = User.query.filter_by(username=username).first()
        print(user)

        if not user:
            return '<h1>Wrong username</h1>'
        
        elif check_password_hash(user.password, password):
            login_user(user)
            return '<h1>Logged in</h1>'
        
        else:
            return '<h1>Wrong password</h1>'
    
@app.route('/feedback' , methods = ['GET','POST'], endpoint='feedback')
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
 
    if request.method == 'POST':
        suggestion = request.form['suggestion']
        
        
        conn = sql.connect('DBTest1.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO feedback (submission_date, suggestion) VALUES (CURRENT_TIMESTAMP, ?)", (suggestion,))

        conn.commit()
        conn.close()
        
        return redirect(url_for('feedback'))
    return render_template('feedback.html')  

 #Route for requesting password reset
@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        email = form.email.data
        if email in users:
            token = generate_token()
            # Store the token for the user (e.g., in a database)
            # For now, we'll just print it
            print(f"Password reset token for {email}: {token}")
            send_password_reset_email(email, token)
            flash('Password reset email sent. Check your inbox.')
        else:
            flash('Email not found.')

    return render_template('password_reset.html', form=form)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    userType = db.Column(db.String, nullable=False)
