#!/usr/bin/env python

import asyncio
import json
import websockets
import time
from poker import Poker
from user import User

USERS = set()
poker = Poker()
IN_GAME = False


async def notify_users(message):
    if USERS:  # asyncio.wait doesn't accept an empty list        
        await asyncio.wait([user.websocket.send(message) for user in USERS])


async def register(websocket):
    msg = await websocket.recv()
    data = json.loads(msg)
    user = User(data['name'], websocket)
    USERS.add(user)
    #poker.register_player(user.player)

    msg = '{} connected!'.format(user.player.name)
    print(msg)
    message = json.dumps({"type": "msg", "value": msg})
    await notify_users(message)
    message = json.dumps({"type": "users", "value": [user.player.serialize() for user in USERS]})    
    await notify_users(message)


async def unregister(user):
    #poker.unregister_player(user.player)
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
        if u.player.name == name:
            return u
    return None


async def start_game(user):    
    global IN_GAME
    
    if IN_GAME or len(USERS) <= 1:        
        message = json.dumps({"type": "wait_game"})
        await user.websocket.send(message)
        return
    
    print('Game started')
    IN_GAME = True
    for u in USERS:        
        poker.register_player(u.player)
    poker.start_game()
    poker.deliver()

    print('Players: ' + str(poker.players))
    for p in poker.players:
        u = get_user_by_name(p.name)
        print('Sending cards to ' + u.player.name)
        message = json.dumps({"type": "cards", "value": [str(c) for c in u.player.cards]})
        await u.websocket.send(message)
        if p.name == poker.get_dealer().name:
            message = json.dumps({"type": "play"})
        else:
            message = json.dumps({"type": "wait_play"})
        await u.websocket.send(message)


async def reveal_card():
    if len(poker.table_cards) == 0:
        poker.reveal_card()
        poker.reveal_card()
        poker.reveal_card()
    elif len(poker.table_cards) < 5:
        poker.reveal_card()
    
    message = json.dumps({"type": "table_cards", "value": [str(c) for c in poker.table_cards]})    
    await notify_users(message)


async def check(user):
    message = json.dumps({"type": "wait_play"})
    await user.websocket.send(message)
    print('CHECK : ' + user.player.name)
     
    if poker.close_cycle():
        await reveal_card()        

    next_user = get_user_by_name(poker.next_player().name)
    message = json.dumps({"type": "play"})
    await next_user.websocket.send(message)


async def PokerServer(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    user = get_user_by_ws(websocket)
    
    try:        
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "disconnect":
                await unregister(user)
            elif data["action"] == "idle":
                await start_game(user)
            elif data["action"] == "check":
                await check(user)
            else:
                print("unsupported event: {}", data)
    except websockets.exceptions.ConnectionClosedError:
        print('Connection closed!')    
    


start_server = websockets.serve(PokerServer, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()