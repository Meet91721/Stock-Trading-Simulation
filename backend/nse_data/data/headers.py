from requests import Session
import csv

h = {
    "Host": "www.nseindia.com",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
    "pragma": "no-cache",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}


session = Session()
session.headers.update(h)
session.get("http://www.nseindia.com")

live_quote = 'https://www.nseindia.com/api/quote-equity?symbol={}'
market_status = 'https://www.nseindia.com/api/marketStatus'


name_mappings = {}
names = []
file = open('./backend/nse_data/data/MCAP31032023_0.csv')
csvreader = csv.reader(file)

for row in csvreader:
    name_mappings[row[1].lower()] = {"name": row[2], "symb": row[1]}
    names.append(row[1].lower())
    name_mappings[row[2].lower()] = {"name": row[2], "symb": row[1]}
    names.append(row[2].lower())
file.close()