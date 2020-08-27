from flask import Flask, render_template, request, session, abort, flash, redirect, url_for
import sys, os
from flask_mysqldb import MySQL
import re 
import yaml
import requests
import cv2
import numpy as np
import time
import datetime as dt
from src import align, difference, util

app = Flask(__name__)

regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

url = "http://192.168.43.1:8080/shot.jpg"

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

app.config['SECRET_KEY'] = '5d8ea3a2c51c144d49f0ee95b2bf50bd'

app.add_url_rule('/images/<path:filename>', endpoint='images', view_func=app.send_static_file)

def check(email):   
    if(re.search(regex,email)):  
        return True 
    else:  
        return False

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def capture():
    while True:
        time.sleep(10)
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype = np.uint8)
        img = cv2.imdecode(img_arr, -1)

        if cv2.waitKey(1) == 27:
            break

def resize(img, maximum_small_edge=500):
	h = img.shape[0]
	w = img.shape[1]
	small_edge = h if h < w else w

	# If the image is already 500px or smaller on the shorter edge
	if small_edge <= maximum_small_edge:
		return img

	scale_ratio = 1 / (small_edge*1.0 / maximum_small_edge)
	return cv2.resize(img, (0,0), fx=scale_ratio, fy=scale_ratio)

def check(img1, img2, show_images=0):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/products')
def show():
    cur = mysql.connection.cursor()
    cur.execute("select * from pdetails")
    data = cur.fetchall()
    return render_template('show_products.html', data = data)
    
@app.route('/add_products', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        pDetails = request.form
        pname = pDetails['product']
        pimage = pDetails['upload']
        cur = mysql.connection.cursor()
        cur.execute("insert into pdetails values(%s, %s)", (pname, pimage))
        cur.close()
        mysql.connection.commit()
        flash(f'Details inserted for {pname}!', 'success')
    return render_template('add_products.html')

@app.route('/inspect', methods=['GET', 'POST'])
def inspect():    
    if request.method == 'POST':
        pDetails = request.form
        pname = pDetails['product']
        cur = mysql.connection.cursor()
        count = cur.execute("select * from pdetails where pname = %s", [pname])
        record = cur.fetchall()
        cur.close()
        if count == 0:
                flash('Product name is wrong!', 'alert')
        else:
            flash(f'Item selected successfully!', 'success')
            img_name = "images/" + record[0][1]

            img1 = cv2.imread(img_name)
            cur = mysql.connection.cursor()
            count = cur.execute("select * from pstats where pname = %s and pdate = %s", ([pname], dt.date.today().strftime("%Y-%m-%d")))
            record = cur.fetchall()
            cur.close()
            if len(record) == 0:
                flag = 0
            else:
                flag = 1
            while True:
                cur = mysql.connection.cursor()
                time.sleep(5)
                img_resp = requests.get(url)
                img_arr = np.array(bytearray(img_resp.content), dtype = np.uint8)
                img2 = cv2.imdecode(img_arr, -1)
                cv2.imshow('image2', img2)
                val = check(img1, img2)
                if val >= 150:
                    if flag == 0:
                        cur.execute("insert into pstats(pname, pdate, passed, failed) values(%s, %s, %s, %s)", ([pname], dt.date.today().strftime("%Y-%m-%d"), 1, 0))
                        cur.execute("select * from pstats where pname = %s and pdate = now()", [pname])
                        record = cur.fetchall()
                        flash(f'Pass! { len(record) }', 'success')
                        flag = 1
                    else:
                        cur.execute("update pstats set passed = passed + %s where pname = %s and pdate = %s", (1, [pname], dt.date.today().strftime("%Y-%m-%d")))
                        flash('Pass!', 'success')

                else:
                    if flag == 0:
                        cur.execute("insert into pstats(pname, pdate, passed, failed) values(%s, %s, %s, %s)", ([pname], dt.date.today().strftime("%Y-%m-%d"), 0, 1))
                        cur.execute("select * from pstats where pname = %s and pdate = now()", [pname])
                        record = cur.fetchall()
                        flash(f'Fail! { len(record) }', 'alert')
                        flag = 1
                    else:
                        cur.execute("update pstats set failed = failed + %s where pname = %s and pdate = %s", (1, [pname], dt.date.today().strftime("%Y-%m-%d")))
                        flash('Fail!', 'alert')
                cur.close()
                mysql.connection.commit()
                if cv2.waitKey(1) == 27:
                    break
            cv2.destroyAllWindows()
    return render_template('inspection.html')
    
    
    
@app.route('/statistics', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        pDetails = request.form
        pname = pDetails['product']
        cur = mysql.connection.cursor()
        count = cur.execute("select * from pdetails where pname = %s", [pname])
        record = cur.fetchall()
        cur.close()
        if count == 0:
                flash('Product name is wrong!', 'alert')
        else:
            flash(f'Item selected successfully!', 'success')
            cur = mysql.connection.cursor()
            cur.execute("select * from pstats where pname = %s", [pname])
            data = cur.fetchall()
            return render_template('stats.html', data = data)
    return render_template('statistics.html')
    
    
@app.route('/help')
def help():
    return render_template('manual.html')



if __name__ == '__main__':
    app.run(debug=True)