from flask import Flask, request, render_template, url_for, redirect, abort, flash, session, send_file
from flask_bootstrap import Bootstrap
import sqlite3 as sql
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)


db_path = 'instance//DBTest1.db'

db = SQLAlchemy()

app = Flask(__name__)

bootstarp = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DBTest1.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)
db.init_app(app)
app.logger.addHandler(handler)
login_manager = LoginManager()
login_manager.init_app(app)

class UploadForm(FlaskForm):
    file = FileField('Choose a file')
    submit = SubmitField('Upload')

class LibraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))  # Assuming you store file paths as strings


@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id)

@app.route('/')
def hello():
    registerURL = url_for('register')
    loginURL = url_for('login')
    return render_template('home.html', registerURL=registerURL, loginURL=loginURL)

@app.route('/news')
def news():
    return render_template('news.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = sql.connect(db_path)
            cursor = connection.cursor()

            # Check if the username is already taken
            existing_user_query = "SELECT * FROM User WHERE username = ?"
            existing_user = cursor.execute(existing_user_query, (username,)).fetchone()

            if existing_user:
                flash('Username is already taken. Choose a different one.', 'danger')
                return redirect(url_for('register'))

            # Insert new user
            insert_user_query = "INSERT INTO User (username, password, Type) VALUES (?, ?, ?)"
            cursor.execute(insert_user_query, (username, generate_password_hash(password, method='sha256'), None))

            # Commit changes
            connection.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            flash('Error with database operation. Please try again.', 'danger')

        finally:
            if connection:
                connection.close()

    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            login_user(user)
            user_id = user.User_ID
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')
        
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello'))
    
@app.route('/feedback' , methods = ['GET','POST'], endpoint='feedback')
@login_required
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
 
    if request.method == 'POST':
        suggestion = request.form['suggestion']
        
        
        conn = sql.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO feedback (submission_date, suggestion) VALUES (CURRENT_TIMESTAMP, ?)", (suggestion,))

        conn.commit()
        conn.close()
        
        return redirect(url_for('feedback'))
    return render_template('feedback.html')  

@app.route('/report_sighting' , methods = ['GET','POST'], endpoint='report_sighting')
@login_required
def report_sighting():
    if request.method == 'GET':
        return render_template('report_sighting.html')
 
    if request.method == 'POST':
        location = request.form['location']
        species = request.form['species']
        
        conn = sql.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO sightings (date, location, species_name) VALUES (CURRENT_TIMESTAMP, ?, ?)", (location, species, ))

        conn.commit()
        conn.close()
        
        return redirect(url_for('sighting'))
    return render_template('report_sighting.html')


@app.route('/sighting' , methods = ['GET','POST'], endpoint='sighting')
@login_required
def sighting():

    conn = sql.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM SIGHTINGS')
    sightings = cursor.fetchall()
 
    conn.close()


    return render_template('sighting.html', sightings = sightings)

@app.route('/species' , methods = ['GET','POST'], endpoint='species')
def species():

    conn = sql.connect(db_path)
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
@login_required
def submit():
    form = UploadForm()

    if request.method == 'POST' and form.validate_on_submit():
        title = request.form.get('title')
        description = request.form.get('description')
        file = form.file.data

        try:
            # Save the file to the UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            new_item = LibraryItem(title=title, description=description, file_path=file_path)

            db.session.add(new_item)
            db.session.commit()

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('librarylist'))

        except Exception as e:
            print(f"An error occurred: {e}")
            flash('Error uploading file. Please try again.', 'danger')

    return render_template('library_add.html', form=form)

@app.route('/library_list')
@login_required
def librarylist():
    library_contents = get_library_contents()  # You need to implement this function
    return render_template('library_list.html', library_contents=library_contents)   

@app.route("/register/school", methods=['GET', 'POST'])
def register_school():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        school_name = request.form.get('school_name')
        supervisor_name = request.form.get('supervisor_name')
        supervisor_phone = request.form.get('supervisor_phone')
        access_code = request.form.get('access_code')

        try:
            connection = sql.connect(db_path)
            cursor = connection.cursor()

            existing_user_query = "SELECT * FROM User WHERE username = ?"
            existing_user = cursor.execute(existing_user_query, (username,)).fetchone()

            if existing_user:
                flash('Username is already taken. Choose a different one.', 'danger')
                return redirect(url_for('register_school'))

            insert_user_query = "INSERT INTO User (username, password, Type) VALUES (?, ?, ?)"
            cursor.execute(insert_user_query, (username, generate_password_hash(password, method='sha256'), 'SCHOOL'))

            get_user_id_query = "SELECT User_ID FROM User WHERE username = ?"
            user_id = cursor.execute(get_user_id_query, (username,)).fetchone()

            if user_id:
                insert_school_query = "INSERT INTO School (User_ID, School_Name, Supervisor_Name, Supervisor_Phone, Access_Code) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(insert_school_query, (user_id[0], school_name, supervisor_name, supervisor_phone, access_code))
                connection.commit()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating school. Please try again.', 'danger')
                return redirect(url_for('register_school'))

        except sql.Error as e:
            print(f"SQLite error: {e}")
            flash('Error with database operation. Please try again.', 'danger')
            return redirect(url_for('register_school'))

    return render_template('register_school.html')


@app.route("/register/teacher", methods=['GET', 'POST'])
def register_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        school_id = request.form.get('school_id')
        Class_id = request.form.get('class_id')

        try:
            connection = sql.connect(db_path)
            cursor = connection.cursor()

            existing_user_query = "SELECT * FROM User WHERE username = ?"
            existing_user = cursor.execute(existing_user_query, (username,)).fetchone()

            if existing_user:
                flash('Username is already taken. Choose a different one.', 'danger')
                return redirect(url_for('register_teacher'))

            insert_user_query = "INSERT INTO User (username, password, Type) VALUES (?, ?, ?)"
            cursor.execute(insert_user_query, (username, generate_password_hash(password, method='sha256'), 'TEACHER'))

            get_user_id_query = "SELECT User_ID FROM User WHERE username = ?"
            user_id = cursor.execute(get_user_id_query, (username,)).fetchone()

            if user_id:
                insert_teacher_query = "INSERT INTO Teacher (User_ID, First_Name, Last_Name, School_ID) VALUES (?, ?, ?, ?)"
                cursor.execute(insert_teacher_query, (user_id[0], first_name, last_name, school_id))                
                connection.commit()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating teacher. Please try again.', 'danger')
                return redirect(url_for('register_teacher'))

        except sql.Error as e:
            print(f"SQLite error: {e}")
            flash('Error with database operation. Please try again.', 'danger')
            return redirect(url_for('register_teacher'))

    return render_template('register_teacher.html')




@app.route("/register/student", methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('hello'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        school_id = request.form.get('school_id')  
        class_id = request.form.get('class_id')  

        try:
            connection = sql.connect(db_path)
            cursor = connection.cursor()

            existing_user_query = "SELECT * FROM User WHERE username = ?"
            existing_user = cursor.execute(existing_user_query, (username,)).fetchone()

            if existing_user:
                flash('Username is already taken. Choose a different one.', 'danger')
                return redirect(url_for('register_student'))

            insert_user_query = "INSERT INTO User (username, password, Type) VALUES (?, ?, ?)"
            cursor.execute(insert_user_query, (username, generate_password_hash(password, method='sha256'), 'STUDENT'))

            get_user_id_query = "SELECT User_ID FROM User WHERE username = ?"
            user_id = cursor.execute(get_user_id_query, (username,)).fetchone()

            if user_id:
                insert_student_query = "INSERT INTO Student (User_ID, First_Name, Last_Name, School_ID, Class_ID) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(insert_student_query, (user_id[0], first_name, last_name, school_id, class_id))
                connection.commit()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating student. Please try again.', 'danger')
                return redirect(url_for('register_student'))

        except sql.Error as e:
            print(f"SQLite error: {e}")
            flash('Error with database operation. Please try again.', 'danger')
            return redirect(url_for('register_student'))

    return render_template('register_student.html')


@app.route('/business_dashboard')
def businessDashboard():
    return render_template('business_dashboard.html', users=getUsers())


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        if new_username:
            current_user.username = new_username  # Update the username in the current_user object
            db.session.commit()  # Commit the changes to the database

    user_data = {
        'username': current_user.username,
        'user_type': current_user.Type  # Assuming 'userType' is an attribute in your User model
    }

    return render_template('profile.html', user=user_data)
  
quiz_data = {
    "What is the largest primate in Indonesia?": ["Sumatran Orangutan", "orangutan"],
    "Which species of turtle is critically endangered in Indonesia?": ["Leatherback Turtle", "leatherback"],
    "What is the national animal of Indonesia?": ["Javan Hawk-Eagle", "hawk-eagle"],
    "Which big cat is found in Sumatra and is critically endangered?": ["Sumatran Tiger", "tiger"],
    "What is the world's rarest rhinoceros, found in Indonesia?": ["Javan Rhino", "rhino"],
}

def ask_question(question, correct_answer):
    user_answer = request.form.get(question)
    
    # Check if the form data is None
    if user_answer is None:
        return False
    
    # Convert to lowercase and compare
    return user_answer.lower() == correct_answer

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        score = 0

        # Shuffle the questions
        questions = list(quiz_data.keys())
        random.shuffle(questions)

        for question in questions:
            correct_answer = quiz_data[question][0].lower()
            if ask_question(question, correct_answer):
                score += 1

        return render_template('results.html', score=score, total=len(quiz_data))

    # If the request method is GET, show the quiz form
    return render_template('quiz.html', questions=quiz_data.keys())

def get_student_data(user_id):
    # You need to modify this query based on your database schema
    query = """
        SELECT * FROM Student
        WHERE User_ID = ?
    """
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    student_data = cursor.execute(query, (user_id,)).fetchall()
    conn.close()

    return student_data



@app.route('/download_file/<path:file_path>')
def download_file(file_path):
    # Construct the full path to the file on your server
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)

    # Use Flask's send_file to send the file to the user
    return send_file(full_path, as_attachment=True)


@app.route('/student_dashboard')
@login_required
def student_dashboard():
    # Check if the current user is a student
    if current_user.Type != 'TEACHER':
        abort(403)  # Forbidden, redirect to an error page or display a message

    # Fetch data based on the student's user ID
    student_data = get_student_data(current_user.User_ID)  # You need to implement this function

    return render_template('student_dashboard.html', student_data=student_data)

@app.route('/school_dashboard')
def school_dashboard():
    # Check if the current user is a school
    if current_user.Type != 'SCHOOL':
        abort(403)  # Forbidden, redirect to an error page or display a message


    conn = sql.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM SCHOOL')
    schools = cursor.fetchall()
 
    conn.close()

    return render_template('school_dashboard.html', users=schools)


def get_library_contents():
    # This function fetches all library items from the database
    # You may want to add additional filters or ordering based on your requirements
    return LibraryItem.query.all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def getUsers():
    return User.query.all()

class User(db.Model, UserMixin):
    User_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    Type = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_id(self):
        return str(self.User_ID)
