from fastapi import FastAPI
from backend.database.mongo_connection import get_shares_list, get_fund
from backend.database.influx_connection import read_transactions
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add `null` here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/holding_details")
def holding_details(dbid: str):
    return {"shares": get_shares_list(dbid), "fund": get_fund(dbid)}

@app.get("/transactions_history")
def transactions_history(dbid: str):
    return {"data": read_transactions(dbid)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8401)

