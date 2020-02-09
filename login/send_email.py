import smtplib
import os
from email.message import EmailMessage
from flask import render_template

def send_email(user):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()

	################################################# 
	#                                               #
	#   Check it change how work sending message    #
	
	server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD')) 

	################################################

	fromaddr = os.environ.get('MAIL_USERNAME')
	toaddr = 'steppe.alone@gmail.com'

	email = EmailMessage()
	email['Subject'] = "authentication"
	email['From'] = fromaddr
	email['To'] = toaddr

	slug = f'key={user.auth_key}'
	email.set_content(render_template('login/confirmed.html', slug=slug), subtype='html')

	# Send the message via local SMTP server.
	with server as s:
		s.send_message(email)
