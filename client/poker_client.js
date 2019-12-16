
var websocket;
var my_cards = '';
var slots = [];

window.onload = function() {

    button_connect = '<div class="w3-button w3-orange" id="connect_button" onclick="connect();">Connect</div>';
    button_disconnect = '<div class="w3-button w3-red" id="connect_button" onclick="disconnect();">Disconnect</div>';
    document.getElementById('connect').innerHTML = button_connect;

    message = document.getElementById('message');

};

function refreshUsers(data)
{
    for (var i = 0; i < 7; i++)
    {
        slot = document.getElementById('slot_'+i)
        slot.innerHTML = '';
    }

    for (i in data)
    {
        if (data[i]['name'] == document.getElementById('name').value)
        {
            me = document.getElementById('me');
            me.innerHTML = '<div class="w3-panel w3-blue w3-circle">' + data[i]['last_bet'] + '<br>' + data[i]['name'] + '<br>' + data[i]['money'] + '</div>';
            continue;
        }
        
        slot = document.getElementById('slot_'+i)
        slot.innerHTML = '<div class="w3-panel w3-grey w3-circle">' + data[i]['last_bet'] + '<br>' + data[i]['name'] + '<br>' + data[i]['money'] + '</div>';

        slots[data[i]['name']] = i;        
    }
    
}

function saveMyCards(data)
{
    my_cards = '';
    for (i in data)
    {
        my_cards += data[i] + ' ';
    }
}

function showMyCards()
{    
    me = document.getElementById('me');    
    newcontent = my_cards + me.innerHTML;
    me.innerHTML = newcontent;    
}

function showTable(data)
{
    table = document.getElementById('table');
    var cards = '';
    for (i in data.cards)
    {
        cards += data.cards[i] + ' ';
    }
    table.innerHTML = cards + '<br>' + data.money;
}

function showAllCards(data)
{    
    for (i in data)
    {
        if (data[i]['name'] == document.getElementById('name').value)
            continue;

        slot = document.getElementById('slot_' + slots[data[i]['name']])
        slot.innerHTML += data[i]['cards'];     
    }    
}

function toogleShowButtons(show)
{
    fold_button = document.getElementById('fold_button');
    check_button = document.getElementById('check_button');
    call_button = document.getElementById('call_button');
    raise_button = document.getElementById('raise_button');

    if (show)
    {
        fold_button.style["pointer-events"] = "auto";
        check_button.style["pointer-events"] = "auto";
        call_button.style["pointer-events"] = "auto";
        raise_button.style["pointer-events"] = "auto";
    }
    else
    {
        fold_button.style["pointer-events"] = "none";
        check_button.style["pointer-events"] = "none";
        call_button.style["pointer-events"] = "none";
        raise_button.style["pointer-events"] = "none";
    }
}

function disableSomeButtons(v)
{
    value = parseInt(v);
    
    check_button = document.getElementById('check_button');
    call_button = document.getElementById('call_button');

    if (value > 0)    
        check_button.style["pointer-events"] = "none"; 
    else     
        call_button.style["pointer-events"] = "none"; 
}

function showRaiseInput()
{
    raise_div = document.getElementById("raise_div");
    if (raise_div.style.display === "none") {
        raise_div.style.display = "block";
    } else {
        raise_div.style.display = "none";
    }
}

function check()
{
    websocket.send(JSON.stringify({action: 'check'}));
}

function fold()
{
    websocket.send(JSON.stringify({action: 'fold'}));
}

function call()
{
    websocket.send(JSON.stringify({action: 'call'}));
}

function raise(e)
{    
    if (e.keyCode == 13) {
        raise_value = document.getElementById('raise_input').value;
        websocket.send(JSON.stringify({action: 'raise', value: raise_value}));
        showRaiseInput();
    }
}

function clean_game()
{
    slots = [];
    message.innerHTML = '';
    toogleShowButtons(false);
    table = document.getElementById('table');
    table.innerHTML = '';    
}

function showPauseTime(data)
{
    pause = document.getElementById('pause_time');
    if (parseInt(data) == 0)
    {
        pause.innerHTML = '';
        clean_game();
    }
    else
    {
        pause.innerHTML = 'Game will start in ' + data + ' seconds';
    }
}

function connect()
{
    websocket = new WebSocket("ws://127.0.0.1:6789/");

    websocket.onopen = function ()
    {        
        console.log('Connected!');
        websocket.send(JSON.stringify({name: document.getElementById('name').value}));
        document.getElementById('connect').innerHTML = button_disconnect;
        document.getElementById('name').disabled = true;
        clean_game();
        websocket.send(JSON.stringify({action: 'idle'}));
    };

    websocket.onerror = function (error)
    {
        console.log('WebSocket Error ' + error);
    };

    websocket.onmessage = function(event)
    {
        data = JSON.parse(event.data);
        switch (data.type) {
            case 'msg':
                message.innerHTML = data.value + '<br>' + message.innerHTML;
                break;
            case 'users':
                refreshUsers(data.value);
                break;
            case 'cards':                
                saveMyCards(data.value);
                showMyCards();
                break;
            case 'show_all_cards':                
                showAllCards(data.value);
                break;
            case 'wait_play':
                toogleShowButtons(false);
                break;
            case 'play':                
                toogleShowButtons(true);
                disableSomeButtons(data.value);
                break;
            case 'end_game':                
                websocket.send(JSON.stringify({action: 'idle'}));
                break;
            case 'pause_time':
                showPauseTime(data.value);
                websocket.send(JSON.stringify({action: 'idle'}));
                break;
            case 'update':
                refreshUsers(data.value.players);
                showMyCards();
                showTable(data.value.table);                
                break;
            default:
                console.error("unsupported event", data);
        }
    };

}

function disconnect()
{
    websocket.send(JSON.stringify({action: 'disconnect'}));
    websocket.close();
    document.getElementById('connect').innerHTML = button_connect;
    document.getElementById('name').disabled = false;
}
