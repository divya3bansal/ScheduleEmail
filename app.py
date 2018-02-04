import os
from flask import Flask, render_template, json, request,redirect,session,jsonify
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from celery import Celery
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

#CELERY configurations
app.config['CELERY_BROKER_URL'] = 'redis://localhost:8081/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:8081/0'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'flask@example.com'

# MySQL configurations
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'FlaskPythonApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

mail = Mail(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def getListOfUsersFromDB(eventid):
	conn = mysql.connect()
	cursor = conn.cursor()

        # execute the SQL query using execute() method.
        cursor.execute ("select user_emailid from tbl_user where event_id="+eventid)

        # fetch all of the rows from the query
        data = list(cursor.fetchall ())
	
	userlist=[]
        # print the rows
        for row in data :
                print row[0]
		userlist.append(row[0])

        # close the cursor object
        cursor.close ()

        # close the connection
        conn.close ()

        return userlist

def findTimeDiffInSeconds(timestamp):

	print "Timestamp ::: " + timestamp

	st = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')	
	#st = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
	print st

	current = datetime.now()
	print current

        diffInSeconds = st - current
        
	return int(diffInSeconds.total_seconds())

def queueEmailTask(eventid, timestamp, subject, emailbody):
    #This task is to be instantiated everytime a new entry is made in the DB Email table, it should 

    #time diff from current time in seconds
        timediff = findTimeDiffInSeconds(timestamp)
        print timediff

	send_async_email.apply_async(args=[eventid, subject, emailbody], countdown=timediff)


@app.route("/sendEmail")
def index():
	msg = Message('Hello', recipients = ['lakshay09022@gmail.com'])
	msg.body = "Hello Flask message sent from Flask-Mail"
	send_async_email.delay()
	return "Sent"

@celery.task
def send_async_email(eventid, subject, emailbody):
	print "Inside celery"
	with app.app_context():
		#fetch list of user for the particular event id, 
        	userlist = list(getListOfUsersFromDB(eventid))
	        for name in userlist:
			print name

		
    		#send email invoke function with delay equal to the time computed in the above step in seconds
		#for each of the above users in the fetched list
	        msg = Message(subject, recipients = userlist)
        	msg.body = emailbody

		#msg = Message('Hello', recipients = ['lakshay09022@gmail.com'])
		#msg.body = "Hello Flask message sent from Flask-Mail"
		mail.send(msg)

@app.route('/')
def main():
	return render_template('saveEmail.html')

@app.route('/save_emails')
def showSaveEmailForm():
	return render_template('saveEmail.html')

@app.route('/addUser')
def showAddUserForm():
        return render_template('saveUser.html')

@app.route('/addEmail',methods=['POST'])
def addEmail():
    try:
            _eventid = request.form['inputEventid']
	    _subject = request.form['inputSubject']
            _emailbody = request.form['inputEmailBody']
            _timestamp = request.form['inputTimestamp']

            print "Event ID : " + _eventid;
            print "Subject : " + _subject;
	    print "Email Body : " + _emailbody;
	    print "Timestamp : " + _timestamp;

	    conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_saveEmail',(_eventid, _subject,_emailbody,_timestamp))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                queueEmailTask(_eventid, _timestamp, _subject, _emailbody) 
		return "Scheduled the email !"
            else:
                return render_template('error.html',error = 'An error occurred!')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/addUser',methods=['POST'])
def addUser():
    try:
            _eventid = request.form['inputEventid']
            _username = request.form['inputUsername']
            _emailid = request.form['inputEmailid']

            print "Event ID : " + _eventid;
            print "Username : " + _username;
            print "Email ID : " + _emailid;

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_saveUser',(_eventid, _username,_emailid))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/addUser')
            else:
                return render_template('error.html',error = 'An error occurred!')

    except Exception as e:
    	return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(port=5002)
