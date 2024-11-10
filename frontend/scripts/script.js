

var dbid;
var socket;

window.onload = function(){
    dbid = localStorage.getItem("token")
    if(dbid){
        socket = new WebSocket("ws://localhost:8201")
        socketHandler("initiate");
    }
    else{
        window.location.href = "signIn.html"
    }
}

function logoutHandler(){
    localStorage.removeItem("token")
    window.location.href = "signIn.html"
}

function socketHandler(msg){
    
    socket.onopen = function(e) {
        console.log("Connected to live market status");
        socket.send(msg)
    };


    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        console.log(data)
        document.getElementById('market-status').innerHTML =  data['marketState'][0]['marketStatus'];
        document.getElementById('ltp').innerHTML =  data['marketState'][0]['last'];
        document.getElementById('percent-change').innerHTML = data['marketState'][0]['percentChange'] + "%";
        document.getElementById('variation').innerHTML =  data['marketState'][0]['variation'];
    }

    socket.onclose = function(event) {
        if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
        console.log('[close] Connection died');
        }
    };
}

async function symbolSearchHandler(event){
    console.log(event.target.value)
    await fetch(`http://127.0.0.1:8203/symbolSearch?q=${event.target.value}`,{
        method: "GET",
        headers: {
        "Content-Type": "application/json",
        },
    }).then((res) => res.json()).then((data) => {
        let element = document.getElementById("suggestion");
        element.innerHTML = "";
        element.style.height = "0px"
        element.style.overflow = "scroll"
        for(let i = 0; i < data['suggestions'].length; i++){
            element.style.height = "120px"
            let button = document.createElement("button");
            button.innerHTML = data['suggestions'][i]['name'];
            button.style.display = "block";
            button.value = data['suggestions'][i]['symb'];
            button.addEventListener("click",async (event) => {
                element.innerHTML=""
                element.style.height = "0px"
                // console.log(button.value)
                document.getElementById("stock-detail").setAttribute("symbol", button.value);
                document.getElementById("stock-detail").style.display = "block";
                document.getElementById("stock-detail").src = "/stock.html";
            })
            element.appendChild(button);
        }
    })
}

async function transactionsHandler(event){
    // await fetch(`http://localhost:8401/api/transactions_history/${dbid}`,{
    //     method: "GET",
    // }).then((res) => {console.log(res)})
    dbid = localStorage.getItem("token")
    await fetch(`http://localhost:8401/transactions_history/?dbid=${dbid}`,{
        method: "GET",
        headers: {
        "Content-Type": "application/json",
        },
    }).then((res) => res.json()).then((data) => {
        data = data['data']
        console.log(data)
        let element = document.getElementById("transactions");
        element.innerHTML = "";
        // add table header
        let row = document.createElement("tr");
        let th1 = document.createElement("th");
        th1.innerHTML = "Share";
        let th2 = document.createElement("th");
        th2.innerHTML = "Qty";
        let th3 = document.createElement("th");
        th3.innerHTML = "Price";
        let th4 = document.createElement("th");
        th4.innerHTML = "Time";
        let th5 = document.createElement("th");
        th5.innerHTML = "Type";
        let th6 = document.createElement("th");
        th6.innerHTML = "Status";
        row.appendChild(th1);
        row.appendChild(th2);
        row.appendChild(th3);
        row.appendChild(th4);
        row.appendChild(th5);
        row.appendChild(th6);
        element.appendChild(row);

        for(let i = 0; i < data.length; i++){
            row = document.createElement("tr");
            let td1 = document.createElement("td");
            td1.innerHTML = data[i]['share'];
            let td2 = document.createElement("td");
            td2.innerHTML = Math.abs(Number(data[i]['qty']));
            let td3 = document.createElement("td");
            td3.innerHTML = Math.abs(data[i]['price']);
            let td4 = document.createElement("td");
            td4.innerHTML = data[i]['time'];
            let td5 = document.createElement("td");
            if(data[i]['price'][0] === '-'){
                td5.innerHTML = "Sell";
            }
            else{
                td5.innerHTML = "Buy";
            }

            let td6 = document.createElement("td");
            td6.innerHTML = data[i]['status'];
            row.appendChild(td1);
            row.appendChild(td2);
            row.appendChild(td3);
            row.appendChild(td4);
            row.appendChild(td5);
            row.appendChild(td6);
            element.appendChild(row);
        }
    })
}

function holdingsHandler(event){
    fetch(`http://localhost:8401/holding_details/?dbid=${dbid}`,{
        method: "GET",
        headers: {
        "Content-Type": "application/json",
        },
    }).then((res) => res.json()).then((data) => {
        shares = data['shares']
        let element = document.getElementById("holdings");
        element.innerHTML = "";
        let row = document.createElement("tr");
        let th1 = document.createElement("th");
        th1.innerHTML = "Share";
        let th2 = document.createElement("th");
        th2.innerHTML = "Qty";
        row.appendChild(th1);
        row.appendChild(th2);
        element.appendChild(row);
        for (let i = 0; i < shares.length; i++){
            let th1 = document.createElement("td");
            th1.innerHTML = shares[i]['share'];
            let th2 = document.createElement("td");
            th2.innerHTML = shares[i]['qty'];
            let row = document.createElement("tr");
            row.appendChild(th1);
            row.appendChild(th2);
            element.appendChild(row);
        }
        let fund = document.getElementById("fund");
        fund.innerHTML = "";
        let spn1 = document.createElement("span");
        spn1.innerHTML = "Available Fund: ";
        let spn2 = document.createElement("span");
        spn2.innerHTML = data['fund'];
        fund.appendChild(spn1);
        fund.appendChild(spn2);
    })
}

function initializeActiveMQConsumer() {

    const client = Stomp.client('ws://localhost:61614/stomp');
    client.connect('username', 'password', onSuccess, onError);

    function onSuccess() {
        console.log('Connected to live transactions status');
        const subscription = client.subscribe(`/queue/${localStorage.getItem("token")}`, onMessageReceived);
    }

    function onError(error) {
        console.error('Error connecting to ActiveMQ:', error);
    }

    function onMessageReceived(message) {
        alert(message.body)
    }
}
setInterval(initializeActiveMQConsumer, 20000);
