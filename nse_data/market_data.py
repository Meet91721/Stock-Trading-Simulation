import json
import asyncio
import websockets
from circuitbreaker import circuit

def stockDataFailureHandler(symbol):
    return {
  "info": {
    "symbol": "-1",
    "companyName": "-1",
    "industry": "-1",
    "activeSeries": [-1],
    "debtSeries": [],
    "tempSuspendedSeries": [],
    "isFNOSec": -1,
    "isCASec": -1,
    "isSLBSec": -1,
    "isDebtSec": -1,
    "isSuspended": -1,
    "isETFSec": -1,
    "isDelisted": -1,
    "isin": "-1",
    "isTop10": -1,
    "identifier": "-1"
  },
  "metadata": {
    "series": "-1",
    "symbol": "-1",
    "isin": "-1",
    "status": "-1",
    "listingDate": "-1",
    "industry": "-1",
    "lastUpdateTime": "-1",
    "pdSectorPe": -1,
    "pdSymbolPe": -1,
    "pdSectorInd": "-1"
  },
  "securityInfo": {
    "boardStatus": "-1",
    "tradingStatus": "-1",
    "tradingSegment": "-1",
    "sessionNo": "-1",
    "slb": "-1",
    "classOfShare": "-1",
    "derivatives": "-1",
    "surveillance": {
      "surv": -1,
      "desc": -1
    },
    "faceValue": -1,
    "issuedSize": -1
  },
  "sddDetails": {
    "SDDAuditor": "-1",
    "SDDStatus": "-1"
  },
  "priceInfo": {
    "lastPrice": -1,
    "change": -1,
    "pChange": -1,
    "previousClose": -1,
    "open": -1,
    "close": -1,
    "vwap": -1,
    "lowerCP": "-1",
    "upperCP": "-1",
    "pPriceBand": "-1",
    "basePrice": -1,
    "intraDayHighLow": {
      "min": -1,
      "max": -1,
      "value": -1
    },
    "weekHighLow": {
      "min": -1,
      "minDate": "-1",
      "max": -1,
      "maxDate": "-1",
      "value": -1
    },
    "iNavValue": -1,
    "checkINAV": -1
  },
  "industryInfo": {
    "macro": "-1",
    "sector": "-1",
    "industry": "-1",
    "basicIndustry": "-1"
  },
  "preOpenMarket": {
    "preopen": [
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1,
        "iep": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      },
      {
        "price": -1,
        "buyQty": -1,
        "sellQty": -1
      }
    ],
    "ato": {
      "buy": -1,
      "sell": -1
    },
    "IEP": -1,
    "totalTradedVolume": -1,
    "finalPrice": -1,
    "finalQuantity": -1,
    "lastUpdateTime": "-1",
    "totalBuyQuantity": -1,
    "totalSellQuantity": -1,
    "atoBuyQty": -1,
    "atoSellQty": -1
  }
}


@circuit(failure_threshold=5, recovery_timeout=30, fallback_function=stockDataFailureHandler)
def getStockData(symbol):
    from headers import s
    stockData = s.get(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}")
    return stockData.json()

def marketFailureHandler():
    return {"marketState":[{"market":"Capital Market","marketStatus":"Closed","tradeDate":"-1","index":"-1","last":-1,"variation":-1,"percentChange":-1,"marketStatusMessage":"Normal Market has Closed"}]}

@circuit(failure_threshold=5, recovery_timeout=30, fallback_function=marketFailureHandler)
def getMarketData():
    from headers import s
    marketData = s.get("https://www.nseindia.com/api/marketStatus")
    return marketData.json()['marketState'][0]

async def hello(websocket, path):

    try:
        async for message in websocket:
            from headers import s
            while True:
                if(message != 'initiate'):
                    # stockData = s.get(f"https://www.nseindia.com/api/quote-equity?symbol={message}")
                    stockData = getStockData(message)
                    # await websocket.send(json.dumps(stockData.json()))
                    await websocket.send(json.dumps(stockData))
                    await asyncio.sleep(40)
                    pass
                else:
                    # marketData = s.get("https://www.nseindia.com/api/marketStatus")
                    marketData = getMarketData()
                    # await websocket.send(json.dumps(marketData.json()['marketState'][0]))
                    await websocket.send(json.dumps(marketData))
                    await asyncio.sleep(40)
                    pass
                pass
            
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed from client.")

start_server = websockets.serve(hello, "localhost", 8201)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
