#main.py
from flask import Flask, jsonify, request
import sqlalchemy
import datetime as dt
import io
from datetime import datetime
import uuid


app = Flask(__name__, template_folder="templates")
db_user = 'my-sql-instance'
db_password = 'intense-agency-314911'
db_name = 'db_raw'
db_connection_name = 'intense-agency-314911:asia-southeast2:my-sql-instance'


def open_connection():
    db = sqlalchemy.create_engine(
         sqlalchemy.engine.url.URL(
          drivername="mysql+pymysql",
          username="root",
          password="intense-agency-314911", 
          host="34.101.233.26", 
          database="db_raw"
        )
    )
    return db 

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