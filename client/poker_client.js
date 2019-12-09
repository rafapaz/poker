

var websocket;

function connect()
{
    websocket = new WebSocket("ws://127.0.0.1:6789/");

    websocket.onopen = function ()
    {
        console.log('Sucesso!');
    };

    websocket.onerror = function (error)
    {
        console.log('WebSocket Error ' + error);
    };

}