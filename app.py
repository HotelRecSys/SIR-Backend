import psycopg2
import json
from flask import Flask, jsonify, request, render_template,redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
import hashlib
from flask_cors import CORS,cross_origin
import os
import psycopg2 as dpapi

url = "dbname='jvncgqps' user='jvncgqps' host='suleiman.db.elephantsql.com' password='X3rc42rz2LZi0_lZK4B9i-m_OrumPo-d' "
app = Flask(__name__)
CORS(app)
app.secret_key = "sir"

@app.route('/')
def index():
    return "Hello, world!"

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
            print("dsdskjdhjdshjs")
            return {'error':'Invalid email or password!'}
    else :
        conn.close()
        return {'error':'Please try again!'}

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
    print(data)
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


@app.route('/logout', methods=['GET'])
def logout():
   conn = dpapi.connect(url)
   cursor = conn.cursor()

   if 'id' in session:
        session.pop('id')
   if 'email' in session:
        session.pop('email')

   conn.close()
   return {'success':'Succesfully log out!'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)