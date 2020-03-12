import smtplib, os
from email.message import EmailMessage
from flask import render_template, request, flash

def send_email(user):
	
	login = os.environ.get('MAIL_USERNAME')
	password = os.environ.get('MAIL_PASSWORD')

	fromaddr = os.environ.get('MAIL_USERNAME')
	toaddr = user.email

	email = EmailMessage()
	email['Subject'] = "authentication"
	email['From'] = fromaddr
	email['To'] = toaddr

	url = f'{request.url_root}auth/?user={user.slug}&key={user.auth_key}'
	email.set_content(render_template('confirmed.html', url=url), subtype='html')
	flash('Mail sent to user {}'.format(user.username))
	# Send the message via local SMTP server.
	with smtplib.SMTP_SSL('mail.privateemail.com:465') as server:
		server.ehlo()
		server.login(login, password)
		
		### catch exception and try to repeat sending message ###
		server.send_message(email) 
		server.quit()
