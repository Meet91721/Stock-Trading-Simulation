# Installation Guide

## Prerequisites
- Python 3.6 or higher
- Go 1.16 or higher
- Apache ActiveMQ Classic
- Redis
- Postgres
- MongoDB
- InfluxDB

## Installation

Starting Auth service:
```bash
    PYTHONPATH=. python3 backend/authenticator/user_auth.py  
```

Starting Live market data services:
```bash
    PYTHONPATH=. python3 backend/nse_data/live_market_data.py
```

Starting historical data services:
```bash
    PYTHONPATH=. python3 backend/nse_data/symb_suggestion.py
```

Starting GRPC:
```bash
    PYTHONPATH=. python3 backend/grpc_server/grpc_server.py
```

Starting trade execution services:
```bash
    cd backend/trade_exec/server
    go mod init server
    go run main.go
```

Starting user holding services:
```bash
    PYTHONPATH=. python3 backend/user_holdings/server.py
```