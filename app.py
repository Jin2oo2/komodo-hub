from flask import Flask, request, render_template, url_for, redirect, abort, flash
from flask_bootstrap import Bootstrap
import sqlite3 as sql
from models import create_feedback_table
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
from models import *
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import os
from werkzeug.security import generate_password_hash, check_password_hash

db_path = 'DBTest1.db'
create_feedback_table()

db = SQLAlchemy()

app = Flask(__name__)

bootstarp = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///komodoDB.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

class UploadForm(FlaskForm):
    file = FileField('Choose a file')
    submit = SubmitField('Upload')

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

@app.route('/report_sighting' , methods = ['GET','POST'], endpoint='report_sighting')
def report_sighting():
    if request.method == 'GET':
        return render_template('report_sighting.html')
 
    if request.method == 'POST':
        location = request.form['location']
        species = request.form['species']
        
        conn = sql.connect('DBTest1.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO sightings (date, location, species_name) VALUES (CURRENT_TIMESTAMP, ?, ?)", (location, species, ))

        conn.commit()
        conn.close()
        
        return redirect(url_for('sighting'))
    return render_template('report_sighting.html')


@app.route('/sighting' , methods = ['GET','POST'], endpoint='sighting')
def sighting():

    conn = sql.connect('DBTest1.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM SIGHTINGS')
    sightings = cursor.fetchall()
 
    conn.close()


    return render_template('sighting.html', sightings = sightings)

@app.route('/species' , methods = ['GET','POST'], endpoint='species')
def species():

    conn = sql.connect('DBTest1.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM SPECIES')
    species = cursor.fetchall()
 
    conn.close()


    return render_template('species.html', species = species)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        user = User.query.get(current_user.id)
    
        if user and check_password_hash(user.password, current_password):
            # Hash and update the new password.
            hashed_new_password = generate_password_hash(new_password, method='scrypt:32768:8:1')
            user.password = hashed_new_password

            # Commit changes to the database.
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('feedback'))
        else:
            flash('Current password is incorrect', 'error')

    return render_template('password_reset.html')

@app.route('/library_submit', methods=['GET', 'POST'])
def submit():
    form = UploadForm()
    title = request.form['title']
    description = request.form['description']

    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        # Additional logic for processing the uploaded file, if needed
        return 'File uploaded successfully!'

    return render_template('library_add.html', form=form, title=title, description=description)

@app.route('/library_list')
def librarylist():
    return render_template('library_list.html')    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    userType = db.Column(db.String, nullable=False)
