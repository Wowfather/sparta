from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import schedule
import time
import datetime

# dt = datetime.datetime.now()
# dtYear = dt.year
# dtMonth = dt.month
# dtDay = dt.day
# dtHour = dt.hour

#schedule.every().day.at("10:30").do(dayAssetSaving)

# while True: 
#     schedule.run_pending() 
#     time.sleep(1)

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')

# API 역할을 하는 부분

@app.route('/stock/list', methods=['GET'])
def stock_list():
    result = list(db.stocks.find({}))
    print(result)
    return dumps({'result': 'success', 'stocks': result})

# @app.route('/stock/nameStock', methods=['GET'])
# def stock_name():
#     data = list(db.stocks.find({ },{'_id': 0, 'nameStock':1}))
#     result = list(map(dict, set(tuple(sorted(d.items())) for d in data)))
#     print(result)
#     return jsonify({'result':'success', 'stocks' : result})


@app.route('/stock/list', methods=['POST'])
def write_stock():
    dateTrading = request.form['dateTrading_give']
    nameStock = request.form['nameStock_give']
    selectTrading = request.form['selectTrading_give']
    selectNation = request.form['selectNation_give']
    numStock = request.form['numStock_give']
    priceStock = request.form['priceStock_give']
    rateCurrency = request.form['rateCurrency_give']
    stock = {
        'dateTrading': dateTrading,
        'nameStock': nameStock,
        'selectTrading': selectTrading,
        'selectNation': selectNation,
        'numStock': numStock,
        'priceStock': priceStock,
        'rateCurrency': rateCurrency
    }

    db.stocks.insert_one(stock)
    return jsonify({'result': 'success', 'msg': '정상적으로 입력되었습니다.'})

@app.route('/stock/delete', methods=['POST'])
def stock_delete():
    idStock = request.form['id_give']
    db.stocks.delete_one({"_id": ObjectId(idStock)})
    return jsonify({'result': 'success', 'msg': '완료'})

# 회사명으로 주식 종목 코드를 획득할 수 있도록 하는 함수
def get_code(df, name):
    code = df.query("name=='{}'".format(name))['code'].to_string(index=False)
# 위와같이 code명을 가져오면 앞에 공백이 붙어있는 상황이 발생하여 앞뒤로 sript() 하여 공백 제거
    code = code.strip()
    return code

@app.route('/stock/nameStock', methods=['GET'])
def callprice_stock():
    nameStock = request.args.get('nameStock_give')
    # excel 파일을 다운로드하는거와 동시에 pandas에 load하기
    # 흔히 사용하는 df라는 변수는 data frame을 의미합니다.
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
    # data frame정리
    code_df = code_df[['회사명', '종목코드']]
    # data frame title 변경 '회사명' = name, 종목코드 = 'code'
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    # 종목코드는 6자리로 구분되기때문에 0을 채워 6자리로 변경
    code_df.code = code_df.code.map('{:06d}'.format)
    # ex) 삼성전자의의 코드를 구해보겠습니다.
    code = get_code(code_df, nameStock)
    # yahoo의 주식 데이터 종목은 코스피는 .KS, 코스닥은 .KQ가 붙습니다.
    # 삼성전자의 경우 코스피에 상장되어있기때문에 '종목코드.KS'로 처리하도록 한다.
    code = code + '.KS'
    print(code)
    # get_data_yahoo API를 통해서 yahho finance의 주식 종목 데이터를 가져온다.
    df = pdr.get_data_yahoo(code)
    print(df)
    # df = df.tail(1000)
    x = list(df.index)
    y = list(df.Close)
    return jsonify({'result': 'success', 'x': x, 'y': y})

def dayAssetSaving():
    dt = datetime.datetime.now()
    results = list(db.stocks.find({}))
    total = 0
    myAsset = 200000000
    for result in results:
        if result['selectTrading'] == '매수' or result['selectTrading'] == '배당':
            if result['selectNation'] == '국내':
                price = int(result['priceStock'])
                num = int(result['numStock'])
                total += price * num 
            else :
                price = int(result['priceStock'])
                num = int(result['numStock'])
                rate = int(result['rateCurrency'])
                total += price * num * rate            
    print(total)
    asset = {
        'date' : dt,
        'assetSum': total,
        'myAsset' : myAsset,
    }
    db.assetSum.insert_one(asset)

@app.route('/stock/assetAppend', methods=['GET'])
def assetAppend():
    results = list(db.assetSum.find({}))
    return jsonify({'result': 'success', 'myAsset' : result})

dayAssetSaving()    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    