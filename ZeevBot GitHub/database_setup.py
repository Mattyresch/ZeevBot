import sqlite3
conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute('''CREATE TABLE state(date text, kills integer, deaths integer, wins integer, losses integer, burps integer, pees integer, p1 text, p2 text, p3 text)''')
c.execute('''CREATE TABLE wins(date text, kills integer, p1 text, p2 text, p3 text)''')
c.execute('''CREATE TABLE losses(date text, kills integer, p1 text, p2 text, p3 text)''')
c.execute('''CREATE TABLE totals(date text, kills integer, deaths integer, wins integer, losses integer, burps integer, pees integer)''')
c.execute('''CREATE TABLE mods(name text)''')
c.execute('''CREATE TABLE points(name text, points integer, messages integer)''')
c.execute('''CREATE TABLE open_bets(name text, wager integer, payout integer, type text)''')
c.execute('''CREATE TABLE flags(bet_flag integer)''')
c.execute("INSERT into flags VALUES (0)")
mods = [("capta1n_cypher", ), ("casper026", ), ("dennischirino", ), ("forestna", ), ("frankonical", ),
        ("geemctee", ), ("iamtrevormay", ), ("ianwass", ), ("killoginet", ), ("lieza", ), ("moozow", ), ("nbl_sniper", ),
        ("nordicevan", ), ("ogkickback", ), ("ph0enixb1ood", ), ("poacher117", ), ("secko", ), ("sirlawlington", ),
        ("tex99", ), ("thewhitegamer05", ), ("ukko", ), ("ultra_spaz", ), ("whale728", ), ("willsquill", ), ("xliattttt", ), ("yerrowfever", ), ("zeevbot", ), ("zeevtwitch")]
c.executemany("INSERT INTO mods(name) VALUES (?)", mods)
c.execute("INSERT into state VALUES ('2018-04-05', 100, 14, 8, 4, 0, 0, '', '', '')")
conn.commit()
conn.close()