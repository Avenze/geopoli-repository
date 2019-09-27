import json
import schedule
import time
import datetime
import os
from matplotlib import pyplot as plt
import pandas as pd
from imports.api.exch import getExchangeRatesUSD, getExchangeRatesEUR

def updateRates():
    with open('data/botnations.json', 'r') as f:
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
        for filename in os.listdir('game'):
            if filename.endswith('.json') and 'data' in filename:
                with open('game/'+filename, 'r') as f:
                    gamedata = json.load(f)
                    for n in range(len(gamedata['nations'])):
                        for bot in data['botnations']:
                            if gamedata['nations'][n]['iso'] == bot['iso']:
                                gamedata['nations'][n]['usd'] = bot['usd']
                                gamedata['nations'][n]['eur'] = bot['eur']
                with open('game/'+filename, 'w') as f:
                    json.dump(gamedata, f, indent=4)
        with open('data/botnations-backup.json', 'w') as f:
            json.dump(data, f, indent=4)
        os.remove('data/botnations.json')
        with open('data/botnations.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(datetime.datetime.now(), '- Rates updated')

def recordRates():
    with open('data/dataRecord.json', 'r') as f:
        hist = json.load(f)
        usd_rates = getExchangeRatesUSD()
        usd_rates['usd'] = 1
        eur_rates = getExchangeRatesEUR()
        eur_rates['eur'] = 1
        hist['usd'].append(usd_rates)
        hist['eur'].append(eur_rates)

        usd_rate_dict = {
            'CNY':[], 'RUB':[], 'MXN':[], 'TRY':[], 'EUR':[], 'INR':[], 'GBP':[], 
            'KRW':[], 'BRL':[], 'ZAR':[], 'AUD':[], 'JPY':[], 'CAD':[], 'IDR':[]
        }
        eur_rate_dict = {
            'CNY':[], 'RUB':[], 'MXN':[], 'TRY':[], 'USD':[], 'INR':[], 'GBP':[], 
            'KRW':[], 'BRL':[], 'ZAR':[], 'AUD':[], 'JPY':[], 'CAD':[], 'IDR':[]
        }

        for i in range(len(hist['usd'])):
            for r in range(len(hist['usd'][i]['rates'])):
                rate = hist['usd'][i]['rates']
                usd_rate_dict[list(rate.keys())[r]].append(rate[list(rate.keys())[r]])
        
        for i in range(len(hist['eur'])):
            for r in range(len(hist['eur'][i]['rates'])):
                rate = hist['eur'][i]['rates']
                eur_rate_dict[list(rate.keys())[r]].append(rate[list(rate.keys())[r]])
        
        dfs = [
            pd.DataFrame({
                'x': range(0, len(usd_rate_dict['CNY'])),
                'CNY': usd_rate_dict['CNY'], 'RUB': usd_rate_dict['RUB'], 'MXN': usd_rate_dict['MXN'], 
                'TRY': usd_rate_dict['TRY'], 'EUR': usd_rate_dict['EUR'], 'INR': usd_rate_dict['INR'], 
                'GBP': usd_rate_dict['GBP'], 'KRW': usd_rate_dict['KRW'], 'BRL': usd_rate_dict['BRL']
            }),
            pd.DataFrame({
                'x': range(0, len(usd_rate_dict['ZAR'])),
                'ZAR': usd_rate_dict['ZAR'], 'AUD': usd_rate_dict['AUD'], 'JPY': usd_rate_dict['JPY'], 
                'CAD': usd_rate_dict['CAD'], 'IDR':usd_rate_dict['IDR'] 
            }), 
            pd.DataFrame({
                'x': range(0, len(eur_rate_dict['CNY'])), 
                'CNY': eur_rate_dict['CNY'], 'RUB': eur_rate_dict['RUB'], 'MXN': eur_rate_dict['MXN'], 
                'TRY': eur_rate_dict['TRY'], 'USD': eur_rate_dict['USD'], 'INR': eur_rate_dict['INR'], 
                'GBP': eur_rate_dict['GBP'], 'KRW': eur_rate_dict['KRW'], 'BRL': eur_rate_dict['BRL']
            }),
            pd.DataFrame({
                'x': range(0, len(eur_rate_dict['ZAR'])), 
                'ZAR': eur_rate_dict['ZAR'], 'AUD': eur_rate_dict['AUD'], 'JPY': eur_rate_dict['JPY'], 
                'CAD': eur_rate_dict['CAD'], 'IDR':eur_rate_dict['IDR'] 
            }), 
        ]

        bases = ['USD', 'USD', 'EUR', 'EUR']
        i = 0

        for df in dfs:
            plt.style.use('seaborn-darkgrid')
            palette = plt.get_cmap('Set1')
            
            num=0
            for column in df.drop('x', axis=1):
                num+=1
            
                plt.subplot(3,3, num)
            
                plt.plot(df['x'], df[column], marker='', color=palette(num), linewidth=1.9, alpha=0.9, label=column)
            
                plt.title(column, loc='left', fontsize=12, fontweight=0, color='black')

                plt.xlabel('Time (Days)')
                plt.ylabel('Rate')

            plt.suptitle('Currency exchange rates ('+bases[i]+')', fontsize=13, fontweight=0, color='black', style='italic', y=1.02)

            if os.path.exists('resources/img/rates'+str(i)+'.png'):
                os.remove('resources/img/rates'+str(i)+'.png')
            plt.savefig('resources/img/rates'+str(i)+'.png')
            i += 1

            plt.close()

        f.close()
        with open('data/dataRecord-backup.json', 'w') as f:
            json.dump(hist, f, indent=4)
        os.remove('data/dataRecord.json')
        with open('data/dataRecord.json', 'w') as f:
            json.dump(hist, f, indent=4)
        print(datetime.datetime.now(), '- Rates recorded (.-.)')

schedule.every().minutes.do(updateRates)
schedule.every().day.at('00:00').do(recordRates) 

print('Running server')
while True: 
    schedule.run_pending()
    time.sleep(1)
