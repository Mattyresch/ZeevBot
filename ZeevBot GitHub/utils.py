import json
import urllib.request
import urllib.error
import time
import multiprocessing
import datetime
from datetime import timedelta
from datetime import datetime
import random
import socket
import sqlite3
from threading import Timer
from pprint import pprint
from bs4 import BeautifulSoup


def getFollowers():
    """Function used to get the number of followers for the stream, and display in chat.

    :return: Number of followers in a string along with the number of followers remaining until the giveaway, or nothing if error
    """
    try:
        key = loadTwitchAPI()
        response = json.load(urllib.request.urlopen("https://api.twitch.tv/kraken/channels/zeevtwitch?" + key))
        followers = response['followers']
        result = "Zeev has " + str(followers) + " followers at the moment!\r\n"
        # print(result)
        return result
    except urllib.error.URLError:
        print("timeout")
        return
def getUptime():
    """Function used to get the stream uptime by making a Twitch API call.

    :return: Uptime or timeout
    """
    try:
        key = loadTwitchAPI()
        uptime_json = json.load(urllib.request.urlopen("https://api.twitch.tv/kraken/streams/zeevtwitch?" + key))
        print(uptime_json['stream']['created_at'])
        start_time = uptime_json['stream']['created_at']
        start = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
        start = start - timedelta(hours=4)
        # test = start - timedelta(hours=4)
        # print(test)
        now = datetime.now()
        # print(now-test)
        uptime = now - start
        s = uptime.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours == 0:
            result = str(minutes) + " minutes and " + str(seconds) + " seconds\r\n"
        else:
            result = str(hours) + " hours and " + str(minutes) + " minutes.\r\n"
        print(result)
        return result
    except urllib.error.URLError:
        print("timeout")
        return
def loadTRNAPI():
    """Function used to load user-sensitive data, in this case the TRN API key

    :return: TRN API key from config.txt
    """
    data = open("config.txt", "r+")
    for line in data:
        temp = line
        if temp.startswith('TRN-API-KEY'):
            key = temp.partition(':')
    data.close()
    return key
def loadTwitchAPI():
    """Function used to load user-sensitive data, in this case the users Kraken API key

    :return: User Kraken API key from config.txt
    """
    data = open("config.txt", "r+")
    for line in data:
        temp = line
        if temp.startswith('client_id='):
            key = temp.rstrip()
    data.close()
    return key
def loadPass():
    """Function used to load user-sensitive data, in this case the oauth for twitch.tv

    :return: User oauth for twitch chat, from config.txt
    """
    data = open("config.txt", "r+")
    for line in data:
        temp = line
        if temp.startswith('oauth'):
            cfg = temp.rstrip()
    data.close()
    return cfg
def connect(owner, nick, channel, server, password, port, irc):
    """Function used to connect to a twitch channel via IRC, used for sending reminders

    :param owner: The "owner" of the bot
    :param nick: The name of the bot
    :param channel: The name of the channel you are connecting to
    :param server: The IRC server you are connecting to
    :param password: The password for the IRC bot
    :param port: The port to connect to
    :param irc: the irc connection object
    :return:
    """
    irc.send(bytes('PASS ' + password + '\r\n', 'UTF-8'))
    irc.send(bytes('USER ' + nick + '\r\n', 'UTF-8'))
    irc.send(bytes('NICK ' + nick + '\r\n', 'UTF-8'))
    irc.send(bytes('JOIN ' + channel + '\r\n', 'UTF-8'))
    irc.send(bytes("USER %s %s : %s \r\n" % (nick, server, nick), 'UTF-8'))
def compareNames(old):
    """Function used to compare two lists of names in order to distribute points.

    :param old: List of viewers who were present at last check
    :return: List of the viewers who are still present from time of last check, or error
    """
    new = getNames()
    try:
        intersect = set(old).intersection(new)
        print(intersect)
        return intersect
    except TypeError:
        return "error"
def addPoints(old):
    """Function used to add points to a list of users.

    :param old: List of viewers who were present at last check
    :return:
    """
    winners = compareNames(old)
    if winners == "error":
        return
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    for w in winners:
        cur.execute("SELECT * FROM users WHERE name LIKE ?", (w,))
        row = cur.fetchone()
        try:
            newpoints = int(row[1]) + 5
            cur.execute("UPDATE users SET points=? WHERE name=?", (newpoints, w))
            print("User " + w + " has " + str(newpoints) + " points now")
            conn.commit()
        except TypeError:
            cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (w, 5, 0, 0, 0, 0))
            conn.commit()
    conn.close()
    return
def addMessage(user):
    """Function used to add points to a user when they make a post in chat.

    :param user: The user who made the post
    :return:
    """
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name LIKE ?", (user,))
    row = cur.fetchone()
    try:
        newpoints = int(row[1]) + 1
        newmsgs = int(row[2]) + 1
        cur.execute("UPDATE users SET points=?, messages=? WHERE name=?", (newpoints, newmsgs, user))
        conn.commit()
    except TypeError:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (user, 1, 1, 0, 0, 0))
        conn.commit()
    conn.close()
    return
def reminder(usr, msg, c):
    """Function used to set a reminder for the streamer.

    :param usr: user sending the reminder
    :param msg: the message the user is sending
    :param c: the channel the user is sending it to
    :return:
    """
    owner = 'SirLawlington'
    nick = 'zeevBOT'
    channel = '#zeevtwitch'
    server = 'irc.twitch.tv'
    password = loadPass()

    port = 6667
    irc = socket.socket()
    irc.connect((server, port))
    connect(owner, nick, channel, server, password, port, irc)
    irc.send(bytes('PRIVMSG ' + c + '  :' + str(usr) + ' sent you a reminder, here it is: ' + str(msg) + '\r\n', 'UTF-8'))
    return
def getNames():
    """Function used to get the current viewers for the stream.

    :return: List of viewers OR timeout
    """
    try:
        viewer_string = json.load(urllib.request.urlopen("https://tmi.twitch.tv/group/user/zeevtwitch/chatters"))
        viewers = viewer_string['chatters']['moderators'] + viewer_string['chatters']['viewers']
        #print("Current viewers: " + str(viewers))
        return viewers
    except urllib.error.URLError:
        print("timeout")
        return
def bP(t):
    """Function used to get basic arb pairs on bittrex crypto exchange

    :param t: token that you're getting an arb for if available
    :return: A string of arb opportunity OR timeout
    """
    now = datetime.now()
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
    """Function used to call bP() for multiple tokens if one fails.

    :return: The first arb pair available
    """
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
    """Function used to evaluate if a message is a command or not.

    :param msg: Message which is being evaluated from IRC chat
    :return: a dict containing the command part, and args part of evaluated message
    """
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
    """Function used to check if a user has privilege to use the bot commands.

    :param user: User who is being checked
    :return: 1 if user is a mod, 0 if they are not
    """
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
def correctTriviaQuestion(user, channel):
    """Function used to award points and increment things when a trivia question is answered correctly

    :param user: user who got the question right
    :param channel: channel name
    :return: response message
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT difficulty FROM trivia")
    r = c.fetchone()
    difficulty = r[0]
    c.execute("SELECT * FROM users WHERE name=?", (user,))
    res = c.fetchone()
    balance = res[1]
    if difficulty=='easy':
        reward = 75
    elif difficulty=='medium':
        reward = 150
    elif difficulty=='hard':
        reward = 250
    else:
        reward = 75
    newbal = balance + reward
    wins = res[5]
    wins += 1
    c.execute("UPDATE users SET points=?, trivia_wins=? WHERE name=?", (newbal, wins, user))
    c.execute("SELECT count FROM trivia")
    temp = c.fetchone()
    count = temp[0]
    print(count)
    if count == 2:
        result = bytes('PRIVMSG ' + channel + ' :@' + user + ' got the final trivia question right for this game, taking home '+ str(reward) +' Zeevbux!\r\n','UTF-8')
        c.execute("UPDATE trivia SET q1=' ', q2=' ', q3=' ', a1=' ', a2=' ', a3=' ', count=0, difficulty=' '")
        c.execute("UPDATE flags SET trivia_flag=0")
        conn.commit()
        conn.close()
        print(result)
        return result
    elif count == 1:
        result = 'PRIVMSG ' + channel + ' :@' + user + ' got the 2nd question right, ' + str(reward) + ' Zeevbux are headed to your account! Next question: '
        c.execute("SELECT q3 FROM trivia")
        temp = c.fetchone()
        q = temp[0]
        result = result + q + '\r\n'
    elif count == 0:
        result = 'PRIVMSG ' + channel + ' :@' + user + ' got the 1st question right, ' + str(reward) + ' Zeevbux are headed to your account! Next question: '
        c.execute("SELECT q2 FROM trivia")
        temp = c.fetchone()
        q = temp[0]
        result = result + q + '\r\n'
    count += 1
    c.execute("UPDATE trivia SET count=?", (count,))
    conn.commit()
    conn.close()
    print(result)
    return bytes(result, 'UTF-8')
def checkAnswers(message):
    """Function used to check the message for the answer to the current trivia question.

    :param message: message to search for the answer in
    :return: 1 if right, 0 if wrong
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trivia")
    result = c.fetchone()
    round_number = int(result[6])
    message = str(message).lower()
    if round_number == 0:
        answer = result[3]
    elif round_number == 1:
        answer = result[4]
    elif round_number == 2:
        answer = result[5]
    answer = str(answer).lower()
    if message.find(answer) != -1:
        print('yay u got it right')
        return 1
    else:
        return 0
def getCurrentQuestion(channel):
    """Function used to get the current question

    :param channel: channel to post response to
    :return: response message string
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trivia")
    result = c.fetchone()
    round_number = int(result[6])
    question = str('PRIVMSG ' + channel + ' : ' + result[round_number])
    print(question)
    return question
def getTriviaQuestions(args):
    """Function used to to pull trivia questions from the API and move them into DB. !trivia <category> <difficulty>

    :return: response message
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT trivia_flag FROM flags")
    r = c.fetchone()
    flag = r[0]
    accepted_categories = {'sports', 'videogames', 'general', 'movies', 'games'}
    accepted_difficulties = {'easy', 'medium', 'hard'}
    if flag == 1:
        msg = ' :Trivia game already in progress!\r\n'
        conn.close()
        return(msg)
    if (args == ''):
        response = json.load(urllib.request.urlopen('https://opentdb.com/api.php?amount=3&category=15&difficulty=easy&type=multiple'))
        difficulty = 'easy'
    else:
        temp = str(args).partition(' ')
        difficulty = temp[2]
        category = temp[0]
        print(category)
        print(difficulty)
        if category not in accepted_categories:
            response = json.load(urllib.request.urlopen('https://opentdb.com/api.php?amount=3&category=15&difficulty=easy&type=multiple'))
        else:
            if category == 'sports':
                cat_num = 21
            elif category == 'videogames' or category=='games':
                cat_num = 15
            elif category == 'movies':
                cat_num = 11
            else:
                cat_num = 9
            if difficulty not in accepted_difficulties:
                difficulty = 'easy'
            response = json.load(urllib.request.urlopen('https://opentdb.com/api.php?amount=3&category='+str(cat_num)+'&difficulty='+str(difficulty)+'&type=multiple'))
            # response = json.load(urllib.request.urlopen('https://opentdb.com/api.php?amount=3&category=15&difficulty=easy&type=multiple'))
    print(response)
    count = 0
    result = []
    for i in response['results']:
        q = str(BeautifulSoup(i['question'], "html.parser"))
        a = str(BeautifulSoup(i['correct_answer'], "html.parser"))
        if q.startswith("Which"):
            count = 0
            x = random.randint(0, 2)
            print(x)
            for j in i['incorrect_answers']:
                # print(j)
                if count == x:
                    q = q + " " + str(a) + ", "
                if count == 2:
                    q = q + " " + j
                else:
                    q = q + " " + j + ", "
                count+=1
        q = str(BeautifulSoup(q, "html.parser"))
        temp = (q, a)
        result.append(temp)
    print(result)
    q1 = result[0][0]
    q2 = result[1][0]
    q3 = result[2][0]
    a1 = result[0][1]
    a2 = result[1][1]
    a3 = result[2][1]
    c.execute("UPDATE trivia SET q1=?, q2=?, q3=?, a1=?, a2=?, a3=?, count=0, difficulty=?", (q1, q2, q3, a1, a2, a3, difficulty))
    c.execute("UPDATE flags SET trivia_flag=1")
    conn.commit()
    conn.close()
    msg = ' :Trivia started! First question: ' + q1 + '\r\n'
    return msg
def skipTriviaQuestion(user, channel):
    """Function used to skip a trivia question

    :param user: user skipping the question
    :param channel: channel name
    :return: result string
    """
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT count FROM trivia")
    r = c.fetchone()
    temp = r[0]
    print(temp)
    if temp == 2:
        result = 'PRIVMSG ' + channel + ' :@' + user + ' gave up on the final question, what a quitter DansGame\r\n'
        c.execute("UPDATE trivia SET q1=' ', q2=' ', q3=' ', a1=' ', a2=' ', a3=' ', count=0")
        c.execute("UPDATE flags SET trivia_flag=0")
        conn.commit()
        conn.close()
        print(result)
        return result
    else:
        new_count = r[0] + 1
        c.execute("UPDATE trivia SET count=?", (new_count, ))
        c.execute("SELECT q2, q3 FROM trivia")
        r2 = c.fetchone()
        result = 'PRIVMSG ' + channel + ' :@' + user + ' gave up on the question, on to the next one ResidentSleeper '
        if new_count==1:
            q = r2[0]
        elif new_count==2:
            q = r2[1]
        result = result + q + '\r\n'
        conn.commit()
        conn.close()
        print(result)
        return result
def execute(command, args, user):
    """Function used to execute the command given for the given params

    :param command: Command to execute
    :param args: Args to pass for command
    :param user: User who is passing the command
    :return: The result string for that command
    """
    c = '#zeevtwitch'
    #check = checkPriv(user)
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    #print(check)
    date = datetime.now()
    user = str(user).lower()
    formatted = date.strftime("%Y-%m-%d")
    yesterday = datetime.today() - timedelta(days=1)
    yformatted = yesterday.strftime("%Y-%m-%d")
    command = str(command).lower()
    if command == '!woof':
        result = bytes('PRIVMSG ' + c + ' :FrankerZ\r\n', 'UTF-8')
    elif command == '!trivia' or command == '!starttrivia':
        result = 'PRIVMSG ' + c
        temp = getTriviaQuestions(args)
        result = bytes(result + temp, 'UTF-8')
    elif command == '!question' or command == '!currentquestion':
        result = bytes(getCurrentQuestion(c) + '\r\n', 'UTF-8')
    elif command == '!skip' or command == '!skipquestion':
        result = bytes(skipTriviaQuestion(user, c), 'UTF-8')
    elif command == '!woodenspoon':
        result = bytes('PRIVMSG ' + c + ' :You made ' + str(user) + ' mad--better run quick, they are going to get the wooden spoon!\r\n', 'UTF-8')
    elif command == '!help' or command == '!commands':
        result = bytes('PRIVMSG ' + c + ' :Command help for me is found here: https://pastebin.com/8KFMTMfE \r\n', 'UTF-8')
    elif command == '!sorry':
        result = bytes('PRIVMSG ' + c + ' :Sorry my owner killed you. I would have done it myself, but I have no hands BibleThump\r\n', 'UTF-8')
    elif command == '!uptime':
        temp = getUptime()
        result = bytes('PRIVMSG ' + c + ' :Zeev has been streaming for ' + temp, 'UTF-8')
    elif command == '!followers':
        temp = getFollowers()
        result = bytes('PRIVMSG ' + c + ' : ' + temp, 'UTF-8')
    elif command == '!stats':
        cur.execute("SELECT * FROM global_totals")
        r = cur.fetchone()
        temp = totals(int(r[0]), int(r[1]), str(r[2]), int(r[3]), float(r[4]), float(r[5]), str(r[6]))
        #temp.printAll()
        s = temp.chatMsg()
        print(s)
        result = bytes('PRIVMSG ' + c + s, 'UTF-8')
    elif command == '!multitwitch' or command == '!multi':
        cur.execute("SELECT p1, p2, p3 FROM state WHERE date=?", (formatted,))
        row = cur.fetchone()
        if (row[0] == ''):
            result = bytes('PRIVMSG ' + c + ' :Zeev is currently playing solos\r\n', 'UTF-8')
        elif (row[0] != '' and row[1] == ''):
            result = bytes('PRIVMSG ' + c + ' :Zeev and his partners on multitwitch! http://multitwitch.tv/zeevtwitch/' + row[0] + '\r\n', 'UTF-8')
        elif (row[0] != '' and row[1] != ''):
            result = bytes('PRIVMSG ' + c + ' :Zeev and his partners on multitwitch! http://multitwitch.tv/zeevtwitch/' + row[0] + '/' + row[1] + '\r\n', 'UTF-8')
        elif (row[0] != '' and row[1] != '' and row[2] != ''):
            result = bytes('PRIVMSG ' + c + ' :Zeev and his partners on multitwitch! http://multitwitch.tv/zeevtwitch/' + row[0] + '/' + row[1] + '/' + row[2] + '\r\n', 'UTF-8')
    elif command == '!tracker':
        result = bytes('PRIVMSG ' + c + ' : https://fortnitetracker.com/profile/pc/twitchzeevtwitch <- click here for stats\r\n', 'UTF-8')
    elif command == '!bailout':
        cur.execute("SELECT points FROM users WHERE name=?", (user,))
        check = cur.fetchone()
        print(check)
        if check[0] < 100:
            cur.execute("UPDATE users SET points=100 WHERE name=?", (user,))
            conn.commit()
            result = bytes('PRIVMSG ' + c + ' :HEY EVERYONE, LOOK AT HOW POOR @' + user + ' is! Here\'s your 100 ZeevBux bailout, you degenerate gambler Kappa\r\n', 'UTF-8')
        else:
            result = bytes('PRIVMSG ' + c + ' :Sorry, but you are not broke enough to qualify for a bailout yet, try gambling some more!\r\n', 'UTF-8')
    elif command == '!sendzeevbux' or command == '!send':
        if (args==''):
            result = bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then try sending again with !send <user> <amount>.\r\n', 'UTF-8')
        else:
            temp = str(args).partition(' ')
            try:
                user = user.strip('@')
                cur.execute("SELECT points FROM users WHERE name=?", (user,))
                check = cur.fetchone()
                print(check)
                amt_in_acc = int(check[0])
                amt_sent = int(temp[2])
            except ValueError:
                if str(temp[2]) == 'all':
                    cur.execute("SELECT points FROM users WHERE name=?", (user,))
                    check = cur.fetchone()
                    amt_sent = int(check[0])
                    amt_in_acc = amt_sent
                else:
                    return bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Try !send <recipient><amount>\r\n', 'UTF-8')
            if amt_sent <= 0:
                result = bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Cannot send a non-positive amount of ZeevBux.\r\n', 'UTF-8')
            elif amt_sent > amt_in_acc:
                result = bytes('PRIVMSG ' + c + ' :@' + user + ' ERROR: Cannot send more ZeevBux than you have in your account. Check your balance before trying again.\r\n', 'UTF-8')
            elif temp[0] == user:
                result = bytes('PRIVMSG ' + c + ' :@' + user + ' ERROR: Cannot send Zeevbux to yourself\r\n', 'UTF-8')
            else:
                sender_new_bal = amt_in_acc - amt_sent
                recipient = str(temp[0]).lower()
                cur.execute("SELECT points FROM users WHERE name=?", (recipient,))
                check = cur.fetchone()
                print(check)
                if check==None:
                    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (recipient, amt_sent, 0, 0, 0, 0))
                else:
                    recipient_new_bal = int(check[0]) + amt_sent
                    cur.execute("UPDATE users SET points=? WHERE name=?", (recipient_new_bal, recipient))
                cur.execute("UPDATE users SET points=? WHERE name=?", (sender_new_bal, user))
                conn.commit()
                result = bytes('PRIVMSG ' + c + ' :@' + user + ' just sent ' + str(amt_sent) + ' Zeevbux to @' + recipient + '.\r\n', 'UTF-8')
    elif command == '!wager' or command == '!bet':
        cur.execute("SELECT bet_flag FROM flags")
        value = cur.fetchone()
        flag = value[0]
        if flag == 0:
            return bytes('PRIVMSG ' + c + ' :@' + user + ' sorry, but betting has been closed for this game.\r\n', 'UTF=8')
        accepted_bets = {'win', 'loss', 'over', 'under'}
        if (args == ''):
            result = bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then place a wager using <!wager or !bet> <amount or "all"><over/under/win/loss>\r\n', 'UTF-8')
        else:
            temp = str(args).partition(' ')
            try:
                cur.execute("SELECT points FROM users WHERE name=?", (user,))
                wager = int(temp[0])
                if(wager<=0):
                    return bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then place a wager using <!wager or !bet> <amount or "all"><over/under/win/loss>\r\n', 'UTF-8')
                balance = cur.fetchone()
                bal = int(balance[0])
            except ValueError:
                if str(temp[0]) == 'all':
                    cur.execute("SELECT points FROM users WHERE name=?", (user,))
                    balance = cur.fetchone()
                    wager = int(balance[0])
                    bal = int(balance[0])
                else:
                    return bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then place a wager using <!wager or !bet> <amount or "all"><over/under/win/loss>\r\n', 'UTF-8')
            type = temp[2]
            if type not in accepted_bets:
                return bytes('PRIVMSG ' + c + ' :@' + user + ' improper usage. Check your balance with !zeevbux, then place a wager using <!wager or !bet> <amount or "all"><over/under/win/loss>\r\n','UTF-8')
            print(str(wager) + " : " + str(balance[0]) + " : " + type)
            if wager <= bal:
                if type=='win' or type=='loss':
                    checks = {'win', 'loss'}
                    cur.execute("SELECT * from open_bets WHERE name=?", (user,))
                    temp = cur.fetchall()
                    for b in temp:
                        if b[3] in checks:
                            return bytes('PRIVMSG ' + c + ' :@' + user + ' user already has a bet open on type win/loss. Try over/under, or just wait for Tyler to finish this round.\r\n', 'UTF-8')
                    cur.execute("SELECT win_percentage FROM global_totals")
                    r = cur.fetchone()
                    winloss = r[0]
                    print(winloss)
                    wl = int(winloss[0:2])
                    if type =='win':
                        payout = int(wager + wager*(100/wl))
                        newbal = bal - wager
                    elif type =='loss':
                        payout = int(wager + wager*(wl/100))
                        newbal = bal - wager
                    # cur.execute("SELECT wins, losses FROM state WHERE date=?", (formatted,))
                    # winloss = cur.fetchone()
                    # try:
                    #     payout = int((wager * (winloss[1] / winloss[0])) + wager)
                    #     newbal = bal - wager
                    # except ZeroDivisionError:
                    #     payout = wager * 1.5
                    #     newbal = bal - wager
                    # except TypeError:
                    #     payout = bal * (1.5)
                    #     newbal = 0
                    #     wager = bal
                    print(user + " bet " + str(wager) + " expected payout of " + str(payout) + " on bet type " + type)
                    cur.execute("INSERT INTO open_bets VALUES (?, ?, ?, ?)", (user, wager, payout ,type))
                    cur.execute("UPDATE users SET points=? WHERE name=?", (newbal, user))
                    result = bytes('PRIVMSG ' + c + ' :@' + user + ' just bet ' + str(wager) + ' ZeevBucks that Zeev will get a ' + type + ' their next game, with an expected payout of ' + str(payout) + ' if they are right\r\n', 'UTF-8')
                elif type=='over' or type=='under':
                    checks = {'under', 'over'}
                    cur.execute("SELECT * from open_bets WHERE name=?", (user,))
                    temp = cur.fetchall()
                    for b in temp:
                        if b[3] in checks:
                            return bytes('PRIVMSG ' + c + ' :@' + user + ' user already has a bet open on type over/under. Try win/loss, or just wait for Tyler to finish this round.\r\n', 'UTF-8')
                    # cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
                    # killdeath = cur.fetchone()
                    cur.execute("SELECT kdr FROM global_totals")
                    r = cur.fetchone()
                    kd = r[0]
                    # try:
                    #     kd = killdeath[0]/killdeath[1]
                    # except TypeError:
                    #     kd = 5
                    # except ZeroDivisionError:
                    #     kd = 5
                    payout = int(wager + int(wager * (1/kd)))
                    newbal = bal - wager
                    print(user + " bet " + str(wager) + " expected payout of " + str(payout) + " on bet type " + type)
                    cur.execute("UPDATE users SET points=? WHERE name=?", (newbal, user))
                    cur.execute("INSERT INTO open_bets VALUES (?, ?, ?, ?)", (user, wager, payout ,type))
                    result = bytes('PRIVMSG ' + c + ' :@' + user + ' just bet ' + str(wager) + ' ZeevBucks that Zeev will get ' + type + ' their average kills next game, with an expected payout of ' + str(payout) + ' if they are right\r\n', 'UTF-8')
            else:
                result = bytes("PRIVMSG " + c + ' :Insufficient balance. Check your ZeevBucks amount again before placing a bet.\r\n', 'UTF-8')
            # print("You bet " + str(wager) + " on bet type " + str(type))
    elif command == '!odds':
        cur.execute("SELECT kdr, win_percentage FROM global_totals")
        r = cur.fetchone()
        kd = r[0]
        winper = r[1]
        wl = winper[0:2]
        win_odd = round(100/int(wl), 2)
        lose_odd = round(int(wl)/100, 2)
        over_odd = round(1/int(kd), 2)
        result = bytes('PRIVMSG ' + c + ' : Estimated payout for !wager <win> : wager + (wager * ' + str(win_odd) + ') !wager <loss> : wager + (wager * ' + str(lose_odd) +') !wager <over/under> : wager + (wager * ' + str(over_odd) + ')\r\n', 'UTF-8')
    elif command == '!totalwins':
        cur.execute("SELECT SUM(wins) FROM totals")
        row = cur.fetchone()
        wins = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Total wincount for Zeevtwitch: ' + wins + '\r\n', 'UTF-8')
    elif command == '!top5':
        cur.execute("SELECT * FROM users WHERE NAME NOT LIKE '%BOT' AND NAME NOT LIKE '%zeevtwitch' ORDER BY points DESC LIMIT 5")
        rows = cur.fetchall()
        count = 0
        for r in rows:
            count += 1
            if count == 1:
                res_str = " :1st: @" + r[0] + " ZeevBux: " + str(r[1])
            elif count == 2:
                res_str += ", 2nd: @" + r[0] + " ZeevBux: " + str(r[1])
            elif count == 3:
                res_str += ", 3rd: @" + r[0] + " ZeevBux: " + str(r[1])
            elif count == 4:
                res_str += ", 4th: @" + r[0] + " ZeevBux: " + str(r[1])
            elif count == 5:
                res_str += ", 5th: @" + r[0] + " Zeevbux: " + str(r[1]) + "\r\n"
        result = bytes('PRIVMSG ' + c + res_str, 'UTF-8')
        print(result)
    elif command == '!burpcount':
        cur.execute("SELECT burps FROM state")
        row = cur.fetchone()
        burps = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has burped ' + burps + ' times without saying excuse me, this stream alone. Tsk tsk.\r\n', 'UTF-8')
    elif command == '!zeevbux' or command == '!zeevbucks' or command == '!balance':
        cur.execute("SELECT points FROM users WHERE name=?", (user,))
        balance = cur.fetchone()
        print(user)
        print(str(balance[0]))
        result = bytes('PRIVMSG ' + c + ' :/w ' + user + ' Welcome to ZeevBank! You currently have ' + str(balance[0]) + ' ZeevBux in your account.\r\n', 'UTF-8')
    elif command == '!pottycount':
        cur.execute("SELECT pees FROM state")
        row = cur.fetchone()
        pees = str(row[0])
        result = bytes('PRIVMSG ' + c + ' :Zeev has peed ' + pees + ' times this stream. Think he washed his hands? Kappa \r\n', 'UTF-8')
    elif command == '!whispertest':
        result = bytes('PRIVMSG ' + c + ' :/w ' + user + ' Wait till u see my oh\r\n', 'UTF-8')
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
    elif command == '!refund':
        cur.execute("SELECT name, wager FROM open_bets")
        bets = cur.fetchall()
        for b in bets:
            name = b[0]
            wager = b[1]
            cur.execute("SELECT points FROM users WHERE name=?", (name,))
            bal = cur.fetchone()
            new_bal = int(bal[0])
            new_bal = new_bal + int(wager)
            cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
        cur.execute("DELETE from open_bets")
        result = bytes('PRIVMSG ' + c + ' :bets refunded, something must have gone wrong.\r\n', 'UTF-8')
    elif command == '!addloss':
        cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
        killdeath = cur.fetchone()
        try:
            kills = int(args)
        except ValueError:
            kills = 0
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
            # print(b)
            # print(b.keys())
            # row = cur.fetchone()
            name = b[0]
            reward = b[1]
            bet_type = b[2]
            print(bet_type + " : " + name + " : " + str(reward))
            balance = cur.execute("SELECT points FROM users WHERE name=?", (name,))
            bal = cur.fetchone()
            initial_bal = bal[0]
            if bet_type == 'under':
                if (kills <= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'over':
                if (kills >= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'loss':
                new_bal = initial_bal + reward
                cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
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
        result = bytes('PRIVMSG ' + c + ' :You have added a loss and ' + str(kills) + ' kills. So far, Zeev has ' + str(
            losses) + ' this stream.\r\n', 'UTF-8')
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
    elif command == '!mywagers' or command == '!mybets':
        bets = cur.execute("SELECT * FROM open_bets WHERE name=?", (user,))
        allbets=""
        for b in bets:
            allbets += "(Wager: " + str(b[1]) + " | Reward: " + str(b[2]) + " | Bet Type: " + str(b[3]) + ")"
            # print(b)
            # print(allbets)
        result = bytes('PRIVMSG ' + c + ' :Open bets for @' + user + ' '+ allbets + '\r\n', 'UTF-8')
    elif command == '!openbets' or command == '!openbetting':
        cur.execute("SELECT bet_flag FROM flags")
        value = cur.fetchone()
        flag = value[0]
        if flag == 0:
            cur.execute("UPDATE flags SET bet_flag=1")
            result = bytes('PRIVMSG ' + c + ' :Betting opened\r\n','UTF-8')
        else:
            result = bytes('PRIVMSG ' + c + ' :Betting has already been opened\r\n', 'UTF-8')
    elif command == '!closebets' or command == '!closebetting':
        cur.execute("SELECT bet_flag FROM flags")
        value = cur.fetchone()
        flag = value[0]
        if flag == 1:
            cur.execute("UPDATE flags SET bet_flag=0")
            result = bytes('PRIVMSG ' + c + ' :Betting closed\r\n', 'UTF-8')
        else:
            result = bytes('PRIVMSG ' + c + ' :Betting has already been closed\r\n', 'UTF-8')
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
            balance = cur.execute("SELECT points FROM users WHERE name=?", (row[0]),)
            print(balance)
            if row[3] == 'under':
                if(args <= kd):
                    new_bal = balance + int(row[2])
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, user))
            elif row[3] == 'over':
                if(args > kd):
                    new_bal = balance + int(row[2])
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, user))
    elif command == '!addwin' or command =='!addwins':
        cur.execute("SELECT kills, deaths FROM state WHERE date=?", (formatted,))
        killdeath = cur.fetchone()
        try:
            kills = int(args)
        except ValueError:
            return bytes('PRIVMSG ' + c + ' :Improper usage, try !addwin <number of kills>.\r\n', 'UTF-8')
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
            balance = cur.execute("SELECT points FROM users WHERE name=?", (name,))
            bal = cur.fetchone()
            initial_bal = bal[0]
            if bet_type == 'under':
                if(kills <= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'over':
                if(kills >= kd):
                    new_bal = initial_bal + reward
                    cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
                    print(name + " new balance: " + str(new_bal))
                    conn.commit()
                    continue
            elif bet_type == 'win':
                new_bal = initial_bal + reward
                cur.execute("UPDATE users SET points=? WHERE name=?", (new_bal, name))
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
    elif command == '!addpartner' or command == '!addpartners':
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
    elif command == '!clearpartners':
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
    elif command == '!newstream':
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
    elif command == '!feed':
        cur.execute('SELECT food from feed')
        row = cur.fetchone()
        food = row[0]
        print(food)
        food = food + 1
        cur.execute('UPDATE feed set food=?', (food,))
        conn.commit()
        result = bytes('PRIVMSG ' + c + ' : GivePLZ DoritosChip TakeNRG ' + str(food) + ' chips for me, no diabetes yet...feed me some RAM MrDestructoid\r\n', 'UTF-8')
    elif command == '!drank':
        cur.execute('SELECT drink from feed')
        row = cur.fetchone()
        drinks = row[0]
        print(drinks)
        drinks = drinks + 1
        cur.execute('UPDATE feed set drink=?', (drinks,))
        conn.commit()
        result = bytes('PRIVMSG ' + c + ' : FreakinStinkin HSCheers LUL ' + str(drinks) + ' drinks for me, robots cant get drunk...get me some oil human MrDestructoid\r\n', 'UTF-8')
    elif command == '!sourcecode':
        result = bytes('PRIVMSG ' + c + ' : View my source here, feel free to fork and offer suggestions to @Sirlawlington https://github.com/Mattyresch/ZeevBot\r\n', 'UTF-8')
    elif command == '!vanish':
        result = bytes('PRIVMSG ' + c + ' :/timeout ' + user + ' 1\r\n', 'UTF-8')
    elif command == '!sens' or command == '!sensitivity':
        result = bytes('PRIVMSG ' + c + ' : 1600 dpi, 0.03 in game\r\n', 'UTF-8')
    elif command == '!specs':
        result = bytes('PRIVMSG ' + c + ' :MOUSE: Logitech Proteus Core G502 | KEYBOARD: Corsair Gaming K65 LUX RGB | MOUSEPAD: Corsair Gaming MM200 Medium | MIC: Blue Yeti | CAM: Logitech C920 | RIG: GTX 1070 Asus ROG Strix Am4 Motherboard Cryorig H7 Cpu Cooler Ryzen 5 3.6 GHz Team Group Dark 2 x 8 gb RAM | HEADSET: Hyper X Cloud Alpha Pro | MONITOR: Acer Predator XB241H-24, Nvidia G-Sync\r\n', 'UTF-8')
    elif command == '!seasontotals':
        result = seasonTotals(c)
        return result
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
class totals:
    def __init__(self, newWins, newKills, newScore, newMatches, newKDR, newKPM, newWinPercentage):
        self.wins = newWins
        self.kills = newKills
        self.score = newScore
        self.matches = newMatches
        self.kdr = newKDR
        self.kpm = newKPM
        self.win_percentage = newWinPercentage
    def setkills(self, kills):
        self.kills = kills
    def setwins(self, wins):
        self.wins = wins
    def setscore(self, score):
        self.score = score
    def setmatches(self, matches):
        self.matches = matches
    def setkdr(self, kdr):
        self.kdr = kdr
    def setkpm(self, kpm):
        self.kpm = kpm
    def setwinpercent(self, winper):
        self.win_percentage = winper
    def printAll(self):
        result = (" : Wins: " + str(self.wins) + " Kills: " + str(self.kills) + " Score: " + str(self.score) + " Matches: " + str(self.matches) + " KDR: " + str(self.kdr) + " KPM: " + str(self.kpm) + " Win%: " + str(self.win_percentage))
        print(result)
    def chatMsg(self):
        result = " : Career stats - Wins: " + str(self.wins) + " Kills: " + str(self.kills) + " Score: " + str(self.score) + " Matches: " + str(self.matches) + " KDR: " + str(self.kdr) + " Win%: " + str(self.win_percentage) + '\r\n'
        print(result)
        return result


def seasonTotals(c):
    key = loadTRNAPI()
    req = urllib.request.Request('https://api.fortnitetracker.com/v1/profile/pc/ZeevTwitch')
    req.add_header(key[0], key[2])
    index1=[]
    index2=[]
    index3=[]
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    try:
        idk = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError:
        return
    result = 'PRIVMSG ' + c + ' :Solo stats: '
    for j in idk['stats']['curr_p2']:
        if idk['stats']['curr_p2'][j]['label'] == 'wins':
            result = result + "Wins: " + idk['stats']['curr_p2'][j]['value']
        elif idk['stats']['curr_p2'][j]['label'] == 'Score':
            result = result + " Score: " + idk['stats']['curr_p2'][j]['value']
        elif idk['stats']['curr_p2'][j]['label'] == 'K/d':
            result = result + " Kill/Death: " + idk['stats']['curr_p2'][j]['value']
        elif idk['stats']['curr_p2'][j]['label'] == 'Win %':
            result = result + " Win %: " + idk['stats']['curr_p2'][j]['value']
        elif idk['stats']['curr_p2'][j]['label'] == 'Kills':
            result = result + ' Kills : ' + idk['stats']['curr_p2'][j]['value'] + ' | '
        else:
            continue
    result = result + 'Duo stats: '
    for j in idk['stats']['curr_p10']:
        if idk['stats']['curr_p10'][j]['label'] == 'wins':
            result = result + "Wins: " + idk['stats']['curr_p10'][j]['value']
        elif idk['stats']['curr_p10'][j]['label'] == 'Score':
            result = result + " Score: " + idk['stats']['curr_p10'][j]['value']
        elif idk['stats']['curr_p10'][j]['label'] == 'K/d':
            result = result + " Kill/Death: " + idk['stats']['curr_p10'][j]['value']
        elif idk['stats']['curr_p10'][j]['label'] == 'Win %':
            result = result + " Win %: " + idk['stats']['curr_p10'][j]['value']
        elif idk['stats']['curr_p10'][j]['label'] == 'Kills':
            result = result + " Kills : " + idk['stats']['curr_p10'][j]['value'] + ' | '
        else:
            continue
    result = result + 'Squad stats: '
    for j in idk['stats']['curr_p9']:
        if idk['stats']['curr_p9'][j]['label'] == 'wins':
            result = result + "Wins: " + idk['stats']['curr_p9'][j]['value']
        elif idk['stats']['curr_p9'][j]['label'] == 'Score':
            result = result + " Score: " + idk['stats']['curr_p9'][j]['value']
        elif idk['stats']['curr_p9'][j]['label'] == 'K/d':
            result = result + " Kill/Death: " + idk['stats']['curr_p9'][j]['value']
        elif idk['stats']['curr_p9'][j]['label'] == 'Win %':
            result = result + " Win %: " + idk['stats']['curr_p9'][j]['value']
        elif idk['stats']['curr_p9'][j]['label'] == 'Kills':
            result = result + " Kills : " + idk['stats']['curr_p9'][j]['value'] + "\r\n"
        else:
            continue
    print(result)
    result = bytes(result, 'UTF-8')
    return result
def updateTotals():
    """Get up to date info from fortnite tracker API, write differences to DB

    :return:
    """
    #get updated info from the fortnite tracker API
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    key = loadTRNAPI()
    req = urllib.request.Request('https://api.fortnitetracker.com/v1/profile/pc/ZeevTwitch')
    req.add_header(key[0], key[2])
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    try:
        idk = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError:
        return
    index2 = []
    new = totals(0, 0, 0, 0, 0, 0, 0)
    try:
        for j in idk["lifeTimeStats"]:
            index2.append(j)
        # print(j)
    except KeyError:
        return
    # print(index2)
    for j in index2:
        if j['key'] == "Kills":
            new.setkills(int(j['value']))
        elif j['key'] == "Wins":
            new.setwins(int(j['value']))
        elif j['key'] == "Score":
            new.setscore(str(j['value']))
        elif j['key'] == "Matches Played":
            new.setmatches(int(j['value']))
        elif j['key'] == "Win%":
            new.setwinpercent(str(j['value']))
        elif j['key'] == "K/d":
            new.setkdr(float(j['value']))
        elif j['key'] == "Kills Per Min":
            new.setkpm(float(j['value']))
        else:
            continue
    c.execute("SELECT * from global_totals")
    r = c.fetchone()
    # print(r)
    old = totals(int(r[0]), int(r[1]), str(r[2]), int(r[3]), float(r[4]), float(r[5]), str(r[6]))
    old.printAll()
    # new.printAll()
    result = old
    if new.kills != old.kills:
        result.setkills(new.kills)
    if new.wins != old.wins:
        result.setwins(new.wins)
    if new.score != old.score:
        result.setscore(new.score)
    if new.matches != old.matches:
        result.setmatches(new.matches)
    if new.win_percentage != old.win_percentage:
        result.setwinpercent(new.win_percentage)
    if new.kdr != old.kdr:
        result.setkdr(new.kdr)
    if new.kpm != old.kpm:
        result.setkpm(new.kpm)
    c.execute("UPDATE global_totals SET kills=?, wins=?, score=?, matches=?, kdr=?, kpm=?, win_percentage=?", (result.kills, result.wins, result.score, result.matches, result.kdr, result.kpm, result.win_percentage))
    conn.commit()
    conn.close()
    result.printAll()
    return