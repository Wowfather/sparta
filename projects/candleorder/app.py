from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta                      # 'dbsparta'라는 이름의 db를 만듭니다.

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')

@app.route('/memo', methods=['GET'])
def listing():
    # 모든 document 찾기 & _id 값은 출력에서 제외하기
    result = list(db.inf_order.find({},{'_id':0}))
    # inf_order라는 키 값으로 영화정보 내려주기
    return jsonify({'result':'success', 'inf_order':result})

## API 역할을 하는 부분
@app.route('/memo', methods=['POST'])
def saving():
		# 클라이언트로부터 데이터를 받는 부분
    username_receive = request.form['username_give']
    Quantity_receive = request.form['Quantity_give']
    address_receive = request.form['address_give']
    phonenumber_receive = request.form['phonenumber_give']

    print (username_receive)

		# mongoDB에 넣는 부분
    inf_order = {'username': username_receive, 'Quantity': Quantity_receive, 'address': address_receive,
               'phonenumber': phonenumber_receive}

    print (inf_order)
    db.inf_order.insert_one(inf_order)

    return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)