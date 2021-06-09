#main.py
from flask import Flask, jsonify, request, url_for, redirect, render_template, send_file
import pymysql
import sqlalchemy
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import io
import datetime
import uuid
from random import seed
from random import random
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

seed(1)


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

#asddsasaddsasadsadasd
df = []
with db.connect() as conn:
     qry = "SELECT * FROM raw"
     results = conn.execute(qry).fetchall()
     for row in results:
            df.append(row)

data_raw = pd.DataFrame.from_records(df, columns = ['Order_ID', 'Size', 'Color', 'Order_Type', 'Detail_Divan', 'Buyer_ID', 'Order_Date', 'Finish_Date', 'Shipment_Date', 'Order_Detail', 'Price'])
data = data_raw.copy()
data["Order_Date"] = pd.to_datetime(data["Order_Date"])
data['Order_Date'] = data.Order_Date.dt.to_period('W').dt.to_timestamp()
week_agg = data.groupby(["Order_Date", "Order_Type"]).size().unstack("Order_Type")
week_agg = week_agg.fillna(0)

split = int(week_agg.shape[0]*0.8)
train, test = week_agg[:split], week_agg[split:]

scaler = MinMaxScaler()
train_scale = scaler.fit_transform(train)
test_scale = scaler.transform(test)

n_past = 4
n_future = 1 
n_features = 4

def split_series(series, n_past, n_future):
  X, y = list(), list()
  for window_start in range(len(series)):
    past_end = window_start + n_past
    future_end = past_end + n_future
    if future_end > len(series):
      break
    past, future = series[window_start:past_end, :], series[past_end:future_end, :]
    X.append(past)
    y.append(future)
  return np.array(X), np.array(y)

X_train, y_train = split_series(train_scale,n_past, n_future)
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], n_features))
y_train = y_train.reshape((y_train.shape[0], y_train.shape[1], n_features))
X_test, y_test = split_series(test_scale,n_past, n_future)
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], n_features))
y_test = y_test.reshape((y_test.shape[0], y_test.shape[1], n_features))

tf.keras.backend.clear_session()

encoder_inputs = tf.keras.layers.Input(shape=(n_past, n_features))
encoder_l1 = tf.keras.layers.LSTM(64, return_state=True)
encoder_outputs1 = encoder_l1(encoder_inputs)
encoder_states1 = encoder_outputs1[1:]
decoder_inputs = tf.keras.layers.RepeatVector(n_future)(encoder_outputs1[0])
decoder_l1 = tf.keras.layers.LSTM(64, return_sequences=True)(decoder_inputs,initial_state = encoder_states1)
decoder_outputs1 = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(n_features))(decoder_l1)

model = tf.keras.models.Model(encoder_inputs,decoder_outputs1)

reduce_lr = tf.keras.callbacks.LearningRateScheduler(lambda x: 1e-3 * 0.90 ** x)
model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.Huber())

history = model.fit(X_train,y_train,
                            epochs=100,
                            validation_data=(X_test,y_test),
                            verbose=1,
                            callbacks=[reduce_lr])

X = week_agg.iloc[-4:,:]
X = scaler.transform(X)
X = np.reshape(X, (1,4,4))

forecast = model.predict(X)
forecast = np.round(scaler.inverse_transform(np.reshape(forecast, (1,4))),0)
type1 = np.int(forecast[0][0])
type2 = np.int(forecast[0][1])
type3 = np.int(forecast[0][2])
type4 = np.int(forecast[0][3])
#sadsdasadsdasaddsadas

@app.route('/')
def landing_page():     
    return render_template('index.html')

@app.route('/login/information')
def information_page():
    reverse_shipment = data_shipment.iloc[::-1]
    reverse_order = data_order.iloc[::-1]
    print(forecast)
    return render_template('information.html', tables=[reverse_shipment.to_html(classes='', index=False)], titles=reverse_shipment.columns.values, tables2 = [reverse_order.to_html(classes='', index=False)], titles2=reverse_order.columns.values, tipe1 = type1, tipe2=type2,tipe3=type3,tipe4=type4)    

@app.route('/login/success',methods=['POST'])
def success_page():     
    input_data = [i for i in request.form.values()]
    order_id = random()
    size = input_data[0]
    color = input_data[1]
    order_type = input_data[2]
    detail_divan = input_data[3]
    buyer_id = 2
    order_date = datetime.datetime.now()
    order_date = str(order_date)
    order_date = order_date[0:10]
    finish_date = input_data[4][0:10]
    shipment_date = datetime.datetime.now()+datetime.timedelta(days=7)
    shipment_date = str(shipment_date)
    shipment_date = shipment_date[0:10]
    order_detail = str(order_type)+" "+str(detail_divan)+" "+str(size)+" "+str(color)
    print(order_id)
    order_status = "BELUM"
    with db.connect() as conn:
        qry = "INSERT INTO raw (Order_ID, Size, Color, Order_Type, Detail_Divan, Buyer_ID, Order_Date, Finish_Date, Shipment_Date, Order_Detail, Price) VALUES (order_id, size, color, order_type, detail_divan, buyer_id, order_date, finish_date, shipment_date, order_detail, 1000000);"
        conn.execute(qry)
        return render_template('success.html')

@app.route('/plot.png')
def plot_page():
    bytes_obj = save_plot()
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')  
    # return render_template('owner.html', plot = bytes_obj) 

@app.route('/login',methods=['POST', 'GET'])
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

@app.route('/login/dashboard')
def login_dashboard():     
    return render_template('owner.html')

if __name__ == '__main__':
    app.run(debug=True)