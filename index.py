from flask import Flask,render_template,request,url_for
import sqlite3,flask

app = Flask(__name__)

@app.route('/')
def transaction_home():
    return render_template('index.html')


@app.route('/Transaction')
def transaction(alertmessage=""):
	conn=dbConn()
	data=conn.execute("SELECT Name from userdata")
	userlist=generateOption(data)
	conn.close()
	return render_template('transaction.html',userlist=userlist,alertmessage=alertmessage)

@app.route('/Transaction_details',methods=['GET','POST'])
def transaction_details():
	sender=request.form.get('sender')
	receiver=request.form.get('receiver')
	sender=str(sender)
	receiver=str(receiver)
	amount=request.form.get('amount')
	amount=int(amount)
	if sender==receiver:
		return render_template("transactiondetails.html",option=2,sender=sender) 
	else:
		conn=dbConn()
		balance_sender=getdata(sender,conn)
		balance_receiver=getdata(receiver,conn)
		if amount==0:
			return render_template("transactiondetails.html",option=0)
		elif balance_sender<amount:
			return render_template("transactiondetails.html",option=1)
		else:
			balance_sender=balance_sender-amount
			balance_receiver=balance_receiver+amount
			conn.execute("UPDATE userdata SET Balance='"+str(balance_sender)+"' WHERE Name='"+sender+"'")
			conn.execute("UPDATE userdata SET Balance='"+str(balance_receiver)+"' WHERE Name='"+receiver+"'")
			addToHistory(conn,sender,receiver,amount)
			conn.commit()
			conn.close()
			return render_template("transactiondetails.html",option=3)	
			
	


@app.route('/Transaction_history')
def transactionHistory():
	conn=dbConn()
	data=conn.execute("SELECT Sender,Receiver,Amount from transactions")
	transactionlist=generateTransactionList(data)
	conn.close()
	return render_template('transactionHistory.html',data=transactionlist)	

@app.route('/userlist')
def userList():
	conn=dbConn()
	data=conn.execute("SELECT Name,Email,Balance from userdata")
	userlist=generateUserList(data)
	conn.close()	
	return render_template('userlist.html',userlist=userlist)

@app.route('/userdetails',methods=['GET','POST'])
def userDetails():
	user=request.form.get('user')
	user=str(user)
	conn=dbConn()
	userdata=conn.execute('SELECT Name,Email,Balance from userdata WHERE Name="'+user+'"')
	userdatalist=generateList(userdata)
	transactiondata=conn.execute('SELECT Sender,Receiver,Amount from transactions WHERE Sender="'+user+'"OR Receiver="'+user+'"')
	transactionlist=generateTransactionList(transactiondata)
	optionlist=generateOption(conn.execute('SELECT Name from userdata WHERE NOT Name="'+user+'"'))
	conn.close()
	senderdata=flask.Markup('<input type="hidden" id="sender" name="sender" value="'+user+'">')
	return render_template('userdetails.html',userdata=userdatalist,transactionlist=transactionlist,user=user,optionlist=optionlist,senderdata=senderdata)

def dbConn():
	return sqlite3.connect('data.sqlite')

def generateList(data):
	udata=''
	for row in data:
		udata+=flask.Markup("<tr>")
		for item in row:
			item=str(item)
			udata+=flask.Markup("<td>")+flask.Markup.escape(item)+flask.Markup("</td>")
		udata+=flask.Markup("</tr>")
	return udata	

def generateTransactionList(data):
	data=list(data)
	data.reverse()
	udata=''
	for row in data:
		udata+=flask.Markup("<tr>")
		for item in row:
			item=str(item)
			udata+=flask.Markup("<td>")+flask.Markup.escape(item)+flask.Markup("</td>")
		udata+=flask.Markup("</tr>")
	return udata

def generateUserList(data):
	udata=''
	for row in data:
		udata+=flask.Markup("<tr>")
		item=str(row[0])
		udata+=flask.Markup("<td>")+flask.Markup.escape(item)+flask.Markup("</td>")
		udata+=flask.Markup('<td><button name="user" type="submit" value="'+item+'">View</button></td>')
		udata+=flask.Markup("</tr>")
	return udata

def generateOption(data):
	udata=''
	for item in data:
		it=item[0]
		udata+=flask.Markup('<option value="'+it+'">')+flask.Markup.escape(it)+flask.Markup('</option>') 
	return udata

def addToHistory(conn,sender,receiver,amount):
	conn.execute("INSERT INTO transactions (Sender,Receiver,Amount) VALUES ('"+sender+"','"+receiver+"',"+str(amount)+")")

def getdata(name,conn):
	data=conn.execute("SELECT Balance from userdata WHERE Name LIKE '"+str(name)+"'")
	data=data.fetchone()
	data=data[0]
	return int(data)


if __name__=='__main__':
	app.run(debug=True)


