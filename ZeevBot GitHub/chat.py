from utils import *
import time
import random
import socket
import threading
import string
import sys
import json
import urllib.request
import time
import multiprocessing
import datetime
from pprint import pprint

conn = sqlite3.connect('bot.db')
cur = conn.cursor()
owner ='SirLawlington'
nick = 'zeevBOT'
channel ='#zeevtwitch'
server = 'irc.twitch.tv'
password = loadPass()
port = 6667
inputBuffer=""
irc = socket.socket()
irc.connect((server, port))
irc.send(bytes('PASS ' + password + '\r\n', 'UTF-8'))
irc.send(bytes('USER ' + nick + '\r\n', 'UTF-8'))
irc.send(bytes('NICK ' + nick + '\r\n', 'UTF-8'))
# irc.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'UTF-8'))
# irc.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))
irc.send(bytes('JOIN ' + channel + '\r\n', 'UTF-8'))
irc.send(bytes("USER %s %s : %s \r\n" %(nick, server, nick), 'UTF-8'))
irc.send(bytes('PRIVMSG ' + channel + ' :WHAT\'S UP MY FLIM FLAMS, EVERYONE\'S FAVORITE SKYNET BETA IS IN THE HOUSE!\r\n', 'UTF-8'))
last = getNames()
updateTotals()
while 1:
    ircmessage = irc.recv(2048).decode("UTF-8", errors="ignore")
    ircmessage = ircmessage.strip('\n\r')
    #break message into two parts: user and message
    #stored in dict, keys are 'user' and 'msg'
    if ircmessage.find('PING') != -1:
        irc.send(bytes('PONG ' + server + '\r\n', 'UTF-8'))
        ##compareNames(last)
        addPoints(last)
        updateTotals()
        last = getNames()
        x = random.randint(0, 4)
        if x == 0:
            msg = bytes('PRIVMSG ' + channel + ' : Go follow Zeev\'s insta so you can see cool pics and stuff! Instagram: zeevgram\r\n','UTF-8')
        elif x == 1:
            msg = bytes('PRIVMSG ' + channel + ' :  Checkout Zeev\'s latest montage here! Don\'t forget to like and sub! https://youtu.be/hChsWxsoxgA \r\n', 'UTF-8')
        elif x == 2:
            msg = bytes('PRIVMSG ' + channel + ' : Don\'t forget to checkout our discord to get more involved with the stream! https://discord.gg/bGScpua \r\n', 'UTF-8')
        elif x == 3:
            msg = bytes('PRIVMSG ' + channel + ' :Feel free to follow the twitter for stream updates and general useless thoughts! twitter.com/zeevtweets \r\n', 'UTF-8')
        elif x == 4:
            msg = bytes('PRIVMSG ' + channel + ' : Add the snapchat so Zeev can see all of your beautiful faces lul: zeevsnap \r\n', 'UTF-8')
        irc.send(msg)
    parsed = parse(ircmessage)
    print(parsed['user'] + ':' + parsed['msg'])
    evaluated = evaluate(parsed['msg'])
    try:
        if evaluated['command'] == 'NONE':
            addMessage(parsed['user'])
            cur.execute("SELECT trivia_flag FROM flags")
            r = cur.fetchone()
            trivia_flag = r[0]
            if trivia_flag == 1:
                check = checkAnswers(parsed['msg'])
                if check == 1:
                    output = correctTriviaQuestion(parsed['user'], channel)
                    irc.send(output)
            continue
        else:
         output = execute(evaluated['command'], evaluated['args'], parsed['user'])
         irc.send(output)
         continue
    except TypeError:
        continue

