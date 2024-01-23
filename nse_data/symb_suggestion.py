from flask import Flask
from flask_restful import Api, Resource, request
from flask_cors import CORS
import json

import redis

client = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
CORS(app)
api = Api(app)

class SymbolSearch(Resource):

    def __init__(self) -> None:

        self.name_mappings = {}
        self.names = []

        import csv
        file = open('MCAP31032023_0.csv')
        csvreader = csv.reader(file)

        for row in csvreader:
            self.name_mappings[row[1].lower()] = {"name": row[2], "symb": row[1]}
            self.names.append(row[1].lower())
            self.name_mappings[row[2].lower()] = {"name": row[2], "symb": row[1]}
            self.names.append(row[2].lower())
        file.close()

    def get(self):
        query = request.args.get('q')
        if (len(query) == 0):
            return {"suggestions":[]}
        filtered_list = list(set([self.name_mappings[string]['symb'] for string in self.names if string.startswith(query)]))
        return_list = [self.name_mappings[symbol_name.lower()] for symbol_name in filtered_list]
        return {"suggestions":return_list}    
    pass

class HistoryData(Resource):

    def __init__(self) -> None:
        super().__init__()
        pass

    def fetchingDetails(self, symbol, start, end):
        cache_key = f"{symbol}_{start}_{end}"
        cached_result = client.get(cache_key)
        # cached_result = None
        if cached_result is not None:
            print("hello")
            return json.loads(cached_result)
        from headers import s
        import time
        time.sleep(3)
        print(cache_key)
        rr = s.get(f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={start}&to={end}")
        client.set(cache_key, json.dumps(rr.json()['data']))
        return rr.json()['data']
        
    def get(self):
        start = request.args.get('start')
        end = request.args.get('end')
        symbol = request.args.get('symbol')
        return {"data":self.fetchingDetails(symbol, start, end)}
    pass

api.add_resource(SymbolSearch, '/symbolSearch')
api.add_resource(HistoryData, '/history')
app.run(debug=True, port=8203)