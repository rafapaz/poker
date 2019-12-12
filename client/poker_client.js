
var websocket;

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
            me.innerHTML = '<div class="w3-panel w3-blue w3-circle">' + data[i]['name'] + '<br>' + data[i]['money'] + '</div>';
            continue;
        }
        
        slot = document.getElementById('slot_'+i)
        slot.innerHTML = '<div class="w3-panel w3-grey w3-circle">' + data[i]['name'] + '<br>' + data[i]['money'] + '</div>';
    }
}

function showCards(data)
{    
    me = document.getElementById('me');
    var cards = '';
    for (i in data)
    {
        cards += data[i] + ' ';
    }
    
    newcontent = cards + me.innerHTML;
    me.innerHTML = newcontent;
    //console.log(newcontent);
}

function showTableCards(data)
{
    table = document.getElementById('table');
    var cards = '';
    for (i in data)
    {
        cards += data[i] + ' ';
    }
    table.innerHTML = cards;
}

function toogleShowButtons(show)
{
    buttons = document.getElementById('buttons');
    if (show)
        buttons.style["pointer-events"] = "auto";
    else
        buttons.style["pointer-events"] = "none";        
}

function check()
{
    websocket.send(JSON.stringify({action: 'check'}));
}

function clean_game()
{
    toogleShowButtons(false);
    table = document.getElementById('table');
    table.innerHTML = '';
    websocket.send(JSON.stringify({action: 'idle'}));
}

function connect()
{
    websocket = new WebSocket("ws://127.0.0.1:6789/");

    websocket.onopen = function ()
    {        
        console.log('Connected!');        
        websocket.send(JSON.stringify({name: document.getElementById('name').value}));
        document.getElementById('connect').innerHTML = button_disconnect;

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
                message.innerHTML = data.value;
                break;
            case 'users':
                refreshUsers(data.value);
                break;
            case 'cards':                
                showCards(data.value);
                break;
            case 'wait_game':
                //websocket.send(JSON.stringify({action: 'idle'}));
                break;
            case 'wait_play':
                toogleShowButtons(false);
                break;
            case 'play':
                toogleShowButtons(true);
                break;
            case 'table_cards':
                showTableCards(data.value);
                break;
            case 'end_game':
                setTimeout(clean_game, 10000);                
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
}