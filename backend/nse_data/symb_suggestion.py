import json, redis, uvicorn
from fastapi import FastAPI
from backend.nse_data.data.headers import session, name_mappings, names
from backend.config.redis_db_config import REDIS_HOST, REDIS_PORT
from fastapi.middleware.cors import CORSMiddleware

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add `null` here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/symbolSearch")
def symbol_search(q: str):
    if (len(q) == 0):
        return {"suggestions": []}    
    q = q.lower()
    filtered_list = list(set([name_mappings[string]['symb'] for string in names if string.startswith(q)]))
    return_list = [name_mappings[symbol_name.lower()] for symbol_name in filtered_list]
    return {"suggestions": return_list}


@app.get("/historyData")
def history_data(symbol: str, start: str, end: str):
    cache_key = f"{symbol}_{start}_{end}"
    cached_result = client.get(cache_key)
    if cached_result is not None:
        return json.loads(cached_result)
    rr = session.get(f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={start}&to={end}")
    client.set(cache_key, json.dumps(rr.json()['data']))
    print(rr.json())
    return rr.json()    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8203)