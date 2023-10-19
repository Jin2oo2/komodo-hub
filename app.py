from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask App</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '<h1>Log in page</h1>'
    