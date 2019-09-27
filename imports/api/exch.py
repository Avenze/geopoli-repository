import requests
import json

def getExchangeRatesUSD():
    api_url = 'https://api.exchangeratesapi.io/latest?base=USD&symbols=AUD,BRL,CAD,CNY,EUR,INR,IDR,JPY,MXN,KRW,RUB,ZAR,TRY,GBP'
    response = requests.get(api_url)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    return None

def getExchangeRatesEUR():
    api_url = 'https://api.exchangeratesapi.io/latest?base=EUR&symbols=AUD,BRL,CAD,CNY,USD,INR,IDR,JPY,MXN,KRW,RUB,ZAR,TRY,GBP'
    response = requests.get(api_url)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    return None

