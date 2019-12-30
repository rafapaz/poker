#!/usr/bin/env python

import asyncio
import json
import websockets
import time
import datetime
import logging
from room import Room
from user import User


logging.basicConfig(format='%(asctime)s Room: %(room)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
ROOMS = dict()
PLAYER_ROOM = dict()
MAX_USERS = 8


def log(user, msg):
    if user.player.name in PLAYER_ROOM:
        logger.info(msg, extra={'room': PLAYER_ROOM[user.player.name]})


def open_room():    
    room = Room()
    cod = str(hash(datetime.datetime.now()))[-5:]
    ROOMS[cod] = room
    return cod
    

def close_room(cod):
    del ROOMS[cod]


def empty_room():
    for cod, room in ROOMS.items():
        if len(room.users) < MAX_USERS:
            return cod
    
    return None
    

async def notify_users(user, message):
    #if USERS:  # asyncio.wait doesn't accept an empty list        
    #    await asyncio.wait([user.websocket.send(message) for user in USERS if not user.bot])
    for u in ROOMS[PLAYER_ROOM[user.player.name]].users.copy():
        if not u.bot:
            try:
                await u.websocket.send(message)
            except websockets.exceptions.ConnectionClosedOK:
                await unregister(u)
            except websockets.exceptions.ConnectionClosedError:
                log(user, 'Unknown error while notifying user: ' + u.player.name)
                await unregister(u)
    
    
async def send(user, dest=None, type_msg='msg', msg=None):
    #dest_name = dest.player.name if dest else 'all'
    #log(user, str(datetime.datetime.now()) + ': Sending ' + type_msg + ' to ' + dest_name)
    if type_msg == 'msg':
        log(user, msg)
    
    message = json.dumps({'type': type_msg, 'value': msg})
    if dest:
        if dest.bot and type_msg == 'play':
            await bot_play(user, dest)
        elif not dest.bot:
            try:
                await dest.websocket.send(message)
            except websockets.exceptions.ConnectionClosedOK:
                await unregister(dest)
    else:
        await notify_users(user, message)
    

async def register(websocket):
    msg = await websocket.recv()
    data = json.loads(msg)    
    if 'token' not in data:
        return None
    user = User(data['name'], int(data['money']), websocket)

    cod_room = empty_room()
    if cod_room is None:
        cod_room = open_room()
    
    ROOMS[cod_room].users.add(user)
    PLAYER_ROOM[data['name']] = cod_room
    
    await send(user, None, 'msg', '{} connected!'.format(user.player.name))
    return user
    

async def unregister(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    users = room.users

    if user not in users:
        return

    play_now = None
    if len(poker.players) > 0:
        play_now = poker.who_play_now()
        poker.fold_player(user.player)
        poker.unregister_player(user.player)
    users.remove(user)
    await send(user, None, 'msg', '{} disconnect!'.format(user.player.name))

    if len(users) == 0:
        close_room(PLAYER_ROOM[user.player.name])
        del PLAYER_ROOM[user.player.name]

    if not room.in_game:
        return
    
    if len(poker.players) == 1:
        await end_game(user)
        return
        
    if len(poker.players) > 0 and user.player.name == play_now.name:
        await do_cycle(user)
    

def get_user_by_name(user, name):    
    users = ROOMS[PLAYER_ROOM[user.player.name]].users
    for u in users:
        if u.player.name == name:
            return u
    return None


def get_update_dict(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    users = room.users

    ret = dict()
    table = dict()
    table['cards'] = [str(c) for c in poker.table_cards]
    table['money'] = poker.table_money
    ret['table'] = table
    list_players = [(u.player, poker.get_player_order(u.player)) for u in users]
    list_players.sort(key = lambda x: x[1])
    ret['players'] = [p.serialize(all=False) for p,o in list_players]
    return ret


async def start_game(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    users = room.users   
    
    if room.in_game or len(users) <= 1:
        return
    
    if room.pause:
        await pause_time(user)
        return

    room.in_game = True
    await send(user, None, 'msg', 'Game started!')
    await send(user, None, 'users', [u.player.serialize(all=False) for u in users])
    
    for u in users:        
        poker.register_player(u.player)
    poker.start_game()
    poker.deliver()

    log(user, 'Players: ' + str(poker.players))
    log(user, 'Dealer: ' + poker.get_dealer().name)
    for p in poker.players:
        u = get_user_by_name(user, p.name)
        
        log(user, 'Sending cards to ' + u.player.name)
        await send(user, u, 'cards', [str(c) for c in u.player.cards])
        await send(user, u, 'wait_play')        

    room.play_start = time.time()
    dealer = get_user_by_name(user, poker.get_dealer().name)    
    await send(user, None, 'dealer', dealer.player.name)
    await check(dealer)
    await raise_bet(get_user_by_name(user, poker.who_play_now().name), 25)
    await raise_bet(get_user_by_name(user, poker.who_play_now().name), 50)
    

async def reveal_card(user):
    poker = ROOMS[PLAYER_ROOM[user.player.name]].poker
    
    if len(poker.table_cards) == 0:
        poker.reveal_card()
        poker.reveal_card()
        poker.reveal_card()
    elif len(poker.table_cards) < 5:
        poker.reveal_card()
    

async def do_cycle(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
       
    room.play_start = time.time()
        
    if poker.close_cycle():
        if len(poker.table_cards) == 5:      
            await send(user, None, 'show_all_cards', [p.serialize(all=True) for p in poker.players])            
            await end_game(user)            
            return
        else:
            await reveal_card(user)
    
    next_user = get_user_by_name(user, poker.next_player().name)
    await send(user, next_user, 'play', poker.high_bet)    
    if not room.in_game:
        return
    await send(user, None, 'update', get_update_dict(user))
    await send(user, None, 'turn', {'name': next_user.player.name, 'time': int(room.play_time - (time.time() - room.play_start))})
    

async def check(user):    
    await send(user, user, 'wait_play')
    await send(user, None, 'msg', user.player.name + ' CHECK')    
    await do_cycle(user)
  

async def fold(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    
    poker.fold_player(user.player)
    await send(user, user, 'wait_play')
    await send(user, None, 'msg', user.player.name + ' FOLD')
    if len(poker.players) == 1:        
        await end_game(user)
        return
    await do_cycle(user)


async def raise_bet(user, value):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker

    if int(value) <= poker.high_bet:
        await call(user)
        return
    value_bet = user.player.bet(int(value))
    poker.get_money(user.player, value_bet)
    await send(user, user, 'wait_play')
    await send(user, None, 'msg', user.player.name + ' RAISE to ' + str(value_bet))
    await do_cycle(user)


async def call(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker

    poker.get_money(user.player, user.player.bet(poker.high_bet))
    await send(user, user, 'wait_play')
    await send(user, None, 'msg', user.player.name + ' CALL')    
    await do_cycle(user)


async def show_winner(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker

    win, score = poker.winner()
    await send(user, None, 'msg', '{} win with {}'.format(win.name, score))


async def end_game(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]   
    users = room.users 

    await show_winner(user)
    room.in_game = False
    room.pause = True
    room.pause_start = time.time()
    for u in users.copy():
        if u.player.money == 0:
            await send(user, u, 'out')
            await unregister(u)
    await send(user, None, 'end_game')


async def pause_time(user):
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    
    now = time.time()
    if int(now - room.pause_start) > room.pause_time:
        room.pause = False
        await send(user, None, 'end_game')
        return
        
    await send(user, None, 'pause_time', int(room.pause_time - (now - room.pause_start)))


async def verify_timeout(user, turn_name): 
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    
    if not room.in_game:
        return

    time.sleep(0.5)
    now = time.time()
    if int(room.play_time - (now - room.play_start)) < 0:
        u = get_user_by_name(user, turn_name)
        await unregister(u)
        await do_cycle(user)
        return
        
    if turn_name != poker.who_play_now().name:
        return
    await send(user, user, 'update', get_update_dict(user))    
    await send(user, user, 'turn', {'name': turn_name, 'time': int(room.play_time - (now - room.play_start))})


async def bot_play(user, bot):    
    room = ROOMS[PLAYER_ROOM[user.player.name]]
    poker = room.poker
    
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
    user = await register(websocket)
    if user is None:
        return
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
                log(user, 'unsupported event: {}'.format(data))
    except websockets.exceptions.ConnectionClosedError:
        log(user, 'Connection closed!')    
    


start_server = websockets.serve(PokerServer, "0.0.0.0", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()