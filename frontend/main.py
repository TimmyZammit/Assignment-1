from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    response = requests.get('https://api-dot-assignment-1-v2.ew.r.appspot.com/generate')
    return response.json()
    

@app.route('/results')
def results():
    response = requests.get('https://api-dot-assignment-1-v2.ew.r.appspot.com/results')
    return response.json()

@app.route('/all_numbers')
def all_numbers():
    response = requests.get('https://api-dot-assignment-1-v2.ew.r.appspot.com/all_numbers')
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
