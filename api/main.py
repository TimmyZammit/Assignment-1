from flask import Flask, jsonify
import time
import random
import sqlalchemy
from google.cloud.sql.connector import Connector
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

connector = Connector()

def getconn():
    conn = connector.connect(
        "assignment-1-v2:europe-west1:num-storage",
        "pymysql",
        user="root",
        password="Kozhikode2003!",
        db="num-db"
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)
print("sql config done")

@app.route('/')
def home():
    return jsonify({"message": "test"})

@app.route('/generate')
def generate_random_number():
    print("generating number")
    number = random.randint(1, 100000)
    instance_id = os.getenv('GAE_INSTANCE', 'default_instance')
    insert_query = sqlalchemy.text("INSERT INTO numbers (instance_id,number) VALUES (:instance_id,:number)")
    try:
        with pool.connect() as db_connection:
            db_connection.execute(insert_query, {'instance_id': instance_id, 'number': number})
            db_connection.commit()
            time.sleep(0.1)
        return jsonify({"message": "OK", "number": number}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def instance_summary():
    query = sqlalchemy.text("""
        SELECT instance_name, COUNT(*) as count
        FROM generated_numbers
        GROUP BY instance_name
    """)
    with pool.connect() as db_connection:
        result = db_connection.execute(query)
        summary = [{"instance_name": row[0], "count": row[1]} for row in result]
    return jsonify(summary)

@app.route('/all_numbers')
def extreme_numbers():
    min_query = sqlalchemy.text("SELECT number, instance_name FROM generated_numbers ORDER BY number ASC LIMIT 1")
    max_query = sqlalchemy.text("SELECT number, instance_name FROM generated_numbers ORDER BY number DESC LIMIT 1")
    with pool.connect() as db_connection:
        min_result = db_connection.execute(min_query).fetchone()
        max_result = db_connection.execute(max_query).fetchone()

    return jsonify({
        "min": {"number": min_result[0], "instance_name": min_result[1]},
        "max": {"number": max_result[0], "instance_name": max_result[1]},
    })

@app.route('/restart', methods=['GET'])
def restart():
    print("restart called")
    query = sqlalchemy.text("TRUNCATE TABLE generated_numbers")
    with pool.connect() as db_connection:
        db_connection.execute(query)
        db_connection.commit()
    return jsonify({"message": "Table reset successful."})

if __name__ == '_main_':
    app.run(host='0.0.0.0', port = 8080)