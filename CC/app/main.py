#main.py
import os
from flask import Flask, jsonify, request
import pymysql


app = Flask(__name__)
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password,
                                unix_socket=unix_socket, db=db_name,
                                cursorclass=pymysql.cursors.DictCursor
                                )
    except pymysql.MySQLError as e:
        print(e)

    return conn


db = open_connection()

# @app.route('/', methods=["POST", "GET"])
# def home():
#     data = []
#     if request.method == "GET":
#         with db.connect() as conn:
#             qry = "SELECT * FROM login"
#             results = conn.execute(qry).fetchall()
#             columns = ["ID","Email", "Nama", "Password", "Role"]
#             for i in results:
#                 data.append(dict(zip(columns,i)))
#         return jsonify(data)
#     elif request.method == "POST":
#         new_post = request.get_json()
#         print(new_post)
#         return "Jeasd"

@app.route('/login', methods=["GET"])
def login():
    data = []
    with db.connect() as conn:
        qry = "SELECT * FROM login"
        results = conn.execute(qry).fetchall()
        columns = ["ID","Email", "Nama", "Password", "Role"]
        for i in results:
            data.append(dict(zip(columns,i)))
    return jsonify(data)

# @app.route('/raw', methods=["POST"])
# def home_2():
#     new_post = request.form["nama"]
#     print(new_post)
#     return "Jeasd"

@app.route('/raw', methods=["GET"])
def raw():
    data = []
    with db.connect() as conn:
        qry = "SELECT * FROM raw"
        results = conn.execute(qry).fetchall()
        columns = ["Order_ID","Size", "Color", "Order_Type", "Detail_Divaan", "Buyer_ID", "Order_Date", "Finish_Date", "Shipment_Date", "Order_Detail", "Price"]
        for i in results:
            data.append(dict(zip(columns,i)))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True) 