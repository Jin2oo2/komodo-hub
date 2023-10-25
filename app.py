from flask import Flask, request, render_template, url_for, abort

app = Flask(__name__)

@app.route('/')
def hello():
    registerURL = url_for('register')
    loginURL = url_for('login')
    return render_template('home.html', registerURL=registerURL, loginURL=loginURL)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

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