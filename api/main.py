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
        "assignment-1-424613:europe-west1:num-storage",
        "pymysql",
        user="root",
        password="Kozhikode2003!",
        db="num-db"
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
    pool_size=1,         # The number of connections to maintain in the pool
    max_overflow=0,       # The number of additional connections allowed beyond pool_size
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

@app.route('/all_numbers')
def list_all_numbers():
    query = sqlalchemy.text("SELECT instance_id, number FROM numbers")
    with pool.connect() as db_connection:
        result = db_connection.execute(query)
        numbers_list = [{"instance_id": row[0], "number": row[1]} for row in result]
    return jsonify(numbers_list)


@app.route('/results')
def extreme_numbers():
    min_query = sqlalchemy.text("SELECT number, instance_id FROM numbers ORDER BY number ASC LIMIT 1")
    max_query = sqlalchemy.text("SELECT number, instance_id FROM numbers ORDER BY number DESC LIMIT 1")
    with pool.connect() as db_connection:
        min_result = db_connection.execute(min_query).fetchone()
        max_result = db_connection.execute(max_query).fetchone()

    return jsonify({
        "min": {"number": min_result[0], "instance_id": min_result[1]},
        "max": {"number": max_result[0], "instance_id": max_result[1]},
    })

if __name__ == '_main_':
    app.run(host='0.0.0.0', port = 8080)