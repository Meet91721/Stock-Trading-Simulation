from backend.config.influx_db_config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def add_transaction(dbid, share, qty, price, status):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = (
        Point('transactions')
        .tag("dbid", dbid)
        .field("Share", share)
        .field(field="qty", value=str(qty))
        .field(field="price", value=str(price))
        .field(field="status", value=status)
    )
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    pass

def read_transactions(dbid):

    query_api = client.query_api()

    query = f"""from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: 2019-08-28T22:00:00Z)
    |> filter(fn: (r) => r._measurement == "transactions" and r.dbid == "{dbid}")"""
    tables = query_api.query(query, org=INFLUXDB_ORG)

    if(len(tables) == 0):
        return []
    time_series = []
    for i in range(len(tables[0].records)):
        data = {}
        data['time'] = tables[0].records[i].values['_time'].strftime("%Y-%m-%d %H:%M:%S")
        data['share'] = tables[0].records[i].values['_value']
        data['price'] = tables[1].records[i].values['_value']
        data['qty'] = tables[2].records[i].values['_value']
        data['status'] = tables[3].records[i].values['_value']
        time_series.append(data)
        pass
    return time_series
