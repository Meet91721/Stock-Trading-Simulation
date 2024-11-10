package main

import (
	"net/http"
	"io"
	"encoding/json"
    "google.golang.org/grpc"
	"strconv"
	"log"
	"server/goprotos"
	"context"
	"time"
)

type ApiResponse struct {
	Price  string `json:"price,omitempty"`
	Status string  `json:"status"`
}

type Response struct {
	Msg  string `json:"msg"`
	Dbid string `json:"dbid"`
}

func get_connection() (goprotos.RegisteringTransactionClient, context.Context) {
	conn, err := grpc.Dial("localhost:8501", grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	client := goprotos.NewRegisteringTransactionClient(conn)
	ctx := context.Background()
	return client, ctx
}

func buy_order_router(dbid string, symbol string, price string, qty string) {
	for true {
		conn, err := grpc.Dial("localhost:8501", grpc.WithInsecure(), grpc.WithBlock())
		if err != nil {
			log.Fatalf("did not connect: %v", err)
		}
		defer conn.Close()
		client := goprotos.NewRegisteringTransactionClient(conn)
		ctx, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		req := &goprotos.ShareSymbol{Symbol: symbol}
		res, err := client.GetShareLivePrice(ctx, req)
		if err != nil {
			log.Fatalf("could not get items1: %v", err)
		}
		if res.Status == "failed" {
			continue
		}
		sharePrice := *res.Price
		user_price, _ := strconv.ParseFloat(price, 64)
		
		share_qty, _ := strconv.ParseFloat(qty, 64)
		if sharePrice <= float32(user_price) {
			fund_req := &goprotos.DbID{Dbid: dbid}
			fund_res, fund_err := client.GetFund(ctx, fund_req)
			if fund_err != nil {
				log.Fatalf("could not get items2: %v", fund_err)
			}
			user_fund := fund_res.Fund
			// user_fund, _ := strconv.ParseFloat(fund_res.Fund, 64)
			if user_fund >= (sharePrice * float32(share_qty)) {
				buy_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: ""}
				_, buy_err := client.Buy(ctx, buy_req)
				if buy_err != nil {
					log.Fatalf("could not get items3: %v", buy_err)
				}
				return
			} else {
				buy_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: "Insufficient fund"}
				_, buy_err := client.Buy(ctx, buy_req)
				if buy_err != nil {
					log.Fatalf("could not get items4: %v", buy_err)
				}
				return
			}
		}
		buy_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: "market is closed"}
		_, buy_err := client.Buy(ctx, buy_req)
		if buy_err != nil {
			log.Fatalf("could not get items5: %v", buy_err)
		}
		return
	}
	return 
}

func buy_order(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
    if r.Method == http.MethodOptions {
        w.WriteHeader(http.StatusNoContent) // 204 No Content for preflight response
        return
    }
	if r.Method == "POST" {
		body, _ := io.ReadAll(r.Body)
		keyval := make(map[string]string)
		json.Unmarshal(body, &keyval)
		responseMsg := Response{Msg: "Buy order placed", Dbid: keyval["dbid"]}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(responseMsg)
		go buy_order_router(keyval["dbid"], keyval["symbol"], keyval["price"], keyval["qty"])
	} else {
		responseMsg := Response{Msg: "Method not allowed", Dbid: "1"}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(responseMsg)
	}
}

func sell_order_router(dbid string, symbol string, price string, qty string) {
	for true {
		conn, err := grpc.Dial("localhost:8501", grpc.WithInsecure(), grpc.WithBlock())
		if err != nil {
			log.Fatalf("did not connect: %v", err)
		}
		defer conn.Close()
		client := goprotos.NewRegisteringTransactionClient(conn)
		ctx := context.Background()
		req := &goprotos.ShareSymbol{Symbol: symbol}
		res, err := client.GetShareLivePrice(ctx, req)
		if err != nil {
			log.Fatalf("could not get items: %v", err)
		}
		if res.Status == "failed" {
			continue
		}
		shares_req := &goprotos.ShareQuery{Dbid: dbid, Symbol: symbol}
		shares_res, _ := client.GetShareQty(ctx, shares_req)
		sharePrice := *res.Price
		user_price, _ := strconv.ParseFloat(price, 64)
		share_qty, _ := strconv.ParseFloat(qty, 64)
		if sharePrice >= float32(user_price) {
			if shares_res.Qty >= int32(share_qty) {
				sell_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: ""}
				_, sell_err := client.Sell(ctx, sell_req)
				if sell_err != nil {
					log.Fatalf("could not get items: %v", sell_err)
				}
			} else {
				sell_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: "Insufficient shares"}
				_, sell_err := client.Sell(ctx, sell_req)
				if sell_err != nil {
					log.Fatalf("could not get items: %v", sell_err)
				}
			}
			return 
		}
		sell_req := &goprotos.NotingTransaction{Dbid: dbid, Symbol: symbol, Price: float32(user_price), Qty: int32(share_qty), Error: "market is closed"}
		_, sell_err := client.Sell(ctx, sell_req)
		if sell_err != nil {
			log.Fatalf("could not get items: %v", sell_err)
		}
		return
	}
	return 
}

func sell_order(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
    if r.Method == http.MethodOptions {
        w.WriteHeader(http.StatusNoContent) // 204 No Content for preflight response
        return
    }
	if r.Method == "POST" {
		body, _ := io.ReadAll(r.Body)
		keyval := make(map[string]string)
		json.Unmarshal(body, &keyval)
		responseMsg := Response{Msg: "Sell order placed", Dbid: keyval["dbid"]}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(responseMsg)
		go sell_order_router(keyval["dbid"], keyval["symbol"], keyval["price"], keyval["qty"])
	} else {
		responseMsg := Response{Msg: "Method not allowed", Dbid: "1"}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(responseMsg)
	}
}

func main() {
	http.HandleFunc("/buy_order", buy_order)
	http.HandleFunc("/sell_order", sell_order)
	http.ListenAndServe(":8301", nil)
}