import smtplib, os
from email.message import EmailMessage
from flask import render_template, request, flash

def send_email(user, msg=None):
	
	login = os.environ.get('MAIL_USERNAME')
	password = os.environ.get('MAIL_PASSWORD')
	fromaddr = login
	toaddr = user.email

	email = EmailMessage()
	email['From'] = fromaddr
	email['To'] = toaddr

	if not msg:
		email['Subject'] = "authentication"
		url = f'{request.url_root}auth/?user={user.slug}&key={user.auth_key}'
		email.set_content(render_template('confirmed.html', url=url), subtype='html')
	else:
		email['Subject'] = "Good job!"
		email.set_content(render_template('post_to_email.html', post=msg), subtype='html')
	# Send the message via local SMTP server.
	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
		server.ehlo()
		server.login(login, password)
		
		### catch exception and try to repeat sending message ###
		server.send_message(email) 
		server.quit()
