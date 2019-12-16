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
PAUSE = False
PAUSE_TIME = 10
PAUSE_START = 0


async def notify_users(message):
    if USERS:  # asyncio.wait doesn't accept an empty list        
        await asyncio.wait([user.websocket.send(message) for user in USERS])


async def send(who=None, type_msg='msg', msg=None):
    if type_msg == 'msg':
        print(msg)
    message = json.dumps({'type': type_msg, 'value': msg})
    if who:
        await who.send(message)
    else:
        await notify_users(message)


async def register(websocket):
    msg = await websocket.recv()
    data = json.loads(msg)
    user = User(data['name'], websocket)
    USERS.add(user)    
    await send(None, 'msg', '{} connected!'.format(user.player.name))
    

async def unregister(user):
    play_now = None
    if len(poker.players) > 0:
        play_now = poker.who_play_now()
        poker.fold_player(user.player)
        poker.unregister_player(user.player)
    USERS.remove(user)    
    await send(None, 'msg', '{} disconnect!'.format(user.player.name))
    if len(poker.players) == 1:        
        await end_game()
        return
        
    if len(poker.players) > 0 and user.player.name == play_now.name:
        await do_cycle()
    

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


def get_update_dict():
    ret = dict()
    table = dict()
    table['cards'] = [str(c) for c in poker.table_cards]
    table['money'] = poker.table_money
    ret['table'] = table
    ret['players'] = [p.serialize(all=False) for p in poker.players]
    return ret


async def start_game(user):
    global IN_GAME
    global PAUSE
    
    if IN_GAME or len(USERS) <= 1:        
        return
    
    if PAUSE:
        await pause_time()
        return

    IN_GAME = True
    await send(None, 'msg', 'Game started!')    
    await send(None, 'users', [user.player.serialize(all=False) for user in USERS])
    
    for u in USERS:        
        poker.register_player(u.player)
    poker.start_game()
    poker.deliver()

    print('Players: ' + str(poker.players))
    for p in poker.players:
        u = get_user_by_name(p.name)
        
        print('Sending cards to ' + u.player.name)
        await send(u.websocket, 'cards', [str(c) for c in u.player.cards])
        
        if p.name == poker.get_dealer().name:
            await send(u.websocket, 'play', poker.high_bet)            
            await send(None, 'msg', 'Its {} turn'.format(p.name))
        else:
            await send(u.websocket, 'wait_play')
        

async def reveal_card():
    if len(poker.table_cards) == 0:
        poker.reveal_card()
        poker.reveal_card()
        poker.reveal_card()
    elif len(poker.table_cards) < 5:
        poker.reveal_card()
    
    await send(None, 'table_cards', [str(c) for c in poker.table_cards])
    

async def do_cycle():    
    if poker.close_cycle():
        if len(poker.table_cards) == 5:
            await send(None, 'show_all_cards', [p.serialize(all=True) for p in poker.players])            
            await end_game()
            return
        else:
            await reveal_card()

    next_user = get_user_by_name(poker.next_player().name)
    await send(next_user.websocket, 'play', poker.high_bet)
    await send(None, 'msg', 'Its {} turn'.format(next_user.player.name))
    await send(None, 'update', get_update_dict())


async def check(user):    
    await send(user.websocket, 'wait_play')
    await send(None, 'msg', user.player.name + ' CHECK')    
    await do_cycle()
  

async def fold(user):    
    poker.fold_player(user.player)
    await send(user.websocket, 'wait_play')
    await send(None, 'msg', user.player.name + ' FOLD')
    if len(poker.players) == 1:        
        await end_game()
        return
    await do_cycle()


async def raise_bet(user, value):
    poker.get_money(user.player, user.player.bet(int(value)))
    await send(user.websocket, 'wait_play')
    await send(None, 'msg', user.player.name + ' RAISE to ' + value)    
    await do_cycle()


async def call(user):
    poker.get_money(user.player, user.player.bet(poker.high_bet))
    await send(user.websocket, 'wait_play')
    await send(None, 'msg', user.player.name + ' CALL')    
    await do_cycle()


async def show_winner():
    win, score = poker.winner()
    await send(None, 'msg', '{} win with {}'.format(win.name, score))


async def end_game():
    global IN_GAME
    global PAUSE    
    global PAUSE_START

    await show_winner()
    IN_GAME = False
    PAUSE = True
    PAUSE_START = time.time()
    await send(None, 'end_game')


async def pause_time():
    global PAUSE    
    global PAUSE_START
    global PAUSE_TIME

    now = time.time()
    if int(now - PAUSE_START) > PAUSE_TIME:
        PAUSE = False
        await send(None, 'end_game')
        return
        
    await send(None, 'pause_time', int(PAUSE_TIME - (now - PAUSE_START)))


async def PokerServer(websocket, path):    
    await register(websocket)
    user = get_user_by_ws(websocket)
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'disconnect':
                await unregister(user)
            elif data['action'] == 'idle':
                await start_game(user)            
            elif data['action'] == 'check':
                await check(user)
            elif data['action'] == 'fold':
                await fold(user)
            elif data['action'] == 'call':
                await call(user)
            elif data['action'] == 'raise':
                await raise_bet(user, data['value'])
            else:
                print("unsupported event: {}", data)
    except websockets.exceptions.ConnectionClosedError:
        print('Connection closed!')    
    


start_server = websockets.serve(PokerServer, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()