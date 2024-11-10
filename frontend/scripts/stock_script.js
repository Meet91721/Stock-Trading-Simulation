var stock;

function socketHandler(msg){

    let socket = new WebSocket("ws://localhost:8201")
    
    socket.onopen = function(e) {
        // console.log("sending for: " + msg);
        stock = msg
        socket.send(stock)
    };


    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        console.log(data)
        document.getElementById('company-name').innerHTML=data['info']['companyName']
        document.getElementById('company-symbol').innerHTML=data['metadata']['symbol']
        document.getElementById('open').innerHTML=data['priceInfo']['open']
        document.getElementById('last').innerHTML=data['priceInfo']['lastPrice']
        document.getElementById('high').innerHTML=data['priceInfo']['intraDayHighLow']['max']
        document.getElementById('low').innerHTML=data['priceInfo']['intraDayHighLow']['min']
    }

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Connection died');
        }
    };
}


async function fetchHistoryHandler(event){
    event.preventDefault();
    let start = document.getElementById("start").value;
    let end = document.getElementById("end").value;
    start = new Date(start)
    end = new Date(end);
    function convertDateToString(date) {
        let dd = date.getDate();
        let mm = date.getMonth() + 1; 
        let yyyy = date.getFullYear();

        if (dd < 10) {
            dd = `0${dd}`;
        }
        if (mm < 10) {
            mm = `0${mm}`;
        }

        return `${dd}-${mm}-${yyyy}`;
    }
    start = convertDateToString(start);
    end = convertDateToString(end);

    console.log(start, end)
    await fetch(`http://127.0.0.1:8203/historyData?start=${start}&end=${end}&symbol=${stock}`,{
        method: "GET",
        headers: {
        "Content-Type": "application/json",
        },
    }).then((res) => res.json()).then((data) => {
        console.log(data)
        // let row = document.createElement("tr");
        document.getElementById("history").innerHTML = "";
        let row = document.createElement("tr");
        let date = document.createElement("th");
        let ltp = document.createElement("th");
        let open = document.createElement("th");
        let high = document.createElement("th");
        let low = document.createElement("th");
        let close = document.createElement("th");
        let volume = document.createElement("th");
        date.innerHTML = "Date";
        ltp.innerHTML = "LTP";
        open.innerHTML = "Open";
        high.innerHTML = "High";
        low.innerHTML = "Low";
        close.innerHTML = "Close";
        volume.innerHTML = "Volume";
        row.appendChild(date);
        row.appendChild(ltp);
        row.appendChild(high);
        row.appendChild(low);
        row.appendChild(open);
        row.appendChild(close);
        row.appendChild(volume);
        document.getElementById("history").appendChild(row);
        data['data'].forEach((element) => {
            let row = document.createElement("tr");
            let date = document.createElement("td");
            let ltp = document.createElement("td");
            let open = document.createElement("td");
            let high = document.createElement("td");
            let low = document.createElement("td");
            let close = document.createElement("td");
            let volume = document.createElement("td");
            date.innerHTML = element['CH_TIMESTAMP'];
            ltp.innerHTML = element['CH_LAST_TRADED_PRICE'];
            open.innerHTML = element['CH_OPENING_PRICE'];
            high.innerHTML = element['CH_TRADE_HIGH_PRICE'];
            low.innerHTML = element['CH_TRADE_LOW_PRICE'];
            close.innerHTML = element['CH_CLOSING_PRICE'];
            volume.innerHTML = element['CH_TOT_TRADED_QTY'];
            row.appendChild(date);
            row.appendChild(ltp);
            row.appendChild(high);
            row.appendChild(low);
            row.appendChild(open);
            row.appendChild(close);
            row.appendChild(volume);
            document.getElementById("history").appendChild(row);
        }
        )
    })
}

function buyHandler(event){
    event.preventDefault();
    let quantity = document.getElementById("quantity").value;
    let price = document.getElementById("price").value;
    dbid = localStorage.getItem("token")
    console.log(dbid)   
    // console.log(quantity, price, dbid)
    fetch(`http://localhost:8301/buy_order`,{
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "dbid": dbid,
            "symbol": stock,
            "price": price,
            "qty": quantity,
        })
    }).then((res) => res.json()).then((data) => {
        console.log(data)
    })
}

function sellHandler(event){
    event.preventDefault();
    let quantity = document.getElementById("quantity").value;
    let price = document.getElementById("price").value;
    dbid = localStorage.getItem("token")
    // console.log(dbid)   
    console.log("This is stock: ", stock)
    fetch(`http://localhost:8301/sell_order`,{
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "dbid": dbid,
            "symbol": stock,
            "price": price,
            "qty": quantity,
        })
    }).then((res) => res.json()).then((data) => {
        console.log(data)
    })
}