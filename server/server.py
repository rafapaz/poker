#!/usr/bin/env python

import asyncio
import json
import websockets
import time
import datetime
from poker import Poker
from user import User

USERS = set()
poker = Poker()
IN_GAME = False
PAUSE = False
PAUSE_TIME = 10
PAUSE_START = 0
PLAY_TIME = 30
PLAY_START = 0


async def notify_users(message):
    #if USERS:  # asyncio.wait doesn't accept an empty list        
    #    await asyncio.wait([user.websocket.send(message) for user in USERS if not user.bot])
    for user in USERS.copy():
        if not user.bot:
            try:
                await user.websocket.send(message)
            except websockets.exceptions.ConnectionClosedOK:
                await unregister(user)
    
    
async def send(who=None, type_msg='msg', msg=None):
    #dest = who.player.name if who else 'all'
    #print(str(datetime.datetime.now()) + ': Sending ' + type_msg + ' to ' + dest)
    if type_msg == 'msg':
        print(msg)
    
    message = json.dumps({'type': type_msg, 'value': msg})
    if who:
        if who.bot and type_msg == 'play':
            await bot_play(who)
        elif not who.bot:
            try:
                await who.websocket.send(message)
            except websockets.exceptions.ConnectionClosedOK:
                await unregister(who)
    else:
        await notify_users(message)
    

async def register(websocket):
    msg = await websocket.recv()
    data = json.loads(msg)
    user = User(data['name'], websocket)
    USERS.add(user)
    """
    bot1 = User('BOT1', None, True)
    USERS.add(bot1)
    bot2 = User('BOT2', None, True)
    USERS.add(bot2)
    bot3 = User('BOT3', None, True)
    USERS.add(bot3)
    bot4 = User('BOT4', None, True)
    USERS.add(bot4)
    bot5 = User('BOT5', None, True)
    USERS.add(bot5)
    """
    await send(None, 'msg', '{} connected!'.format(user.player.name))
    

async def unregister(user):
    global IN_GAME

    play_now = None
    if len(poker.players) > 0:
        play_now = poker.who_play_now()
        poker.fold_player(user.player)
        poker.unregister_player(user.player)
    USERS.remove(user)    
    await send(None, 'msg', '{} disconnect!'.format(user.player.name))

    if not IN_GAME:
        return
    
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
    ret['players'] = [u.player.serialize(all=False) for u in USERS]
    return ret


async def start_game(user):
    global IN_GAME
    global PAUSE
    global PLAY_START
   
    
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
    print('Dealer: ' + poker.get_dealer().name)
    for p in poker.players:
        u = get_user_by_name(p.name)
        
        print('Sending cards to ' + u.player.name)
        await send(u, 'cards', [str(c) for c in u.player.cards])
        await send(u, 'wait_play')        

    PLAY_START = time.time()
    dealer = get_user_by_name(poker.get_dealer().name)
    await send(dealer, 'play', poker.high_bet)
    await send(None, 'update', get_update_dict())    
    await send(None, 'turn', {'name': dealer.player.name, 'time': int(PLAY_TIME - (time.time() - PLAY_START))})


async def reveal_card():
    if len(poker.table_cards) == 0:
        poker.reveal_card()
        poker.reveal_card()
        poker.reveal_card()
    elif len(poker.table_cards) < 5:
        poker.reveal_card()
    

async def do_cycle():
    global IN_GAME
    global PLAY_START
    
    PLAY_START = time.time()
        
    if poker.close_cycle():
        if len(poker.table_cards) == 5:      
            await send(None, 'show_all_cards', [p.serialize(all=True) for p in poker.players])            
            await end_game()            
            return
        else:
            await reveal_card()
    
    next_user = get_user_by_name(poker.next_player().name)
    await send(next_user, 'play', poker.high_bet)    
    if not IN_GAME:
        return
    await send(None, 'update', get_update_dict())    
    await send(None, 'turn', {'name': next_user.player.name, 'time': int(PLAY_TIME - (time.time() - PLAY_START))})    
    

async def check(user):
    await send(user, 'wait_play')
    await send(None, 'msg', user.player.name + ' CHECK')    
    await do_cycle()
  

async def fold(user):    
    poker.fold_player(user.player)
    await send(user, 'wait_play')
    await send(None, 'msg', user.player.name + ' FOLD')
    if len(poker.players) == 1:        
        await end_game()
        return
    await do_cycle()


async def raise_bet(user, value):
    if int(value) <= poker.high_bet:
        await call(user)
        return
    value_bet = user.player.bet(int(value))
    poker.get_money(user.player, value_bet)
    await send(user, 'wait_play')
    await send(None, 'msg', user.player.name + ' RAISE to ' + str(value_bet))
    await do_cycle()


async def call(user):
    poker.get_money(user.player, user.player.bet(poker.high_bet))
    await send(user, 'wait_play')
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
    for u in USERS.copy():
        if u.player.money == 0:
            await send(u, 'out')
            await unregister(u)
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


async def verify_timeout(user, turn_name): 
    global IN_GAME
    if not IN_GAME:
        return

    time.sleep(0.5)
    now = time.time()
    if int(PLAY_TIME - (now - PLAY_START)) < 0:
        user = get_user_by_name(turn_name)
        await unregister(user)
        await do_cycle()
        return
        
    if turn_name != poker.who_play_now().name:
        return
    await send(user, 'update', get_update_dict())    
    await send(user, 'turn', {'name': turn_name, 'time': int(PLAY_TIME - (now - PLAY_START))})


async def bot_play(bot):    
    action, value = bot.player.play(poker.table_cards, poker.high_bet)
    if action == 'fold':
        await fold(bot)
    elif action == 'check':
        await check(bot)
    elif action == 'call':
        await call(bot)
    elif action == 'raise':
        await raise_bet(bot, value)


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
            elif data['action'] == 'timeout':
                await verify_timeout(user, data['value'])
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