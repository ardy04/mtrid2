#main.py
from flask import Flask, jsonify, request, url_for, redirect, render_template, send_file
import pymysql
import sqlalchemy
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import uuid


app = Flask(__name__, template_folder="templates")
db_user = 'my-sql-instance'
db_password = 'intense-agency-314911'
db_name = 'db_raw'
db_connection_name = 'intense-agency-314911:asia-southeast2:my-sql-instance'


def open_connection():
    import sqlalchemy
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

def login_db():
    with db.connect() as conn:
        qry = "SELECT * FROM login"
        results = conn.execute(qry).fetchall()
    return results

details_db = []
order_db = []
shipments_db = []
with db.connect() as conn:
    qry_details = "SELECT * FROM details"
    qry_order = "SELECT * FROM orderr"
    qry_shipment = "SELECT * FROM shipment"
    results_details = conn.execute(qry_details).fetchall()
    results_order = conn.execute(qry_order).fetchall()
    results_shipment = conn.execute(qry_shipment).fetchall()
    for row in results_details:
        details_db.append(row)
    for row in results_order:
        order_db.append(row)
    for row in results_shipment:
        shipments_db.append(row)


data_product = pd.DataFrame.from_records(details_db, columns = ["Order_ID", "Size", "Color", "Order", "Detail_Divan"])
data_order = pd.DataFrame.from_records(order_db, columns = ["Order_ID", "Order_Date", "Order_Detail", "Order_Status", "Order_Deadline"])
data_shipment = pd.DataFrame.from_records(shipments_db, columns = ["Order_ID", "Shipment_Date", "Shipment_Detail", "Finish_Date"])


data_product["Detail_Divan"] = data_product["Detail_Divan"].str.replace(r'\r', "")
data_order["Order_Date"] = pd.to_datetime(data_order["Order_Date"])
joined = data_product.set_index("Order_ID").combine_first(data_order.set_index("Order_ID")).reset_index()
joined_week = joined.copy()
joined_week["Order_Date"] = joined.Order_Date.dt.to_period('W').dt.to_timestamp()
fixed_date = pd.Series(pd.to_datetime("2019-11-12")).dt.to_period("W").dt.to_timestamp()
for_plot_week = joined_week[joined_week.Order_Date.isin(fixed_date)].groupby("Order").size()

names_week = for_plot_week.reset_index().iloc[:, 0]
size_week = for_plot_week.reset_index().iloc[:, 1]

img = io.BytesIO()
def myplot(x, y, title):
    fig = plt.figure()
    
    my_circle = plt.Circle( (0,0), 0.7, color='white')
    plt.pie(y, labels=x, wedgeprops = {'linewidth' : 7, 'edgecolor' : 'white' })
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    if title:
        plt.title(title, figure = fig)
    
    return fig


def save_plot():
    bytes_image = io.BytesIO()
    myplot(names_week, size_week, "Pie Chart") 
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image

@app.route('/')
def landing_page():     
    return render_template('owner.html')

@app.route('/information')
def information_page():
    reverse_shipment = data_shipment.iloc[::-1]
    reverse_order = data_order.iloc[::-1]
    return render_template('information.html', tables=[reverse_shipment.to_html(classes='', index=False)], titles=reverse_shipment.columns.values, tables2 = [reverse_order.to_html(classes='', index=False)], titles2=reverse_order.columns.values)    

@app.route('/success',methods=['POST'])
def success_page():     
    input_data = [i for i in request.form.values()]
    order_id = uuid.uuid1()
    order_date = datetime.date(datetime.now())
    order_detail = input_data[0]
    order_status = "BELUM"
    order_deadline = input_data[1][0:10]
    with db.connect() as conn:
        qry = "INSERT INTO orderr (Order_ID, Order_Date, Order_Detail, Order_Status, Order_Deadline) VALUES (order_id, order_date, order_detail, order_status, order_deadline);"
        conn.execute(qry)
    print(order_id, order_date, order_detail, order_status, order_deadline, "SUCCESSSSS")
    return render_template('success.html')

@app.route('/plot.png')
def plot_page():
    bytes_obj = save_plot()
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')  
    # return render_template('owner.html', plot = bytes_obj) 

@app.route('/login',methods=['POST'])
def prediksi():
    input_data = [i for i in request.form.values()]
    id = input_data[0]
    password = input_data[1]
    db = open_connection()
    
    with db.connect() as conn:
        qry = "SELECT * FROM login WHERE email = '{}' AND password = '{}'".format(id, password)
        results = conn.execute(qry).fetchall()
        print(results)
        if not results:
            return("Anda belum terdaftar")
        if results[0][4][0] == "m":
            return render_template('owner.html')
        elif results[0][4][0] == "e":
            return render_template('employee.html')

if __name__ == '__main__':
    app.run(debug=True)