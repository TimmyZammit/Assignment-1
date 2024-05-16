from flask import Flask, jsonify
import random
from google.cloud.sql.connector import Connector
from flask_cors import CORS
import requests

import sqlalchemy

app = Flask(__name__)
CORS(app)

# Cloud SQL setup
connector = Connector()
connection = connector.connect(
    "assignment-1-v2:europe-west1:num-storage",
    "pymysql",
    user="root",
    password="Kozhikode2003!",
    db="num-db"
)

def get_instance_id():
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/id"
    headers = {
        "Metadata-Flavor": "Google"
    }
    try:
        response = requests.get(metadata_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching instance ID: {e}")
        return None


@app.route('/generate', methods=['GET'])
def generate():
    num = random.randint(0, 100000)
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO numbers (instance_id, number) VALUES (%s, %s)", 
            (get_instance_id(), num)
        )
    connection.commit()

@app.route('/results', methods=['GET'])
def results():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(number), MIN(number) FROM numbers")
        result = cursor.fetchone()
    return jsonify({"max_number": result[0], "min_number": result[1]})

@app.route('/all_numbers', methods=['GET'])
def all_numbers():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM numbers")
        results = cursor.fetchall()
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
