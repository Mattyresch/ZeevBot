import sqlite3
conn = sqlite3.connect('bot.db')
c = conn.cursor()
# c.execute('''CREATE TABLE state(date text, kills integer, deaths integer, wins integer, losses integer, burps integer, pees integer, p1 text, p2 text, p3 text)''')
# c.execute('''CREATE TABLE wins(date text, kills integer, p1 text, p2 text, p3 text)''')
# c.execute('''CREATE TABLE losses(date text, kills integer, p1 text, p2 text, p3 text)''')
# c.execute('''CREATE TABLE totals(date text, kills integer, deaths integer, wins integer, losses integer, burps integer, pees integer)''')
# c.execute('''CREATE TABLE mods(name text)''')
# c.execute('''CREATE TABLE users(name text, points integer, messages integer,is_mod integer,is_sub integer,trivia_wins integer)''')
# c.execute('''CREATE TABLE open_bets(name text, wager integer, payout integer, type text)''')
# c.execute('''CREATE TABLE flags(bet_flag integer)''')
# c.execute('''CREATE TABLE global_totals(wins integer, kills integer, score text, matches integer, kdr real, kpm real, win_percentage text)''')
# c.execute("INSERT into global_totals VALUES(0, 0, ' ', 0, 0.0, 0.0, ' ')")
# c.execute("INSERT into flags VALUES (0)")
# mods = [("capta1n_cypher", ), ("casper026", ), ("dennischirino", ), ("forestna", ), ("frankonical", ),
#         ("geemctee", ), ("iamtrevormay", ), ("ianwass", ), ("killoginet", ), ("lieza", ), ("moozow", ), ("nbl_sniper", ),
#         ("nordicevan", ), ("ogkickback", ), ("ph0enixb1ood", ), ("poacher117", ), ("secko", ), ("sirlawlington", ),
#         ("tex99", ), ("thewhitegamer05", ), ("ukko", ), ("ultra_spaz", ), ("whale728", ), ("willsquill", ), ("xliattttt", ), ("yerrowfever", ), ("zeevbot", ), ("zeevtwitch")]
# c.executemany("INSERT INTO mods(name) VALUES (?)", mods)
# c.execute("UPDATE users SET points = 1000000 WHERE name='zeevtwitch'")
# c.execute("INSERT into state VALUES ('2018-04-05', 100, 14, 8, 4, 0, 0, '', '', '')")
# c.execute("UPDATE users SET is_mod=0, is_sub=0, trivia_wins=0")
# c.execute("ALTER TABLE flags ADD trivia_flag integer")
c.execute("UPDATE flags SET trivia_flag=0")
# c.execute('''CREATE TABLE trivia(q1 text, q2 text, q3 text, a1 text, a2 text, a3 text, count integer)''')
# c.execute("INSERT INTO trivia VALUES(' ', ' ', ' ', ' ', ' ', ' ', 0)")
conn.commit()
conn.close()