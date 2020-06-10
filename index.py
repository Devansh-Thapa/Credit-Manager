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
	s=str(sender)
	r=str(receiver)
	amount=request.form.get('amount')
	amount=int(amount)
	if s==r:
		return render_template("transactiondetails.html",option=2) 
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
	transactionlist=generateList(data)
	conn.close()
	return render_template('transactionHistory.html',data=transactionlist)	

@app.route('/userdata')
def userData():
	conn=dbConn()
	data=conn.execute("SELECT Name,Email,Balance from userdata")
	userlist=generateList(data)
	conn.close()	
	return render_template('userdata.html',userlist=userlist)


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


