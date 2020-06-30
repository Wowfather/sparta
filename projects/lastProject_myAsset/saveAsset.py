import schedule

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

def run():
    schedule.every().day.at('08:00').do(dayAssetSaving) # 매일 08:00 마다 dayAssetSaving 함수를 실행
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    run()
