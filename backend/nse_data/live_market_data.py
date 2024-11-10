import json, asyncio, websockets
from circuitbreaker import circuit
from backend.nse_data.data.failed_stock_info import result
from backend.nse_data.data.headers import session, live_quote, market_status

def stockDataFailureHandler(symbol):
    return result

@circuit(failure_threshold=5, recovery_timeout=30, fallback_function=stockDataFailureHandler)
def getStockData(symbol):
    response = session.get(live_quote.format(symbol))
    if response.status_code == 200:
        return response.json()
    else:
        return result

def marketFailureHandler():
    return {"marketState":[{"market":"Capital Market","marketStatus":"Closed","tradeDate":"-1","index":"-1","last":-1,"variation":-1,"percentChange":-1,"marketStatusMessage":"Normal Market has Closed"}]}

@circuit(failure_threshold=5, recovery_timeout=30, fallback_function=marketFailureHandler)
def getMarketData():
    response = session.get(market_status)
    if response.status_code == 200:
        return response.json()
    else:
        return marketFailureHandler()

async def hello(websocket, path):
    try:
        async for message in websocket:
            while True:
                if(message != 'initiate'):
                    stockData = getStockData(message)
                    await websocket.send(json.dumps(stockData))
                    await asyncio.sleep(1)
                else:
                    await websocket.send(json.dumps(getMarketData()))
                    await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed from client.")

start_server = websockets.serve(hello, "localhost", 8201)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
