#!/usr/bin/env python

import asyncio
import json
import websockets
from user import User

USERS = set()

async def notify_users(message):
    if USERS:  # asyncio.wait doesn't accept an empty list        
        await asyncio.wait([user.websocket.send(message) for user in USERS])


async def register(websocket):
    msg = await websocket.recv()
    data = json.loads(msg)
    user = User(data['name'], websocket)
    USERS.add(user)

    msg = '{} connected!'.format(user.player.name)
    print(msg)
    message = json.dumps({"type": "msg", "value": msg})
    await notify_users(message)
    message = json.dumps({"type": "users", "value": [user.player.serialize() for user in USERS]})    
    await notify_users(message)


async def unregister(user):
    USERS.remove(user)    
    
    msg = '{} disconnect!'.format(user.player.name)
    print(msg)
    message = json.dumps({"type": "msg", "value": msg})
    await notify_users(message)
    message = json.dumps({"type": "users", "value": [user.player.serialize() for user in USERS]})    
    await notify_users(message)

def get_user_by_ws(websocket):
    for u in USERS:
        if u.websocket == websocket:
            return u
    return None

def get_user_by_name(name):
    for u in USERS:
        if u.name == name:
            return u
    return None

async def PokerServer(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    user = get_user_by_ws(websocket)
    
    try:
        #await websocket.send(state_event())
        async for message in websocket:            
            data = json.loads(message)
            if data["action"] == "disconnect":
                await unregister(user)                
            else:
                print("unsupported event: {}", data)
    except websockets.exceptions.ConnectionClosedError:
        print('Connection closed!')    
    


start_server = websockets.serve(PokerServer, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()