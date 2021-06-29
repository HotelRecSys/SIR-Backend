import json
from flask import Flask, jsonify, request, session
import hashlib
from flask_cors import CORS
import psycopg2 as dpapi
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

url = ""

app = Flask(__name__)
CORS(app)
app.secret_key = "sir"

prop_df = pd.read_csv("real_embedding.csv")
item_id = prop_df['item_id'].values
id_to_index = {item_id: idx for idx, item_id in enumerate(item_id)}
index_to_id = {idx: item_id for item_id, idx in id_to_index.items()}

model = load_model('lstm_predict.h5')

@app.route('/login', methods=['POST', 'GET'])
def login():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    data = json.loads(request.data)
    email = data['email']
    password = data['password']

    if email and password:
        # if request.form.get("forgotPassword"):
        #    return render_template("index.html")
        cursor.execute("SELECT * FROM person WHERE email=%s AND password=%s",
                       (email, hashlib.md5(password.encode('utf-8')).hexdigest()))
        user = cursor.fetchone()

        if user:
            user_data = {"id": user[0], "name": user[1], "password": user[3], "email": user[2], "country": user[4],
                         "image": user[5], "impressions": user[6]}
            session["email"] = email
            session["id"] = user[0]
            response = jsonify(user_data)
            conn.close()
            return response
        else:
            return jsonify(message="User with that email or password do not exist"), 404
    else:
        conn.close()
        return jsonify(message='Please try again!'), 404


@app.route('/register', methods=['POST'])
def register():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)
    name = data['name']
    email = data['email']
    password = data['password']
    country = data['country']
    image = data['image']
    impression = ''
    if name and email and password and country:
        # if request.form.get("forgotPassword"):
        #    return render_template("index.html")
        cursor.execute(
            "INSERT INTO person(name, password, email, country, image, impressions) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, hashlib.md5(password.encode('utf-8')).hexdigest(), email, country, image, impression))
        conn.commit()
        conn.close()

        return {'success': 'Succesfully registerated!'}
    else:
        conn.close()
        return {'error': 'Please try again!'}


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    conn = dpapi.connect(url)

    if 'id' in session:
        session.pop('id')
    if 'email' in session:
        session.pop('email')

    conn.close()
    return {'success': 'Succesfully log out!'}


@app.route('/country-filter', methods=['GET', 'POST'])
def countryFilter():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)
    country = data['country']
    page = data['page']
    otelList = []

    if country:
        cursor.execute('SELECT * FROM otel WHERE country=%s ORDER BY item_id DESC LIMIT %s OFFSET %s',
                       (country, 10, 10 * page,))
        otels = cursor.fetchall()

        for otel in otels:
            array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4],
                     "address": otel[5], "img": otel[6], "properties": otel[7]}
            otelList.append(array)

        response = jsonify(otelList)
        conn.close()
        return response
    else:
        conn.close()
        return {'error': 'No country!'}


@app.route('/top-ten', methods=['GET', 'POST'])
def topHotels():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM otel WHERE score = (SELECT MAX(score) FROM otel) ORDER BY item_id ASC LIMIT 10')
    topOtels = cursor.fetchall()
    otelList = []
    for otel in topOtels:
        array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4],
                 "address": otel[5], "img": otel[6], "properties": otel[7]}
        otelList.append(array)

    response = jsonify(otelList)
    conn.close()
    return response


@app.route('/search', methods=['GET', 'POST'])
def search():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)
    print(data)
    name = data['otelName']

    if name:
        cursor.execute('SELECT * FROM otel WHERE name LIKE %s', ("%" + name + "%",))
        searchedOtel = cursor.fetchall()
        otelList = []
        for otel in searchedOtel:
            array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4],
                     "address": otel[5], "img": otel[6], "properties": otel[7]}
            otelList.append(array)

        response = jsonify(otelList)
        conn.close()
        return response


@app.route('/filter', methods=['GET', 'POST'])
def filter():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)
    score = data['score']
    properties = data['properties']
    city = data['city']
    ids = []
    ids_copy = []
    print(data)
    if score and city and properties:
        cursor.execute('SELECT item_id FROM otel WHERE score = %s AND city = %s', (score, city,))
        ids = cursor.fetchall()
        ids = [i[0] for i in ids]
        if ids:
            for idx in ids:
                count = 0
                for prop in properties:
                    if list(prop_df[prop][prop_df['item_id'] == idx])[0] == 1:
                        count += 1
                if count == len(properties):
                    ids_copy.append(idx)
        if ids_copy:
            t = tuple(ids_copy)
            cursor.execute("SELECT * FROM otel WHERE item_id IN {}".format(t))
            filtered = cursor.fetchall()

            otelList = []
            for otel in filtered:
                array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4],
                         "address": otel[5], "img": otel[6], "properties": otel[7]}
                otelList.append(array)

            response = jsonify(otelList)
            conn.close()
            return response

        else:
            return {'error': 'No Hotel!'}
    else:
        return {'error': 'No Hotel!'}


@app.route('/clickout', methods=['GET', 'POST'])
def clickout():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)

    user_id = data['user_id']
    item_id = data['item_id']

    otelList = []

    if user_id:
        cursor.execute("SELECT impressions FROM person WHERE personid = %s", (user_id,))
        impression = cursor.fetchone()

        if item_id > 0:
            impression = impression[0]
            if impression == '':
                impression += str(item_id)
            else:
                impression += '|' + str(item_id)

            impression_list = impression.split('|')

            if len(impression_list) > 25:
                impression = ''
                del impression_list[0]
                impression += impression_list[0]
                for i in range(1,len(impression_list)):
                    impression += '|' + impression_list[i]

            cursor.execute("UPDATE person SET impressions = %s WHERE personid = %s", (impression, user_id))
            conn.commit()

        else:
            impression = impression[0]
            if impression is not None:
                impression_list = impression.split('|')
            else:
                return {'error': 'no predicted hotels'}

        if len(impression_list) >= 3:
            imp = [int(i) for i in impression_list]
            imp = [id_to_index[i] for i in imp]
            imp = np.asarray(imp)
            temp_pred = model.predict(imp.reshape(-1, len(imp)))
            temp_pred = temp_pred.reshape(-1)
            predict = temp_pred.argsort()[-20:][::-1].tolist()

            predict = [index_to_id[i] for i in predict]
            t = tuple(predict)

            cursor.execute('SELECT * FROM otel WHERE item_id IN {}'.format(t))
            predict_otels = cursor.fetchall()

            for otel in predict_otels:
                array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4],
                         "address": otel[5], "img": otel[6], "properties": otel[7]}
                otelList.append(array)


            response = jsonify(otelList)
            conn.close()
            return response

        return {'error': 'no predicted hotels'}

    else:
        return []

@app.route('/update', methods=['GET', 'POST'])
def update():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)

    name = data['name']
    password = data['password']
    user_id = data['user_id']
    print(name, password, user_id)

    if name != '':
        cursor.execute("UPDATE person SET name = %s WHERE personid = %s", (name, user_id))
        conn.commit()

    if password != '':
        cursor.execute("UPDATE person SET password = %s WHERE personid = %s", (hashlib.md5(password.encode('utf-8')).hexdigest(), user_id))
        conn.commit()

    conn.close()
    return {'success': 'Changed'}



@app.route('/')
def index():
    return "bittik gg"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
