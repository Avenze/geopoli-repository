import json
import schedule
import time
import datetime
import os
from exch import getExchangeRatesUSD, getExchangeRatesEUR

def updateRates():
    with open('botnations.json', 'r') as f:
        data = json.load(f)
        usd_rates = getExchangeRatesUSD()
        eur_rates = getExchangeRatesEUR()
        if usd_rates == None or eur_rates == None:
            return
        for n in data['botnations']:
            if n['curr'] in usd_rates['rates'].keys():
                n['usd'] = usd_rates['rates'][n['curr']]
            if n['curr'] in eur_rates['rates'].keys():
                n['eur'] = eur_rates['rates'][n['curr']]
        f.close()
        with open('botnations-backup.json', 'w') as f:
            json.dump(data, f, indent=4)
        os.remove('botnations.json')
        with open('botnations.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(datetime.datetime.now(), '- Rates updated')

def recordRates():
    with open('dataRecord.json', 'r') as f:
        hist = json.load(f)
        usd_rates = getExchangeRatesUSD()
        eur_rates = getExchangeRatesEUR()
        hist['usd'].append(usd_rates)
        hist['eur'].append(eur_rates)
        with open('dataRecord-backup.json', 'w') as f:
            json.dump(hist, f, indent=4)
        os.remove('dataRecord.json')
        with open('dataRecord.json', 'w') as f:
            json.dump(hist, f, indent=4)
        print(datetime.datetime.now(), '- Rates recorded (.-.)')

schedule.every().minutes.do(updateRates)
schedule.every().day.at('00:00').do(recordRates) 

print('Running server')
while True: 
    schedule.run_pending()
    time.sleep(1)
