import smtplib
import random
import os
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.mysql import MySQL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mysql = MySQL()
app = Flask(__name__)
print('enetered into app')

# root for our directory and abs=working directory
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print('app')

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'rfpportal'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Florid@1'
app.config['MYSQL_DATABASE_DB'] = 'rfpportal'
app.config['MYSQL_DATABASE_HOST'] = '166.62.8.3'
app.config['MYSQL_DATABASE_PORT'] = '3306'
mysql.init_app(app)


# main page
@app.route('/')
def main():
    return render_template('main.html')
print('mainpage')


# procedure for login
@app.route('/Login', methods=['post'])
def Login():
    print('entered into login session')
    user_mail = request.form['Uemail']
    print(user_mail)
    password = request.form['password']
    print(password)

    print('validating the userdetails')
    log = mysql.connect()
    cursor = log.cursor()
    # database procedure
    print('connectd to cursor')
    cursor.execute(" SELECT useremail, userpassword FROM login WHERE\
                    useremail='%s' AND userpassword ='%s' " %
                    (user_mail, password))
    print('fetching data')
    data = cursor.fetchone()
    print(data)
    if data is None:
        return "Username or Password is wrong"
    else:
        return render_template('docment.html')
    cursor.close()
    log.close()


# uploading zip file
@app.route('/upload', methods=['POST'])
def upload():
    print('creating target')
    target = os.path.join(APP_ROOT, 'zipfiles/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print('hello file')
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        print("requested")
        destination = '/'.join([target, filename])
        print(destination)
        f.save(destination)
        return 'file uploaded successfully'


# procedure for registration
@app.route('/signup', methods=['POST'])
def signup():
    print('fetching from form')
    _name = request.form['name']
    print (_name)
    _email = request.form['email']
    print(_email)
    _company = request.form['company']
    print(_company)
    _number = request.form['phoneno']
    print(_number)
    if _name:
        con = mysql.connect()
        print('connected to db')
        cursor = con.cursor()
        print('connected to cursor')
        cursor.callproc('registerUser', (_name, _email, _company, _number))
        print('connected and stored in db')
        # password generation
        s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXTZ'
        pwdlen = 6
        user_password = ''.join(random.sample(s, pwdlen))
        print (user_password)
        # send the pswd to the email
        fromaddress = 'pmeghanagoud@gmail.com'
        toaddress = _email
        text = 'Login credentials for DNOW RFP'
        username = 'pmeghanagoud'
        password = 'tubelight@211'
        print('read the mail details')
        msg = MIMEMultipart()  # basically for attaching text or files
        msg['FROM'] = fromaddress
        msg['TO'] = toaddress
        msg['Subject'] = text
        print('from and to fields are done')
        msg.attach(MIMEText(user_password))  # extracting text message
        server = smtplib.SMTP('smtp.googlemail.com')
        server.ehlo()  # greeting server
        server.starttls()  # transport layer security mode to ssecure our mails
        server.ehlo()  # have to greet the server again
        server.login(username, password)  # login with the details
        server.sendmail(fromaddress, toaddress, msg.as_string())
        # returns the entire message flattened as a string
        server.quit()  # coming out of the server
        print('mail sent succesfully')
        cursor.callproc('loginuser', (_email, user_password))
        print('login details are stored')
        con.commit()
        cursor.close()
        con.close()
    return 'Registered succesfully, check your email'


# procedure for contact
@app.route('/contact', methods=['POST'])
def contact():
    print('fetching from contact form')
    _cname = request.form['cname']
    print(_cname)
    _cemail = request.form['cemail']
    print(_cemail)
    _cmessage = request.form['cmessage']
    print(_cmessage)
    if _cname:
        cnx = mysql.connect()
        cursor = cnx.cursor()
        print('connected to cursor')
        cursor.callproc('contact', (_cname, _cemail, _cmessage))
        print('connected and stored in db')
        cnx.commit()
        cursor.close()
        cnx.close()
    # after storing in database
    # sending an email
    fromaddress = 'pmeghanagoud@gmail.com'
    toaddress = 'meghanagoud211@gmail.com'
    text = 'user messages'
    username = 'pmeghanagoud'
    password = 'tubelight@211'
    print('read the mail details')
    msg = MIMEMultipart()  # basically for attaching text or files
    msg['FROM'] = fromaddress
    msg['TO'] = toaddress
    msg['Subject'] = text
    print('from and to fields are done')
    msg.attach(MIMEText(_cmessage))
    server = smtplib.SMTP('smtp.googlemail.com')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(fromaddress, toaddress, msg.as_string())
    server.quit()
    print('mail sent succesfully')
    return 'message sent succesfully'

if __name__ == "__main__":
    app.run(port=5000, debug=True)
    
