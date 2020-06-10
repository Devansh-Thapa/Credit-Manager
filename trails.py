import sqlite3

conn=sqlite3.connect('data.sqlite')
data=conn.execute("SELECT Name from userdata")
balance=conn.execute("SELECT Balance from userdata WHERE Name LIKE 'Devansh' ")
b=balance.fetchone()
#b=b[0]
print(b)
	