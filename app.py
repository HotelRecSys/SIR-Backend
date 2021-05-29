
import json
from flask import Flask, jsonify, request, session
import hashlib
from flask_cors import CORS
import psycopg2 as dpapi

url = "dbname='sir' user='postgres' host='localhost' port='5432' password='54321' "
app = Flask(__name__)
CORS(app)
app.secret_key = "sir"


@app.route('/')
def index():
    return "Hello,Rümü!"


@app.route('/login', methods=['POST', 'GET'])
def login():

    conn = dpapi.connect(url)
    cursor = conn.cursor()
    data = json.loads(request.data)
    email = data['email']
    password = data['password']

    if email and password:
        #if request.form.get("forgotPassword"):
        #    return render_template("index.html")
        cursor.execute("SELECT * FROM person WHERE email=%s AND password=%s",(email,hashlib.md5(password.encode('utf-8')).hexdigest()))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["email"]= email
            session["id"] = user[0]
            response = jsonify(user)
            return response
        else:
            return jsonify(message="User with that email or password do not exist"), 404
    else :
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

    if name and email and password and country:
        #if request.form.get("forgotPassword"):
        #    return render_template("index.html")
        cursor.execute("INSERT INTO person(name, password, email, country, image) VALUES (%s, %s, %s, %s, %s)",(name, hashlib.md5(password.encode('utf-8')).hexdigest(), email, country, image))
        conn.commit()
        conn.close()

        return {'success':'Succesfully registerated!'}
    else :
        conn.close()
        return {'error':'Please try again!'}


@app.route('/logout', methods=['GET', 'POST'])
def logout():
   conn = dpapi.connect(url)

   if 'id' in session:
        session.pop('id')
   if 'email' in session:
        session.pop('email')

   conn.close()
   return {'success':'Succesfully log out!'}


@app.route('/country-filter', methods=['GET', 'POST'])
def countryFilter():
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    data = json.loads(request.data)
    country = data['country']
    page = data['page']
    otelList = []
    print(page)
    if country:
        cursor.execute('SELECT * FROM otel WHERE country=%s ORDER BY item_id DESC LIMIT %s OFFSET %s', (country, 10, 10*page,))
        otels = cursor.fetchall()

        for otel in otels:
            array = {"item_id": otel[0], "name": otel[1], "score": otel[2], "city": otel[3], "country": otel[4], "address": otel[5], "img": otel[6], "properties": otel[7]}
            otelList.append(array)


        response = jsonify(otelList)
        conn.close()
        return response
    else:
        conn.close()
        return {'error': 'No country!'}


if __name__ == "__main__":
    app.run(debug=True)
