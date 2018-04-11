import json
import urllib.request
import time
import multiprocessing
import datetime
from datetime import timedelta
import random
import socket
import sqlite3
from threading import Timer
from pprint import pprint
def loadConfig():
    data = open("config.txt", "r+")
    for line in data:
        temp = line
        cfg = temp.rstrip()
        data.close()
        return cfg
def connect(owner, nick, channel, server, password, port, irc):
    irc.send(bytes('PASS ' + password + '\r\n', 'UTF-8'))
    irc.send(bytes('USER ' + nick + '\r\n', 'UTF-8'))
    irc.send(bytes('NICK ' + nick + '\r\n', 'UTF-8'))
    irc.send(bytes('JOIN ' + channel + '\r\n', 'UTF-8'))
    irc.send(bytes("USER %s %s : %s \r\n" % (nick, server, nick), 'UTF-8'))
def compareNames(old):
    new = getNames()
    try:
        intersect = set(old).intersection(new)
        print(intersect)
        return intersect
    except TypeError:
        return "error"
def addPoints(old):
    winners = compareNames(old)
    if winners == "error":
        return
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    for w in winners:
        cur.execute("SELECT * FROM points WHERE name LIKE ?", (w,))
        row = cur.fetchone()
        try:
            newpoints = int(row[1]) + 5
            cur.execute("UPDATE points SET points=? WHERE name=?", (newpoints, w))
            print("User " + w + " has " + str(newpoints) + " points now")
            conn.commit()
        except TypeError:
            cur.execute("INSERT INTO points VALUES (?, ?, ?)", (w, 5, 0))
            conn.commit()
    conn.close()
    return
def addMessage(user):
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM points WHERE name LIKE ?", (user,))
    row = cur.fetchone()
    try:
        newpoints = int(row[1]) + 1
        newmsgs = int(row[2]) + 1
        cur.execute("UPDATE points SET points=?, messages=? WHERE name=?", (newpoints, newmsgs, user))
        conn.commit()
    except TypeError:
        cur.execute("INSERT INTO points VALUES (?, ?, ?)", (user, 1, 1))
        conn.commit()
    conn.close()
    return
def reminder(usr, msg, c):
    owner = 'SirLawlington'
    nick = 'zeevBOT'
    channel = '#zeevtwitch'
    server = 'irc.twitch.tv'
    password = loadConfig()

    port = 6667
    irc = socket.socket()
    irc.connect((server, port))
    connect(owner, nick, channel, server, password, port, irc)
    irc.send(bytes('PRIVMSG ' + c + '  :' + str(usr) + ' is reminding you that: ' + str(msg) + '\r\n', 'UTF-8'))
    return
def getNames():
    try:
        viewer_string = json.load(urllib.request.urlopen("https://tmi.twitch.tv/group/user/zeevtwitch/chatters"))
        viewers = viewer_string['chatters']['moderators'] + viewer_string['chatters']['viewers']
        #print("Current viewers: " + str(viewers))
        return viewers
    except urllib.error.URLError:
        print("timeout")
        return
def bP(t):
    now = datetime.datetime.now()
    try:
        token_eth = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=ETH-" + t))
        token_btc = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=BTC-" + t))
        usd_btc = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=usdt-btc"))
        usd_eth = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getticker?&market=usdt-eth"))
    except urllib.error.URLError:
        print("timeout")
        return
    try:
        token_usd_eth = usd_eth['result']['Ask'] * token_eth['result']['Bid']
    except TypeError:
        token_usd_eth = 0
    try:
        token_usd_btc = usd_btc['result']['Ask'] * token_btc['result']['Bid']
    except TypeError:
        token_usd_btc = 0
    if (token_usd_btc > token_usd_eth):
        profit = (token_usd_btc - token_usd_eth)
    elif (token_usd_btc < token_usd_eth):
        profit = (token_usd_eth - token_usd_btc)
    elif (token_usd_btc == token_usd_eth):
        profit = 0
    tx_fee = (profit / 100) / 4
    if (profit > .2 and token_usd_eth != 0 and token_usd_btc != 0):
        ##            file.write(str(now))
        ##            file.write(t + " USD/BTC/TOKEN: $" + str(token_usd_btc))
        ##            file.write((t + " USD/ETH/TOKEN: $" + str(token_usd_eth)))
        ##            file.write(t + " PROFIT: $" + str(profit - tx_fee))
        ##            file.write(t + " Transaction fee: $" + str(tx_fee))
        ##            file.write("=====================================")
        return(t + " If you buy in terms of BTC, this token will cost $" + str(token_usd_btc) + " In terms of ETH it will cost: $" + str(token_usd_eth) +  " USD profit per " + t + " : $" + str(profit - tx_fee) + " Transaction fee: $" + str(tx_fee))
def bAAP():
    # get all possible pairs and info
    tokens = {'SALT'};
    marketSnapshot = json.load(urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getmarkets"))
    for r in marketSnapshot['result']:
        pivot = r['MarketCurrency']
        base = r['BaseCurrency']
        market_string = base + "-" + pivot
        tokens.add(pivot)
    for t in tokens:
        result = bP(t)
        if(result == None):
            continue
        else:
            return(result)
def parse(msg):
    msg1 = dict()
    username=""
    message=""
    copy = msg
    idk = str(copy).partition('!')
    username = idk[0]
    username = username[1:]
    idk = str(copy).partition('#zeevtwitch')
    message = idk[2]
    message.lstrip()
    message = message[2:]
    msg1['user'] = username
    msg1['msg'] = message
    return msg1
def evaluate(msg):
    result = dict()
    try:
        if msg[0] == '!':
            temp = msg
            try:
                partitioned = temp.partition(' ')
                command = partitioned[0]
                args = partitioned[2]
                print("Command: " + command)
                print("Args: " + args)
                result['command'] = command
                result['args'] = args
                return result
            except ValueError:
                result['command'] = msg
                result['args'] = 'NONE'
                return result
            #print(finalstr)
            return
        else:
            result['command'] = 'NONE'
            result['args'] = 'NONE'
            return result
    except IndexError:
        result['command'] = 'NONE'
        result['args'] = 'NONE'
        return
    return
def checkPriv(user):
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute("SELECT * from mods where name like ?", (user,))
    row = cur.fetchone()
    print(row)
    if(row[0] == user):
        conn.close()
        return 1
    else:
        conn.close()
        return 0
def execute(command, args, user):
    c = '#zeevtwitch'
    check = checkPriv(user)
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    print(check)
    date = datetime.datetime.now()
    formatted = date.strftime("%Y-%m-%d")
    yesterday = datetime.datetime.today() - timedelta(days=1)
    yformatted = yesterday.strftime("%Y-%m-%d")
    if command == '!woof':
        result = bytes('PRIVMSG ' + c + ' :FrankerZ\r\n', 'UTF-8')
    elif command == '!woodenspoon':
        result = bytes('PRIVMSG ' + c + ' :You made ' + str(user) + ' mad--better run quick, they are going to get the wooden spoon!\r\n', 'UTF-8')
    elif command == '!help' or command == '!commands':
        result = bytes('PRIVMSG ' + c + ' :Command help for me is found here: https://pastebin.com/FMeV5rVL \r\n', 'UTF-8')
    elif command == '!sorry':
        result = bytes('PRIVMSG ' + c + ' :Sorry my owner killed you. I would have done it myself, but I have no hands BibleThump\r\n', 'UTF-8')
    elif command == '!tracker':
        result = bytes('PRIVMSG ' + c + ' : https://fortnitetracker.com/profile/pc/zeevtwitch <- click here for stats\r\n', 'UTF-8')
    elif command == '!wager':
        if (args == ''):
            result = bytes('PRIVMSG ' + c + ' :Improper usage. Try !wager <amount> <over/under/win/loss>\r\n', 'UTF-8')
        else:
            temp = str(args).partition(' ')
            try:
                cur.execute("SELECT points FROM points WHERE name=?", (user,))
                wager = int(temp[0])
                balance = cur.fetchone()
                bal = int(balance[0])
            except ValueError:
                if str(temp[0]) == 'all':
                    cur.execute("SELECT points FROM points WHERE name=?", (user,))
                    balance = cur.fetchone()
                    wager = int(balance[0])
                    bal = int(balance[0])
                else:
                    return bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then place a wager using !wager <amount or "all"><over/under/win/loss>\r\n', 'UTF-8')
            type = temp[2]
            print(str(wager) + " : " + str(balance[0]) + " : " + type)
            if wager <= bal:
                if type=='win' or type=='loss':
                    cur.execute("SELECT wins, losses FROM state WHERE date=?", (formatted,))
                    winloss = cur.fetchone()
                    try:
                        payout = int((wager * (winloss[1] / winloss[0])) + wager)
                        newbal = bal - wager
                    except ZeroDivisionError:
                        payout = wager * 1.5
                        newbal = bal - wager
                    except TypeError:
                        payout = bal * (1.5)
                        newbal = 0
                        wager = bal
                    print(user + " bet " + str(wager) + " expected payout of " + str(payout) + " on bet type " + type)
                    cur.execute("INSERT INTO open_bets VALUES (?, ?, ?, ?)", (user, wager, payout ,type))
                    cur.execute("UPDATE points SET points=? WHERE name=?", (newbal, user))
                    result = bytes('PRIVMSG ' + c + ' :@' + user + ' just bet ' + str(wager) + ' ZeevBucks that Zeev will ' + type + ' their next game, with an expected payout of ' + str(payout) + ' if they are right\r\n', 'UTF-8')
                elif type=='over' or type=='under':
                    cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
                    killdeath = cur.fetchone()
                    try:
                        kd = killdeath[0]/killdeath[1]
                    except TypeError:
                        kd = 5
                    payout = int(wager + (wager * (1/kd)))
                    newbal = bal - wager
                    print(user + " bet " + str(wager) + " expected payout of " + str(payout) + " on bet type " + type)
                    cur.execute("UPDATE points SET points=? WHERE name=?", (newbal, user))
                    cur.execute("INSERT INTO open_bets VALUES (?, ?, ?, ?)", (user, wager, payout ,type))
                    result = bytes('PRIVMSG ' + c + ' :@' + user + ' just bet ' + str(wager) + ' ZeevBucks that Zeev will get ' + type + ' their average kills next game, with an expected payout of ' + str(payout) + ' if they are right\r\n', 'UTF-8')
            else:
                result = bytes("PRIVMSG " + c + ' :Insufficient balance. Check your ZeevBucks amount again before placing a bet.\r\n', 'UTF-8')
            # print("You bet " + str(wager) + " on bet type " + str(type))
    elif command == '!totalwins':
        cur.execute("SELECT SUM(wins) FROM totals")
        row = cur.fetchone()
        wins = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Total wincount for Zeevtwitch: ' + wins + '\r\n', 'UTF-8')
    elif command == '!burpcount':
        cur.execute("SELECT burps FROM state")
        row = cur.fetchone()
        burps = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has burped ' + burps + ' times without saying excuse me, this stream alone. Tsk tsk.\r\n', 'UTF-8')
    elif command == '!zeevbux':
        cur.execute("SELECT points FROM points WHERE name=?", (user,))
        balance = cur.fetchone()
        result = bytes('PRIVMSG ' + c + ' :@' +user +' you currently have ' + str(balance[0]) + ' ZeevBux in your account.\r\n', 'UTF-8')
    elif command == '!pottycount':
        cur.execute("SELECT pees FROM state")
        row = cur.fetchone()
        pees = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has peed ' + pees + ' times this stream. Think he washed his hands? Kappa \r\n', 'UTF-8')
    elif command == '!peepeetime':
        cur.execute("Select pees from state")
        row = cur.fetchone()
        pees = int(row[0])
        pees = pees + 1
        cur.execute("UPDATE state SET pees=? where date=?", (pees, formatted))
        result = bytes('PRIVMSG ' + c + ' :Tinkle time! Zeev has drained the vein ' + str(pees) + ' times today\r\n', 'UTF-8')
    elif command == '!burp':
        cur.execute("Select burps from state")
        row = cur.fetchone()
        burps = int(row[0])
        burps = burps + 1
        cur.execute("UPDATE state SET burps=? where date=?", (burps, formatted))
        result = bytes('PRIVMSG ' + c + ' :*buuuuuuurp* ni-*burp*-ice one there Zeev. That is li-*burp*-ike your ' + str(burps) +' burp today or something-I don\'t know *burp* who keeps track of *burp* d-d-dumb stuff like this anyway.\r\n', 'UTF-8')
    elif command == '!addkills' or command == '!addkill' and check == 1:
        if (args == ''):
            r = cur.execute("Select * from state")
            row = cur.fetchone()
            print(row)
            kills = int(row[1])
            print(kills)
            kills = kills + 1
            print(kills)
            cur.execute("UPDATE state set kills=? where date=?", (kills, formatted))
            result = bytes('PRIVMSG ' + c + ' :You have added one kill. So far, Zeev has killed ' + str(kills) + ' lanyard wearing freshman PogChamp\r\n', 'UTF-8')
        else:
            r = cur.execute("Select * from state")
            row = cur.fetchone()
            kills = int(row[1])
            try:
                kills = kills + int(args)
                cur.execute('UPDATE state set kills=? where date=?', (kills, formatted))
                result = bytes('PRIVMSG ' + c + ' :You have added ' + str(args) + ' kills. So far, Zeev has killed ' + str(kills) + ' hopeless 6th graders this stream PogChamp\r\n', 'UTF-8')
            except ValueError:
                result = bytes('PRIVMSG ' + c + ' :Improper usage. Try !addkill <number of kills>\r\n', 'UTF-8')
    elif command == '!bodycount':
        cur.execute("SELECT kills FROM state WHERE date=?", (formatted,))
        kills = cur.fetchone()
        result = bytes('PRIVMSG ' + c + ' :Zeev has given  ' + str(kills[0]) + ' nerds swirlies this stream, sending their careers down the toilet\r\n', 'UTF-8')
    elif command == '!addloss' and check == 1:
        cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
        killdeath = cur.fetchone()
        kills = int(args)
        try:
            kd = int(killdeath[0] / killdeath[1])
        except ZeroDivisionError:
            kd = 1
        except TypeError:
            kd = 1
        cur.execute("SELECT name, payout, type FROM open_bets")
        bets = cur.fetchall()
        for b in bets:
            # name = b[0]
            # reward = b[1]
            # bet_type = b[2]
            #print(b)
            #print(b.keys())
            # row = cur.fetchone()
            name = b[0]
            reward = b[1]
            bet_type = b[2]
            print(bet_type + " : " + name + " : " + str(reward))
            balance = cur.execute("SELECT points FROM points WHERE name=?", (name,))
            bal = cur.fetchone()
            initial_bal = bal[0]
            if bet_type == 'under':
                if(kills <= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'over':
                if(kills >= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'loss':
                new_bal = initial_bal + reward
                cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                print(name + " new balance: " + str(new_bal))
                conn.commit()
                continue
            else:
                continue
        cur.execute("DELETE FROM open_bets")

        cur.execute("Select * from state")
        row = cur.fetchone()
        try:
            kills = int(args)
        except ValueError:
            return bytes('PRIVMSG ' + c + ' :Improper usage, try !addloss <number of kills>\r\n', 'UTF-8')
        losses = row[4]
        losses = losses + 1
        deaths = row[2]
        deaths = deaths + 1
        print(losses)
        totkills = kills + row[1]
        print(totkills)
        p1 = row[7]
        p2 = row[8]
        p3 = row[9]
        cur.execute("INSERT INTO losses VALUES(?, ?, ?, ? , ?)", (formatted, kills, p1, p2, p3))
        cur.execute("UPDATE state SET deaths=?, kills=?, losses=? WHERE date=?", (deaths, totkills, losses, formatted))
        result = bytes('PRIVMSG ' + c + ' :You have added a loss and ' + str(kills) + ' kills. So far, Zeev has ' + str(losses) + ' this stream.\r\n', 'UTF-8')
    elif command == '!winloss':
        cur.execute("Select * from state")
        row = cur.fetchone()
        wins = row[3]
        losses = row[4]
        kills = row[1]
        deaths = row[2]
        try:
            kd = kills/deaths
        except ZeroDivisionError:
            kd = 0
        result = bytes('PRIVMSG ' + c + ' :Zeev has a ' + str(wins) + '-' + str(losses) + ' record today, with a kill/death ratio of ' + str(kd) + ' so far.\r\n', 'UTF-8')
    elif command == '!openwagers':
        bets = cur.execute("SELECT * FROM open_bets WHERE name=?", (user,))
        for b in bets:
            print(b)
        result = bytes('PRIVMSG ' + c + ' :Open bets posted to CLI\r\n', 'UTF-8')
    elif command == '!removebets':
        cur.execute("DELETE FROM open_bets")
        result = bytes('PRIVMSG ' + c + ' :Bets deleted\r\n', 'UTF-8')
    elif command == '!cashout':
        cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
        killdeath = cur.fetchone()
        if int(killdeath[0]) > int(killdeath[1]):
            try:
                kd = int(killdeath[0] / killdeath[1])
            except TypeError:
                kd = 1
            print("kill death: " + kd)
        r = cur.execute("SELECT * FROM open_bets")
        for row in r:
            balance = cur.execute("SELECT points FROM points WHERE name=?", (row[0]),)
            print(balance)
            if row[3] == 'under':
                if(args <= kd):
                    new_bal = balance + int(row[2])
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, user))
            elif row[3] == 'over':
                if(args > kd):
                    new_bal = balance + int(row[2])
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, user))
    elif command == '!addwin' or command =='!addwins' and check == 1:
        cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
        killdeath = cur.fetchone()
        kills = int(args)
        try:
            kd = int(killdeath[0] / killdeath[1])
        except ZeroDivisionError:
            kd = 1
        except TypeError:
            kd = 1
        cur.execute("SELECT name, payout, type FROM open_bets")
        bets = cur.fetchall()
        for b in bets:
            # name = b[0]
            # reward = b[1]
            # bet_type = b[2]
            #print(b)
            #print(b.keys())
            # row = cur.fetchone()
            name = b[0]
            reward = b[1]
            bet_type = b[2]
            print(bet_type + " : " + name + " : " + str(reward))
            balance = cur.execute("SELECT points FROM points WHERE name=?", (name,))
            bal = cur.fetchone()
            initial_bal = bal[0]
            if bet_type == 'under':
                if(kills <= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'over':
                if(kills >= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'win':
                new_bal = initial_bal + reward
                cur.execute("UPDATE points SET points=? WHERE name=?", (new_bal, name))
                print(name + " new balance: " + str(new_bal))
                conn.commit()
                continue
            else:
                continue
        cur.execute("DELETE FROM open_bets")
        r = cur.execute("Select * from state")
        row = cur.fetchone()
        print(row)
        try:
            kills = int(args)
        except ValueError:
            result = bytes('PRIVMSG ' + c + ' :Improper usage, try !addwin <number of kills>\r\n', 'UTF-8')
        wins = row[3]
        wins = wins + 1
        kills = row[1] + kills
        p1 = row[7]
        p2 = row[8]
        p3 = row[9]
        cur.execute("INSERT INTO wins VALUES (?, ? , ? , ? , ?)", (formatted, kills, p1, p2, p3))
        cur.execute("UPDATE state SET wins=?, kills=? WHERE date=?", (wins, kills, formatted))
        result = bytes('PRIVMSG ' + c + ' :You have added one win. So far, Zeev has ' + str(wins) + ' wins this stream PogChamp\r\n', 'UTF-8')
    elif command == '!checkwins' or command == '!anywins' or command == '!wins':
        cur.execute("SELECT wins from state")
        row = cur.fetchone()
        wins = row[0]
        result = bytes('PRIVMSG ' + c + ' :Zeev currently has ' + str(wins) + ' wins this stream\r\n', 'UTF-8')
    elif command == '!addpartner' or command == '!addpartners' and check == 1:
        if (args == ''):
            result = bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <partner name>\r\n', 'UTF-8')
        else:
            try:
                partner = str(args)
                cur.execute("SELECT p1, p2, p3 FROM state WHERE date=?", (formatted,))
                row = cur.fetchone()
                if(row[0]==''):
                    cur.execute("UPDATE state SET p1=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now duo-ing with: ' + partner + '\r\n', 'UTF-8')
                elif(row[1]==''):
                    cur.execute("UPDATE state SET p2=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now playing squads with: ' + partner + ' and ' + row[0] + '\r\n', 'UTF-8')
                elif(row[2]==''):
                    cur.execute("UPDATE state SET p3=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now playing squads with: ' + partner + ', ' + row[1] + ' and ' + row[0] +'\r\n', 'UTF-8')
                else:
                    result = bytes('PRIVMSG ' + c + ' :Cannot add any more partners, Zeev already has 3!\r\n', 'UTF-8')
            except ValueError:
                result = bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <partner name>\r\n', 'UTF-8')
    elif command == '!clearpartners' and check == 1:
        cur.execute("UPDATE state SET p1='', p2='', p3='' WHERE date=?", (formatted,))
        result = bytes('PRIVMSG ' + c + ' :Back to soloqueue to destroy some nerds SwiftRage\r\n', 'UTF-8')
    elif command == '!getpartners' or command == '!partners':
        cur.execute("SELECT p1, p2, p3 FROM state WHERE date=?", (formatted,))
        row = cur.fetchone()
        if(row[0] == ''):
            result = bytes('PRIVMSG ' + c + ' :Zeev is currently playing solos\r\n', 'UTF-8')
        elif(row[0]!='' and row[1] ==''):
            result = bytes('PRIVMSG ' + c + ' :Zeev is currently duo-ing with: ' + row[0] + '\r\n', 'UTF-8')
        elif(row[0]!='' and row[1]!=''):
            result = bytes('PRIVMSG ' + c + ' :Zeev is currently playing squads with ' + row[0] + ' and ' + row[1] + '\r\n', 'UTF-8')
        elif(row[0]!='' and row[1]!='' and row[2]!=''):
            result = bytes('PRIVMSG ' + c + ' :Zeev is currently playing squads with ' + row[0] +', ' + row[1] + ' and ' + row[2] + '\r\n', 'UTF-8')
    elif command == '!newStream' and check == 1:
        cur.execute("SELECT * from state")
        row = cur.fetchone()
        if(row[0] == formatted):
            result = bytes('PRIVMSG ' + c + ' :Woah, chill out man! Todays stream is still ongoing!\r\n', 'UTF-8')
        else:
            cur.execute("INSERT into totals VALUES(?, ?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            newrow = (formatted, 0, 0, 0, 0, 0, 0, '', '', '')
            cur.execute("INSERT into state VALUES(?, ? , ? , ? , ?, ?, ?, ?, ?, ?)", (newrow))
            test = str(row[0])
            print(formatted)
            cur.execute("DELETE FROM state WHERE date=?", (test,))
            conn.commit()
            result = bytes('PRIVMSG ' + c + ' :A new day, a new stream. Time to crack some skulls SwiftRage\r\n', 'UTF-8')
    elif command == '!adddeath':
        cur.execute("SELECT deaths FROM state")
        row = cur.fetchone()
        deaths = int(row[0])
        deaths = deaths+1
        cur.execute("UPDATE state SET deaths=? where date=?",(deaths,formatted))
        result = bytes('PRIVMSG ' + c + ' :Death added. This makes ' + deaths + ' dead Zeevs today. Get good DansGame\r\n', 'UTF-8')
    elif command == '!yesterday':
        cur.execute('SELECT * from totals where date=?', (yformatted,))
        row = cur.fetchone()
        print(row)
        result = bytes('PRIVMSG ' + c + ' : Recap for yesterday: ' + str(row[1]) + ' kills, ' + str(row[2]) + ' deaths, ' + str(row[3]) + ' wins, ' + str(row[4]) + ' losses, ' + str(row[5]) + ' burps, and ' + str(row[6]) + ' pees.\r\n','UTF-8')
    elif command == '!resetState':
        cur.execute("UPDATE state SET kills=0, deaths=0, wins=0, losses=0, burps=0, pees=0, p1='', p2='', p3='' WHERE date=?", (formatted,))
        result = bytes('PRIVMSG ' + c + ' :State reset.\r\n', 'UTF-8')
    elif command == '!freemoney':
        temp = bAAP()
        result = bytes('PRIVMSG ' + c + ' :Arbitrage opportunity found - ' + temp + '\r\n', 'UTF-8')
    elif command == '!latestvideo' or command == '!video' or command == '!youtube':
        result = bytes('PRIVMSG ' + c + ' : https://www.youtube.com/watch?v=hChsWxsoxgA <-Check out my latest highlight video! Editing courtesy of @xliattttt\r\n', 'UTF-8')
    elif command == '!roulette':
        x = random.randint(0, 6)
        print(str(x))
        if x == 0:
            result = bytes('PRIVMSG ' + c + ' :/timeout ' + user + ' 60\r\n', 'UTF-8')
        else:
            result = bytes('PRIVMSG ' + c + ' :You shall live to spam another day. You rolled a ' + str(x) + ' @' + user + ' - maybe buy a lottery ticket?\r\n', 'UTF-8')
    elif command == '!sourcecode':
        result = bytes('PRIVMSG ' + c + ' : View my source here, feel free to fork and offer suggestions to @Sirlawlington https://github.com/Mattyresch/ZeevBot\r\n', 'UTF-8')
    elif command == '!vanish':
        result = bytes('PRIVMSG ' + c + ' :/timeout ' + user + ' 1\r\n', 'UTF-8')
    elif command == '!sens' or command == '!sensitivity':
        result = bytes('PRIVMSG ' + c + ' : 1600 dpi, 0.03 in game\r\n', 'UTF-8')
    elif command == '!specs':
        result = bytes('PRIVMSG ' + c + ' :MOUSE: Logitech Proteus Core G502 | KEYBOARD: Corsair Gaming K65 LUX RGB | MOUSEPAD: Corsair Gaming MM200 Medium | MIC: Blue Yeti | CAM: Logitech C920 | RIG: GTX 1070 Asus ROG Strix Am4 Motherboard Cryorig H7 Cpu Cooler Ryzen 5 3.6 GHz Team Group Dark 2 x 8 gb RAM | HEADSET: Hyper X Cloud Alpha Pro | MONITOR: Acer Predator XB241H-24, Nvidia G-Sync\r\n', 'UTF-8')
    elif command == '!remindme':
        if args == '':
            return bytes('PRIVMSG ' + c + ' :Improper usage. Try !remindme <minutes> <message>\r\n', 'UTF-8')
        else:
            temp = args.partition(' ')
            try:
                timerlen = int(temp[0])
                message = temp[2]
                t = Timer((timerlen*60), reminder, args=(user, message, c))
                t.start()
                return bytes('PRIVMSG ' + c + ' :Timer set!\r\n', 'UTF-8')
            except ValueError:
                return bytes('PRIVMSG ' + c + ' :Improper usage. Try !remindme <minutes> <message>\r\n', 'UTF-8')
    else:
        conn.close()
        return
    conn.commit()
    conn.close()
    return result