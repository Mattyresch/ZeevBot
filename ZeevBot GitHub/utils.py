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
#
# def getState(state):
#     data = open("state.txt", "r+")
#     for line in data:
#         if line.find('wintot') != -1:
#             temp = line.partition(':')
#             state['wintot'] = int(temp[2].lstrip())
#         if line.find('total kills') != -1:
#             temp = line.partition(':')
#             state['total kills'] = int(temp[2].lstrip())
#         if line.find('wins')!=-1:
#             temp = line.partition(':')
#             state['wins'] = int(temp[2].lstrip())
#         if line.find('kills')!=-1:
#             temp = line.partition(':')
#             state['kills'] = int(temp[2].lstrip())
#         if line.find('burps')!=-1:
#             temp = line.partition(':')
#             state['burps'] = int(temp[2].lstrip())
#         if line.find('deaths')!=-1:
#             temp = line.partition(':')
#             state['deaths'] = int(temp[2].lstrip())
#         if line.find('pees')!=-1:
#             temp = line.partition(':')
#             state['pees'] = int(temp[2].lstrip())
#         if line.find('p1')!=-1:
#             temp = line.partition(':')
#             state['p1'] = str(temp[2].lstrip())
#         if line.find('p2') != -1:
#             temp = line.partition(':')
#             state['p2'] = str(temp[2].lstrip())
#         if line.find('p3') != -1:
#             temp = line.partition(':')
#             state['p3'] = str(temp[2].lstrip())
#         if line.find('partners')!=-1:
#             temp = line.partition(':')
#             state['numberpartners'] = int(temp[2].lstrip())
#     data.close()
#     return state

# def writeState(state):
#     data = open("state.txt", "w+")
#     data.write("total kills: " + str(state['total kills']) + '\n')
#     data.write("wintot: " + str(state['wintot']) + '\n')
#     data.write("kills: " + str(state['kills']) + '\n')
#     data.write("deaths: " + str(state['deaths']) + '\n')
#     data.write("wins: " + str(state['wins']) + '\n')
#     data.write("pees: " + str(state['pees']) + '\n')
#     data.write("burps: " + str(state['burps']) + '\n')
#     data.write("p1: " + str(state['p1']) + '\n')
#     data.write("p2: " + str(state['p2']) + '\n')
#     data.write("p3: " + str(state['p3']) + '\n')
#     data.write("partners: " + str(state['numberpartners']) + '\n')
#     data.close()
#     return

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
# buildAllArbPairs()

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
        return 1
    else:
        return 0

def execute(command, args, user):
    c = '#zeevtwitch'
    check = checkPriv(user)
    if check == 0:
        result = bytes('PRIVMSG ' + c + ' :Sorry, only mods can control my power SwiftRage\r\n', 'UTF-8')
        return result
    else:
        conn = sqlite3.connect('bot.db')
        cur = conn.cursor()
    print(check)
    date = datetime.datetime.now()
    formatted = date.strftime("%Y-%m-%d")
    yesterday = datetime.datetime.today() - timedelta(days=1)
    yformatted = yesterday.strftime("%Y-%m-%d")
    if command == '!woof':
        result = bytes('PRIVMSG ' + c + ' :FrankerZ\r\n', 'UTF-8')
        return result
    elif command == '!woodenspoon':
        result = bytes('PRIVMSG ' + c + ' :You made ' + str(user) + ' mad--better run quick, they are going to get the wooden spoon!\r\n', 'UTF-8')
        return result
    elif command == '!help' or command == '!commands':
        result = bytes('PRIVMSG ' + c + ' :Command help for me is found here: https://pastebin.com/FMeV5rVL \r\n', 'UTF-8')
        return result
    elif command == '!sorry':
        result = bytes('PRIVMSG ' + c + ' :Sorry my owner killed you. I would have done it myself, but I have no hands BibleThump\r\n', 'UTF-8')
        return result
    elif command == '!tracker':
        result = bytes('PRIVMSG ' + c + ' : https://fortnitetracker.com/profile/pc/zeevtwitch <- click here for stats\r\n', 'UTF-8')
        return result
    elif command == '!totalwins':
        cur.execute("SELECT SUM(wins) FROM totals")
        row = cur.fetchone()
        wins = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Total wincount for Zeevtwitch: ' + wins + '\r\n', 'UTF-8')
        return result
    elif command == '!burpcount':
        cur.execute("SELECT burps FROM state")
        row = cur.fetchone()
        burps = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has burped ' + burps + ' times without saying excuse me, this stream alone. Tsk tsk.\r\n', 'UTF-8')
        return result
    elif command == '!pottycount':
        cur.execute("SELECT pees FROM state")
        row = cur.fetchone()
        pees = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has peed ' + pees + ' times this stream. Think he washed his hands? Kappa \r\n', 'UTF-8')
        return result
    elif command == '!peepeetime':
        cur.execute("Select pees from state")
        row = cur.fetchone()
        pees = int(row[0])
        pees = pees + 1
        cur.execute("UPDATE state SET pees=? where date=?", (pees, formatted))
        result = bytes('PRIVMSG ' + c + ' :Tinkle time! Zeev has drained the vein ' + str(pees) + ' times today\r\n', 'UTF-8')
        conn.commit()
        return result
    elif command == '!burp':
        cur.execute("Select burps from state")
        row = cur.fetchone()
        burps = int(row[0])
        burps = burps + 1
        cur.execute("UPDATE state SET burps=? where date=?", (burps, formatted))
        result = bytes('PRIVMSG ' + c + ' :*buuuuuuurp* ni-*burp*-ice one there Zeev. That is li-*burp*-ike your ' + str(burps) +' burp today or something-I don\'t know *burp* who keeps track of *burp* d-d-dumb stuff like this anyway.\r\n', 'UTF-8')
        conn.commit()
        return result
    elif command == '!addkills' or command == '!addkill':
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
            conn.commit()
            return result
        else:
            r = cur.execute("Select * from state")
            row = cur.fetchone()
            kills = int(row[1])
            try:
                kills = kills + int(args)
                cur.execute('UPDATE state set kills=? where date=?', (kills, formatted))
                result = bytes('PRIVMSG ' + c + ' :You have added ' + str(args) + ' kills. So far, Zeev has killed ' + str(kills) + ' hopeless 6th graders this stream PogChamp\r\n', 'UTF-8')
                conn.commit()
                return result
            except ValueError:
                result = bytes('PRIVMSG ' + c + ' :Improper usage. Try !addkill <number of kills>\r\n', 'UTF-8')
                return result
    elif command == '!bodycount':
        cur.execute("SELECT kills FROM state WHERE date=?", (formatted,))
        kills = cur.fetchone()
        result = bytes('PRIVMSG ' + c + ' :Zeev has given  ' + str(kills[0]) + ' nerds swirlies this stream, sending their careers down the toilet\r\n', 'UTF-8')
        return result
    elif command == '!addloss':
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
        conn.commit()
        result = bytes('PRIVMSG ' + c + ' :You have added a loss and ' + str(kills) + ' kills. So far, Zeev has ' + str(losses) + ' this stream.\r\n', 'UTF-8')
        return result
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
        return result
    elif command == '!addwin' or command =='!addwins':
        r = cur.execute("Select * from state")
        row = cur.fetchone()
        print(row)
        try:
            kills = int(args)
        except ValueError:
            return bytes('PRIVMSG ' + c + ' :Improper usage, try !addwin <number of kills>\r\n', 'UTF-8')
        wins = row[3]
        wins = wins + 1
        kills = row[1] + kills
        p1 = row[7]
        p2 = row[8]
        p3 = row[9]
        cur.execute("INSERT INTO wins VALUES (?, ? , ? , ? , ?)", (formatted, kills, p1, p2, p3))
        cur.execute("UPDATE state SET wins=?, kills=? WHERE date=?", (wins, kills, formatted))
        result = bytes('PRIVMSG ' + c + ' :You have added one win. So far, Zeev has ' + str(wins) + ' wins this stream PogChamp\r\n', 'UTF-8')
        conn.commit()
        return result
    elif command == '!checkwins' or command == '!anywins' or command == '!wins':
        cur.execute("SELECT wins from state")
        row = cur.fetchone()
        wins = row[0]
        result = bytes('PRIVMSG ' + c + ' :Zeev currently has ' + str(wins) + ' wins this stream\r\n', 'UTF-8')
        return result
    elif command == '!addpartner' or command == '!addpartners':
        if (args == ''):
            result = bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <partner name>\r\n', 'UTF-8')
            return result
        else:
            try:
                partner = str(args)
                cur.execute("SELECT p1, p2, p3 FROM state WHERE date=?", (formatted,))
                row = cur.fetchone()
                if(row[0]==''):
                    cur.execute("UPDATE state SET p1=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now duo-ing with: ' + partner + '\r\n', 'UTF-8')
                    conn.commit()
                    return result
                elif(row[1]==''):
                    cur.execute("UPDATE state SET p2=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now playing squads with: ' + partner + ' and ' + row[0] + '\r\n', 'UTF-8')
                    conn.commit()
                    return result
                elif(row[2]==''):
                    cur.execute("UPDATE state SET p3=? WHERE date=?", (partner, formatted))
                    result = bytes('PRIVMSG ' + c + ' :Partner added, Zeev is now playing squads with: ' + partner + ', ' + row[1] + ' and ' + row[0] +'\r\n', 'UTF-8')
                    conn.commit()
                    return result
                else:
                    return bytes('PRIVMSG ' + c + ' :Cannot add any more partners, Zeev already has 3!\r\n', 'UTF-8')
            except ValueError:
                return bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <partner name>\r\n', 'UTF-8')
    elif command == '!clearpartners':
        cur.execute("UPDATE state SET p1='', p2='', p3='' WHERE date=?", (formatted,))
        conn.commit()
        result = bytes('PRIVMSG ' + c + ' :Back to soloqueue to destroy some nerds SwiftRage\r\n', 'UTF-8')
        return result
    elif command == '!getpartners' or command == '!partners':

        cur.execute("SELECT p1, p2, p3 FROM state WHERE date=?", (formatted,))
        row = cur.fetchone()
        if(row[0] == ''):
            return bytes('PRIVMSG ' + c + ' :Zeev is currently playing solos\r\n', 'UTF-8')
        elif(row[0]!='' and row[1] ==''):
            return bytes('PRIVMSG ' + c + ' :Zeev is currently duo-ing with: ' + row[0] + '\r\n', 'UTF-8')
        elif(row[0]!='' and row[1]!=''):
            return bytes('PRIVMSG ' + c + ' :Zeev is currently playing squads with ' + row[0] + ' and ' + row[1] + '\r\n', 'UTF-8')
        elif(row[0]!='' and row[1]!='' and row[2]!=''):
            return bytes('PRIVMSG ' + c + ' :Zeev is currently playing squads with ' + row[0] +', ' + row[1] + ' and ' + row[2] + '\r\n', 'UTF-8')
    elif command == '!newStream':
        cur.execute("SELECT * from state")
        row = cur.fetchone()
        if(row[0] == formatted):
            return bytes('PRIVMSG ' + c + ' :Woah, chill out man! Todays stream is still ongoing!\r\n', 'UTF-8')
        else:
            cur.execute("INSERT into totals VALUES(?, ?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            newrow = (formatted, 0, 0, 0, 0, 0, 0, '', '', '')
            cur.execute("INSERT into state VALUES(?, ? , ? , ? , ?, ?, ?, ?, ?, ?)", (newrow))
            test = str(row[0])
            print(formatted)
            cur.execute("DELETE FROM state WHERE date=?", (test,))
            conn.commit()
            return bytes('PRIVMSG ' + c + ' :A new day, a new stream. Time to crack some skulls SwiftRage\r\n', 'UTF-8')
        return
    elif command == '!adddeath':
        cur.execute("SELECT deaths FROM state")
        row = cur.fetchone()
        deaths = int(row[0])
        deaths = deaths+1
        cur.execute("UPDATE state SET deaths=? where date=?",(deaths,formatted))
        result = bytes('PRIVMSG ' + c + ' :Death added. This makes ' + deaths + ' dead Zeevs today. Get good DansGame\r\n', 'UTF-8')
        return result
    elif command == '!yesterday':
        cur.execute('SELECT * from totals where date=?', (yformatted,))
        row = cur.fetchone()
        print(row)
        result = bytes('PRIVMSG ' + c + ' : Recap for yesterday: ' + str(row[1]) + ' kills, ' + str(row[2]) + ' deaths, ' + str(row[3]) + ' wins, ' + str(row[4]) + ' losses, ' + str(row[5]) + ' burps, and ' + str(row[6]) + ' pees.\r\n','UTF-8')
        return result
    elif command == '!freemoney':
        result = bAAP()
        return bytes('PRIVMSG ' + c + ' :Arbitrage opportunity found - ' + result + '\r\n', 'UTF-8')
    elif command == '!latestvideo' or command == '!video' or command == '!youtube':
        result = bytes('PRIVMSG ' + c + ' : https://www.youtube.com/watch?v=hChsWxsoxgA <-Check out my latest highlight video! Editing courtesy of @xliattttt\r\n', 'UTF-8')
        return result
    elif command == '!giveaway':
        result = bytes('PRIVMSG ' + c + ' :When Zeev reaches 1000 followers he will be giving back to the community with a special giveaway. Just give the channel a follow and when 1000 followers are hit he will give the card out to a random follower WHO IS WATCHING THE STREAM!\r\n', 'UTF-8')
        return result
    elif command == '!roulette':
        x = random.randint(0, 6)
        print(str(x))
        if x == 0:
            return bytes('PRIVMSG ' + c + ' :/timeout ' + user + ' 60\r\n', 'UTF-8')
        else:
            return bytes('PRIVMSG ' + c + ' :You shall live to spam another day. You rolled a ' + str(x) + ' @' + user + ' - maybe buy a lottery ticket?\r\n', 'UTF-8')
    elif command == '!vanish':
        return bytes('PRIVMSG ' + c + ' :/timeout ' + user + ' 1\r\n', 'UTF-8')
    elif command == '!sens' or command == '!sensitivity':
        return bytes('PRIVMSG ' + c + ' : 1600 dpi, 0.03 in game\r\n', 'UTF-8')
    elif command == '!specs':
        return bytes('PRIVMSG ' + c + ' :MOUSE: Logitech Proteus Core G502 | KEYBOARD: Corsair Gaming K65 LUX RGB | MOUSEPAD: Corsair Gaming MM200 Medium | MIC: Blue Yeti | CAM: Logitech C920 | RIG: GTX 1070 Asus ROG Strix Am4 Motherboard Cryorig H7 Cpu Cooler Ryzen 5 3.6 GHz Team Group Dark 2 x 8 gb RAM | HEADSET: Hyper X Cloud Alpha Pro | MONITOR: Acer Predator XB241H-24, Nvidia G-Sync\r\n', 'UTF-8')
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
        return
        #return bytes('PRIVMSG ' + c + ' :DansGame I failed u sensei\r\n', 'UTF-8')

    # elif command == '!totalkills':
    #     result = bytes('PRIVMSG ' + c + ' :Zeev has pwned ' + str(state['total kills']) + ' noobs in his career PogChamp\r\n', 'UTF-8')
    #     return result

    # elif command == '!resetwinszb':
    #     state['wins'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Wins reset. A new day, a new opportunity to humilate people on the internet!\r\n', 'UTF-8')
    #     return result
    # elif command == '!resetburps':
    #     state['burps'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Burps reset. Grab some fizzy lifting drink.\r\n', 'UTF-8')
    #     return result
    # elif command == '!resetpees':
    #     state['pees'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Pees reset, go drink some water and hydrate.\r\n', 'UTF-8')
    #     return result
    # elif command == '!resetdeaths':
    #     state['deaths']  = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Deaths reset...are you trying to hide something? Kappa\r\n', 'UTF-8')
    #     return result
    # elif command == '!resetkills':
    #     state['kills'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Kills reset, bag em and tag em boys BCWarrior\r\n', 'UTF-8')
    #     return result

    # elif command == '!resetall' and user == 'sirlawlington':
    #     state['total kills'] = 0
    #     state['wintot'] = 0
    #     state['kills'] = 0
    #     state['burps'] = 0
    #     state['pees'] = 0
    #     state['wins'] = 0
    #     state['deaths'] = 0
    #     state['p1'] = ""
    #     state['p2'] = ""
    #     state['p3'] = ""
    #     state['numberpartners'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Everything reset, back to factory settings for me BibleThump\r\n', 'UTF-8')
    #     return result
 # elif command == '!addkill' or command == '!addkills':
    #     if(args == ''):
    #         state['kills'] = state['kills'] + 1
    #     else:
    #         try:
    #             state['kills'] = state['kills'] + int(args)
    #         except ValueError:
    #             result = bytes('PRIVMSG ' + c + ' :Improper usage. Try !addkill <number of kills>\r\n', 'UTF-8')
    #             return result
    #     result = bytes('PRIVMSG ' + c + ' :You have added ' + args + ' kills. So far Zeev has pwned ' + str(state['kills']) + ' lanyard wearing freshmen PogChamp\r\n', 'UTF-8')
    #     writeState(state)
    #     return result
# elif (command == '!clearkills' and user == 'sirlawlington'):
#     data = open("wins.txt", "w+")
#     data.write('TOTAL KILLS: 0')
#     return bytes('PRIVMSG ' + c + ' : Kills cleared\r\n', 'UTF-8')
   # elif command == '!clearpartners':
    #     state['p1'] = ""
    #     state['p2'] = ""
    #     state['p3'] = ""
    #     state['numberpartners'] = 0
    #     writeState(state)
    #     result = bytes('PRIVMSG ' + c + ' :Back to soloqueue to destroy some nerds SwiftRage\r\n', 'UTF-8')
    #     return result
    # elif command == '!addpartner':
    #     if (args == ''):
    #         result = bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <link to stream of other partner>\r\n', 'UTF-8')
    #         return result
    #     else:
    #         try:
    #             partner = str(args)
    #             if state['numberpartners'] == 0:
    #                 state['p1'] = partner
    #             elif state['numberpartners'] == 1:
    #                 state['p2'] = partner
    #             elif state['numberpartners'] == 2:
    #                 state['p3'] = partner
    #             state['numberpartners']= state['numberpartners'] + 1
    #             result = bytes('PRIVMSG ' + c + ' :Partner added\r\n', 'UTF-8')
    #         except ValueError:
    #             result = bytes('PRIVMSG ' + c + ' :Improper usage: try !addpartner <link to stream of other partner>\r\n', 'UTF-8')
    #             return result
    #     writeState(state)
    #     return result
    # elif command == '!getpartners' or command == '!partners':
    #     if state['numberpartners'] == 0:
    #         result = bytes('PRIVMSG ' + c + ' :Zeev is currently playing solos\r\n', 'UTF-8')
    #         return result
    #     elif state['numberpartners'] == 1:
    #         result = bytes('PRIVMSG ' + c + ' :Zeev is currently duo-ing with: ' + state['p1'] +'\r\n', 'UTF-8')
    #         return result
    #     elif state['numberpartners'] == 2:
    #         result = bytes('PRIVMSG ' + c + ' :Zeev is playing squads with: ' + state['p1'].rstrip() + ' and ' + state['p2'].rstrip() + '\r\n', 'UTF-8')
    #         return result
    #     elif state['numberpartners'] == 3:
    #         result = bytes('PRIVMSG ' + c + ' :Zeev is playing squads with: ' + state['p1'].rstrip() + ', ' + state['p2'].rstrip() + ' and ' + state['p3'].rstrip() + '\r\n', 'UTF-8')
    #         return result
    # elif command == '!addwin' or command == '!addwins':
    #     if(args == ''):
    #         state['wins'] = state['wins'] + 1
    #         state['wintot'] = state['wintot'] + 1
    #         result = bytes('PRIVMSG ' + c + ' :Win added. Zeev has ' + str(state['wins']) + ' wins right now\r\n', 'UTF-8')
    #     else:
    #         try:
    #             state['wins'] = state['wins'] + int(args)
    #             result = bytes('PRIVMSG ' + c + ' :Wins added, Zeev has ' + str(state['wins']) + ' wins right now, after adding those ' + str(args) + ' wins. What have you mods been up to?\r\n', 'UTF-8')
    #         except ValueError:
    #             result = bytes('PRIVMSG ' + c + ' :Improper usage. Try !addwin <number of kills> or just !addwin\r\n', 'UTF-8')
    #             return result
    #     writeState(state)
    #     return result
    # elif command == '!anywins':
    #     result = bytes('PRIVMSG ' + c + ' :Zeev has ' + str(state['wins']) + ' wins right now\r\n', 'UTF-8')
    #     return result