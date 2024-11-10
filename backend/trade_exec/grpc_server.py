import grpc
import registry.pyprotos.stocks_pb2_grpc
import registry.pyprotos.stocks_pb2
import concurrent.futures as futures
from backend.database.mongo_connection import get_fund, get_shares, sell_share, buy_share
from backend.database.influx_connection import add_transaction
from backend.nse_data.data.headers import session, live_quote
from backend.trade_exec.publisher import sendMessage

class RegisteringTransactionServicer(registry.pyprotos.stocks_pb2_grpc.RegisteringTransactionServicer):
    def GetFund(self, request, context):
        funds = get_fund(request.dbid)
        return registry.pyprotos.stocks_pb2.FundResponse(fund=funds)
    def GetShareQty(self, request, context):
        qty = get_shares(request.dbid, request.symbol)
        return registry.pyprotos.stocks_pb2.ShareQtyResponse(qty=qty)
    def Buy(self, request, context):
        print('Buy request received', request)
        if request.error != "":
            add_transaction(request.dbid, request.symbol, request.qty, request.price, "failed")
            sendMessage(request.dbid, f"Your order for {request.symbol}, {request.price}, {request.qty} has been rejected due to {request.error}")
            return registry.pyprotos.stocks_pb2.Message(message="Failed")
        add_transaction(request.dbid, request.symbol, request.qty, request.price, "success")
        sendMessage(request.dbid, f"Your order for {request.symbol}, {request.price}, {request.qty} has been executed")
        buy_share(request.dbid, request.symbol, request.qty, request.price)
        return registry.pyprotos.stocks_pb2.Message(message="Success")
    def Sell(self, request, context):
        sell_price = '-' + str(request.price)
        if request.error != "":
            add_transaction(request.dbid, request.symbol, request.qty, sell_price, "failed")
            sendMessage(request.dbid, f"Your sell order for {request.symbol}, {request.price}, {request.qty} has been rejected due to {request.error}")
            return registry.pyprotos.stocks_pb2.Message(message="Failed")
        add_transaction(request.dbid, request.symbol, request.qty, sell_price, "success")
        sendMessage(request.dbid, f"Your sell order for {request.symbol}, {request.price}, {request.qty} has been executed")
        sell_share(request.dbid, request.symbol, request.qty, request.price)
        return registry.pyprotos.stocks_pb2.Message(message="Success")
    def GetShareLivePrice(self, request, context):
        try: 
            price = session.get(live_quote.format(request.symbol)).json()['priceInfo']['lastPrice']
            return registry.pyprotos.stocks_pb2.SharePrice(status="success", price=price)
        except:
            return registry.pyprotos.stocks_pb2.SharePrice(status="failed")
    pass

server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
registry.pyprotos.stocks_pb2_grpc.add_RegisteringTransactionServicer_to_server(
        RegisteringTransactionServicer(), server)

server.add_insecure_port('[::]:8501')
server.start()
server.wait_for_termination()
